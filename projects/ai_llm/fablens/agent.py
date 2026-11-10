"""FabLens agent: a tool-calling LLM that decides when to search docs vs. run calculations."""
import time

from langchain.agents import create_agent

from query_log import log_query
from rag import get_llm, pick_provider
from tools import cpk_calculator, dies_per_wafer, make_search_tool, yield_calculator

AGENT_PROMPT = (
    "You are FabLens, a semiconductor yield engineering assistant. "
    "Use search_docs for concepts and definitions, and the calculator tools for any numbers. "
    "Never do yield, dies-per-wafer, or Cpk math in your head. "
    "Cite document sources in [brackets]. If the tools don't give you the answer, say you don't know."
)


def build_agent(retriever, llm=None):
    llm = llm or get_llm(pick_provider())
    tools = [make_search_tool(retriever), yield_calculator, dies_per_wafer, cpk_calculator]
    return create_agent(llm, tools=tools, system_prompt=AGENT_PROMPT)


def run_agent(agent, question, provider="unknown"):
    t0 = time.time()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    msgs = result["messages"]
    tools_used = [tc["name"] for m in msgs for tc in (getattr(m, "tool_calls", None) or [])]
    text = msgs[-1].content if isinstance(msgs[-1].content, str) else str(msgs[-1].content)
    log_query(mode="agent", question=question, provider=provider, tools_used=tools_used,
              answer_chars=len(text), latency_s=time.time() - t0)
    return text, tools_used
