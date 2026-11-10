"""FabLens — Gradio UI for semiconductor yield & manufacturing Q&A (RAG)."""
import gradio as gr

from rag import answer, build_index, pick_provider

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


def agent_chat(message, history):
    provider = pick_provider()
    if provider is None:
        return "The agent needs an LLM. Set MISTRAL_API_KEY or ANTHROPIC_API_KEY (Space settings → Secrets)."
    from agent import build_agent, run_agent

    if state.get("agent") is None:
        state["agent"] = build_agent(state["retriever"])
    text, tools_used = run_agent(state["agent"], message, provider=provider)
    return f"{text}\n\n*Tools used: {', '.join(tools_used) or 'none'}*"


AGENT_EXAMPLES = [
    "What is the Poisson yield for a 2 cm^2 die at 0.3 defects/cm^2, and how would clustering change it?",
    "How many gross dies fit on a 300 mm wafer for a 120 mm^2 die?",
    "A process has mean 10.0, std 0.4, spec 8.5 to 11.5. Is it capable?",
]


def add_files(files):
    paths = [f if isinstance(f, str) else f.name for f in (files or [])]
    state["retriever"] = build_index(paths)
    state["agent"] = None  # rebuild with new docs on next agent question
    n = len(state["retriever"].chunks)
    return f"Indexed {len(paths)} uploaded file(s). Knowledge base now has {n} chunks ({state['retriever'].mode})."


with gr.Blocks(title="FabLens") as demo:
    gr.Markdown(
        "# FabLens\nAsk about semiconductor yield, lithography, metrology, defects, and fab AI. "
        "Answers cite the source documents. Upload your own PDFs or notes to extend the knowledge base."
    )
    with gr.Tab("Ask (RAG)"):
        gr.ChatInterface(chat, examples=EXAMPLES)
    with gr.Tab("Agent (tools)"):
        gr.Markdown("The agent decides when to search the docs and when to run yield, dies-per-wafer, or Cpk calculators.")
        gr.ChatInterface(agent_chat, examples=AGENT_EXAMPLES)
    with gr.Accordion("Add documents (PDF / MD / TXT)", open=False):
        files = gr.File(file_count="multiple", file_types=[".pdf", ".md", ".txt"])
        status = gr.Markdown(f"Retrieval mode: {state['retriever'].mode}")
        gr.Button("Index files").click(add_files, files, status)

if __name__ == "__main__":
    demo.launch()
