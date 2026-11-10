"""Tools the FabLens agent can call. Pure functions are kept separate so they can be unit-tested."""
import math

from langchain_core.tools import tool


# ---------- pure functions (tested in tests/test_tools.py) ----------
def die_yield(die_area_cm2: float, defect_density_per_cm2: float, model: str = "poisson", alpha: float = 2.0) -> float:
    """Predicted die yield (0-1) from die area and defect density."""
    if die_area_cm2 <= 0 or defect_density_per_cm2 < 0:
        raise ValueError("die area must be > 0 and defect density >= 0")
    ad = die_area_cm2 * defect_density_per_cm2
    model = model.lower()
    if model == "poisson":
        return math.exp(-ad)
    if model == "murphy":
        return 1.0 if ad == 0 else ((1 - math.exp(-ad)) / ad) ** 2
    if model in {"negative_binomial", "stapper", "nb"}:
        if alpha <= 0:
            raise ValueError("alpha must be > 0")
        return (1 + ad / alpha) ** (-alpha)
    raise ValueError(f"unknown model '{model}' (use poisson, murphy, negative_binomial)")


def gross_dies_per_wafer(wafer_diameter_mm: float, die_area_mm2: float) -> int:
    """Standard approximation: pi*(d/2)^2/A - pi*d/sqrt(2A)."""
    if wafer_diameter_mm <= 0 or die_area_mm2 <= 0:
        raise ValueError("inputs must be > 0")
    d, a = wafer_diameter_mm, die_area_mm2
    return max(0, int(math.pi * (d / 2) ** 2 / a - math.pi * d / math.sqrt(2 * a)))


def cpk(mean: float, std: float, lsl: float, usl: float) -> float:
    """Process capability index."""
    if std <= 0 or usl <= lsl:
        raise ValueError("std must be > 0 and USL > LSL")
    return min(usl - mean, mean - lsl) / (3 * std)


# ---------- LangChain tools ----------
@tool
def yield_calculator(die_area_cm2: float, defect_density_per_cm2: float, model: str = "poisson", alpha: float = 2.0) -> str:
    """Compute predicted die yield. model is 'poisson', 'murphy', or 'negative_binomial' (uses clustering alpha)."""
    try:
        return f"{model} yield = {die_yield(die_area_cm2, defect_density_per_cm2, model, alpha):.1%}"
    except ValueError as e:
        return f"Error: {e}"


@tool
def dies_per_wafer(wafer_diameter_mm: float, die_area_mm2: float) -> str:
    """Estimate gross dies per wafer from wafer diameter (mm, e.g. 300) and die area (mm^2)."""
    try:
        return f"~{gross_dies_per_wafer(wafer_diameter_mm, die_area_mm2)} gross dies per wafer"
    except ValueError as e:
        return f"Error: {e}"


@tool
def cpk_calculator(mean: float, std: float, lsl: float, usl: float) -> str:
    """Compute process capability Cpk from mean, standard deviation, and lower/upper spec limits."""
    try:
        v = cpk(mean, std, lsl, usl)
        return f"Cpk = {v:.2f} ({'meets' if v >= 1.33 else 'below'} the common 1.33 target)"
    except ValueError as e:
        return f"Error: {e}"


def make_search_tool(retriever):
    @tool
    def search_docs(query: str) -> str:
        """Search the FabLens semiconductor knowledge base. Returns numbered passages with source file names."""
        if not retriever.is_relevant(query):
            return "No relevant documents in the FabLens knowledge base."
        docs = retriever.invoke(query)
        return "\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)

    return search_docs
