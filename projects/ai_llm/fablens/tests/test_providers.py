import rag


def test_azure_provider_selected(monkeypatch):
    for k in ["MISTRAL_API_KEY", "ANTHROPIC_API_KEY"]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "x")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("OPENAI_API_VERSION", "2024-10-21")
    assert rag.pick_provider() == "azure"
    assert type(rag.get_llm("azure")).__name__ == "AzureChatOpenAI"
