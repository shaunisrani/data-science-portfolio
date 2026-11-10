"""FabLens agent built with Microsoft Semantic Kernel, running on Azure OpenAI (Azure AI Foundry).

Same tools as the LangChain agent (agent.py), exposed as a Semantic Kernel plugin, so the two frameworks
can be compared on the same task with the AI App Scorecard.

Env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT (e.g. gpt-4o-mini), AZURE_OPENAI_API_VERSION (optional)
Run: python sk_agent.py "What is the Poisson yield for a 2 cm^2 die at 0.3 defects/cm^2?"
"""
import asyncio
import os
import sys
import time
from typing import Annotated

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments, kernel_function

from query_log import log_query
from tools import cpk, die_yield, gross_dies_per_wafer

INSTRUCTIONS = (
    "You are FabLens, a semiconductor yield engineering assistant. Use search_docs for concepts and the "
    "calculator functions for any numbers; never do the math yourself. Cite sources in [brackets]. "
    "If the tools don't give you the answer, say you don't know."
)


class FabLensPlugin:
    """Semantic Kernel plugin: each @kernel_function is a tool the model can call."""

    def __init__(self, retriever):
        self.retriever = retriever

    @kernel_function(description="Search the FabLens semiconductor knowledge base. Returns passages with source names.")
    def search_docs(self, query: Annotated[str, "what to look up"]) -> str:
        if not self.retriever.is_relevant(query):
            return "No relevant documents in the FabLens knowledge base."
        return "\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in self.retriever.invoke(query))

    @kernel_function(description="Predicted die yield. model: poisson, murphy, or negative_binomial (uses alpha).")
    def yield_calculator(self, die_area_cm2: float, defect_density_per_cm2: float,
                         model: str = "poisson", alpha: float = 2.0) -> str:
        try:
            return f"{model} yield = {die_yield(die_area_cm2, defect_density_per_cm2, model, alpha):.1%}"
        except ValueError as e:
            return f"Error: {e}"

    @kernel_function(description="Gross dies per wafer from wafer diameter (mm) and die area (mm^2).")
    def dies_per_wafer(self, wafer_diameter_mm: float, die_area_mm2: float) -> str:
        try:
            return f"~{gross_dies_per_wafer(wafer_diameter_mm, die_area_mm2)} gross dies per wafer"
        except ValueError as e:
            return f"Error: {e}"

    @kernel_function(description="Process capability Cpk from mean, std, lower and upper spec limits.")
    def cpk_calculator(self, mean: float, std: float, lsl: float, usl: float) -> str:
        try:
            v = cpk(mean, std, lsl, usl)
            return f"Cpk = {v:.2f} ({'meets' if v >= 1.33 else 'below'} the common 1.33 target)"
        except ValueError as e:
            return f"Error: {e}"


def build_kernel(retriever):
    kernel = Kernel()
    kernel.add_plugin(FabLensPlugin(retriever), plugin_name="fablens")
    return kernel


def build_sk_agent(retriever):
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings

    service = AzureChatCompletion(
        deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    )
    settings = AzureChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())
    kernel = build_kernel(retriever)
    kernel.add_service(service)
    return ChatCompletionAgent(kernel=kernel, name="FabLens", instructions=INSTRUCTIONS,
                               arguments=KernelArguments(settings=settings))


async def ask(agent, question):
    t0 = time.time()
    response = await agent.get_response(messages=question)
    text = str(response.content)
    log_query(mode="sk-agent", question=question, provider="azure-openai",
              model=os.getenv("AZURE_OPENAI_DEPLOYMENT"), answer_chars=len(text), latency_s=round(time.time() - t0, 3))
    return text


if __name__ == "__main__":
    from rag import build_index

    q = " ".join(sys.argv[1:]) or "What is the Poisson yield for a 2 cm^2 die at 0.3 defects/cm^2?"
    print(asyncio.run(ask(build_sk_agent(build_index()), q)))
