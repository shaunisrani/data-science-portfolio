from eval import evaluate


def test_retrieval_quality_gate():
    hit, mrr, _ = evaluate()
    assert hit >= 0.9 and mrr >= 0.8


def test_relevance_gate():
    from rag import REFUSAL, answer, build_index

    r = build_index()
    assert answer(r, "Who won the 2022 World Cup?") == (REFUSAL, [])
    text, sources = answer(r, "How is OEE calculated?")
    assert text != REFUSAL and sources
