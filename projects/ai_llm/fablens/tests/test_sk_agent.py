"""Semantic Kernel plugin tests (offline: functions are invoked through the kernel, no LLM call)."""
import asyncio

from rag import build_index
from sk_agent import build_kernel, build_sk_agent


def call(kernel, fn, **kwargs):
    return str(asyncio.run(kernel.invoke(plugin_name="fablens", function_name=fn, **kwargs)))


def test_plugin_registers_all_tools():
    k = build_kernel(build_index())
    names = {f.name for f in k.get_plugin("fablens").functions.values()}
    assert names == {"search_docs", "yield_calculator", "dies_per_wafer", "cpk_calculator"}


def test_plugin_functions_run_through_kernel():
    k = build_kernel(build_index())
    assert "54.9%" in call(k, "yield_calculator", die_area_cm2=2.0, defect_density_per_cm2=0.3)
    assert "1.25" in call(k, "cpk_calculator", mean=10.0, std=0.4, lsl=8.5, usl=11.5)
    assert "02_lithography_euv.md" in call(k, "search_docs", query="EUV wavelength tin plasma")
    assert "No relevant" in call(k, "search_docs", query="banana bread recipe")


def test_agent_builds_for_azure(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    agent = build_sk_agent(build_index())
    assert agent.name == "FabLens"
