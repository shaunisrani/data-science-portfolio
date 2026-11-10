"""FabLens RAG core: load docs, chunk, hybrid retrieval (BM25 + dense FAISS), answer with Claude or Mistral."""
import os
import re
import time
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent / "docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()  # "anthropic", "mistral", "azure", or "" = auto
DEFAULT_MODELS = {"anthropic": "claude-haiku-4-5", "mistral": "mistral-small-latest",
                  "azure": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")}

SYSTEM_PROMPT = (
    "You are FabLens, an assistant for semiconductor manufacturing and yield engineering. "
    "Answer ONLY from the context below. Cite sources as [1], [2] matching the numbered context. "
    "If the context does not contain the answer, say you don't know. Be concise."
)


def load_documents(paths):
    docs = []
    for p in map(Path, paths):
        if p.suffix.lower() == ".pdf":
            docs += PyPDFLoader(str(p)).load()
        elif p.suffix.lower() in {".md", ".txt"}:
            docs += TextLoader(str(p), encoding="utf-8").load()
    for d in docs:
        d.metadata["source"] = Path(d.metadata.get("source", "unknown")).name
    return docs


def split(docs, chunk_size=600, overlap=100):
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap).split_documents(docs)


STOP = set(("a an the is are was what how why when where who does do did of to in on for and or with by from as at it its "
             "which that this be can i me my you your give tell explain please many much").split())
MIN_COVERAGE = 0.5  # share of query terms that must appear in the knowledge base, else refuse
REFUSAL = "I don't know: that isn't covered by the FabLens knowledge base."


def tokenize(text):
    """Lowercase, strip punctuation, drop stopwords, light plural stemming (BM25 preprocessing)."""
    return [w.rstrip("s") if len(w) > 3 else w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


class HybridRetriever:
    """Combines BM25 (keyword) and FAISS (semantic) with reciprocal rank fusion.
    Falls back to BM25 only if the embedding model can't load."""

    def __init__(self, chunks, k=4):
        self.k = k
        self.chunks = chunks
        self.bm25 = BM25Retriever.from_documents(chunks, preprocess_func=tokenize)
        self.bm25.k = k * 2
        self.dense = None
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings

            emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
            self.dense = FAISS.from_documents(chunks, emb).as_retriever(search_kwargs={"k": k * 2})
        except Exception as e:  # e.g., no network for model download
            print(f"[FabLens] Dense retrieval unavailable ({type(e).__name__}); using BM25 only.")

    def coverage(self, query):
        """Share of the query's content words that exist anywhere in the knowledge base (relevance gate)."""
        toks = tokenize(query)
        if not hasattr(self, "_vocab"):
            self._vocab = {t for d in self.chunks for t in tokenize(d.page_content)}
        return sum(t in self._vocab for t in toks) / len(toks) if toks else 0.0

    def is_relevant(self, query):
        return self.coverage(query) >= MIN_COVERAGE

    @property
    def mode(self):
        return "hybrid (BM25 + FAISS)" if self.dense else "BM25"

    def invoke(self, query):
        lists = [self.bm25.invoke(query)]
        if self.dense:
            lists.append(self.dense.invoke(query))
        scores, by_key = {}, {}
        for ranked in lists:
            for rank, d in enumerate(ranked):
                key = (d.metadata.get("source"), d.page_content[:80])
                by_key[key] = d
                scores[key] = scores.get(key, 0) + 1 / (60 + rank)  # RRF
        top = sorted(scores, key=scores.get, reverse=True)[: self.k]
        return [by_key[k] for k in top]


def build_index(extra_paths=()):
    paths = sorted(DOCS_DIR.glob("*.md")) + list(extra_paths)
    return HybridRetriever(split(load_documents(paths)))


def format_context(docs):
    return "\n\n".join(f"[{i}] ({d.metadata['source']})\n{d.page_content}" for i, d in enumerate(docs, 1))


def pick_provider():
    """Choose the LLM provider: explicit LLM_PROVIDER, else whichever API key is set."""
    if LLM_PROVIDER in DEFAULT_MODELS:
        return LLM_PROVIDER
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        return "azure"
    if os.getenv("MISTRAL_API_KEY"):
        return "mistral"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def get_llm(provider):
    model = os.getenv("LLM_MODEL", DEFAULT_MODELS[provider])
    if provider == "azure":  # Azure OpenAI deployment in Azure AI Foundry
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(azure_deployment=model, api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                               temperature=0, max_tokens=600)
    if provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(model=model, temperature=0, max_tokens=600)
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=model, temperature=0, max_tokens=600)


def answer(retriever, question):
    t0 = time.time()
    if not retriever.is_relevant(question):
        from query_log import log_query

        log_query(mode="rag", question=question, provider="gate", refused=True, sources=[],
                  latency_s=round(time.time() - t0, 3))
        return REFUSAL, []
    docs = retriever.invoke(question)
    context = format_context(docs)
    sources = sorted({d.metadata["source"] for d in docs})
    provider = pick_provider()
    if provider is None:
        # Extractive fallback: works with no API key
        text = "**No LLM API key set — showing the most relevant passages:**\n\n" + context
    else:
        llm = get_llm(provider)
        msg = llm.invoke([("system", SYSTEM_PROMPT + "\n\nContext:\n" + context), ("human", question)])
        text = msg.content
    from query_log import log_query

    log_query(mode="rag", question=question, provider=provider or "extractive",
              model=os.getenv("LLM_MODEL", DEFAULT_MODELS.get(provider, "none")),
              retrieval=retriever.mode, sources=sources, answer_chars=len(text), latency_s=round(time.time() - t0, 3))
    return text, sources
