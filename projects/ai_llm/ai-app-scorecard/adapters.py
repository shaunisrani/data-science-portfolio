"""Adapters connect any AI app to the scorecard. Each one implements ask(question) -> {"answer", "sources"}.
To add a team's app, write a small class like these or expose it over HTTP and use HttpAdapter."""
import json
import sys
import urllib.request
from pathlib import Path

FABLENS_DIR = Path(__file__).resolve().parents[1] / "fablens"


class FabLensRAGAdapter:
    categories = {"answerable", "unanswerable"}  # plain RAG has no calculators

    def __init__(self):
        sys.path.insert(0, str(FABLENS_DIR))
        from rag import answer, build_index

        self._answer, self.retriever = answer, build_index()

    def ask(self, question):
        text, sources = self._answer(self.retriever, question)
        return {"answer": text, "sources": sources}


class FabLensAgentAdapter:
    categories = None  # all categories, including calculations

    def __init__(self):
        sys.path.insert(0, str(FABLENS_DIR))
        from agent import build_agent, run_agent
        from rag import build_index, pick_provider

        if pick_provider() is None:
            raise SystemExit("fablens-agent needs MISTRAL_API_KEY or ANTHROPIC_API_KEY")
        self.provider = pick_provider()
        self.retriever = build_index()
        self.agent, self._run = build_agent(self.retriever), run_agent

    def ask(self, question):
        text, _ = self._run(self.agent, question, provider=self.provider)
        sources = [s for s in {d.metadata["source"] for d in self.retriever.invoke(question)} if s in text]
        return {"answer": text, "sources": sources}


class HttpAdapter:
    """Any app with an endpoint: POST {"question": "..."} → {"answer": "...", "sources": [...]}."""
    categories = None

    def __init__(self, url):
        if not url:
            raise SystemExit("--url is required for --app http")
        self.url = url

    def ask(self, question):
        req = urllib.request.Request(self.url, data=json.dumps({"question": question}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return {"answer": data.get("answer", ""), "sources": data.get("sources", [])}


def get_adapter(name, url=None):
    if name == "fablens-rag":
        return FabLensRAGAdapter()
    if name == "fablens-agent":
        return FabLensAgentAdapter()
    if name == "http":
        return HttpAdapter(url)
    raise SystemExit(f"unknown app '{name}'")
