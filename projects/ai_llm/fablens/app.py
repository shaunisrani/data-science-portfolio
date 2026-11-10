"""FabLens — Gradio UI for semiconductor yield & manufacturing Q&A (RAG)."""
import gradio as gr

from rag import answer, build_index

state = {"retriever": build_index()}

EXAMPLES = [
    "How does the negative binomial yield model differ from Poisson?",
    "Why does EUV use mirrors instead of lenses?",
    "What wafer map pattern points to a CMP problem?",
    "How is Cpk calculated?",
    "What is virtual metrology?",
]


def chat(message, history):
    text, sources = answer(state["retriever"], message)
    return f"{text}\n\n*Sources: {', '.join(sources)}*"


def add_files(files):
    paths = [f if isinstance(f, str) else f.name for f in (files or [])]
    state["retriever"] = build_index(paths)
    n = len(state["retriever"].chunks)
    return f"Indexed {len(paths)} uploaded file(s). Knowledge base now has {n} chunks ({state['retriever'].mode})."


with gr.Blocks(title="FabLens") as demo:
    gr.Markdown(
        "# FabLens\nAsk about semiconductor yield, lithography, metrology, defects, and fab AI. "
        "Answers cite the source documents. Upload your own PDFs or notes to extend the knowledge base."
    )
    gr.ChatInterface(chat, examples=EXAMPLES)
    with gr.Accordion("Add documents (PDF / MD / TXT)", open=False):
        files = gr.File(file_count="multiple", file_types=[".pdf", ".md", ".txt"])
        status = gr.Markdown(f"Retrieval mode: {state['retriever'].mode}")
        gr.Button("Index files").click(add_files, files, status)

if __name__ == "__main__":
    demo.launch()
