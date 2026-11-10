"""Agent wiring test with a scripted fake LLM (no API key needed)."""
import json
import os

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import build_agent, run_agent
from rag import build_index


class ScriptedToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def test_agent_calls_yield_tool_and_logs():
    script = iter([
        AIMessage(content="", tool_calls=[{"name": "yield_calculator", "id": "1",
                  "args": {"die_area_cm2": 1.0, "defect_density_per_cm2": 0.1, "model": "poisson"}}]),
        AIMessage(content="Poisson yield is about 90.5%."),
    ])
    agent = build_agent(build_index(), llm=ScriptedToolModel(messages=script))
    text, tools_used = run_agent(agent, "Yield for a 1 cm^2 die at D0=0.1?", provider="fake")
    assert tools_used == ["yield_calculator"]
    assert "90.5%" in text
    last = json.loads(open(os.environ["FABLENS_LOG"]).read().strip().splitlines()[-1])
    assert last["mode"] == "agent" and last["tools_used"] == ["yield_calculator"]
