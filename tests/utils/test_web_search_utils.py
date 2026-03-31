import pytest
from fastapi import HTTPException

import app.utils.web_search as web_search


class DummyTavilyClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query):
        return {"results": [{"title": f"title-{query}", "content": "c", "url": "u"}]}


class DummyTavilyClientError:
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query):
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_search_happy_path_with_injected_client():
    client = web_search.WebSearchClient(api_key="k", tavily_client_factory=DummyTavilyClient)
    result = await client.search("abc")
    assert result["results"][0]["title"] == "title-abc"


@pytest.mark.asyncio
async def test_search_exception_path_returns_fallback():
    client = web_search.WebSearchClient(api_key="k", tavily_client_factory=DummyTavilyClientError)
    result = await client.search("abc")
    assert result["success"] is False
    assert "boom" in result["error"]
    assert result["results"] == []


def test_format_search_results_with_empty_and_non_empty_results():
    client = web_search.WebSearchClient(api_key="k", tavily_client_factory=DummyTavilyClient)
    assert client.format_search_results({"results": []}) == "未找到相关网络搜索结果。"

    text = client.format_search_results(
        {"results": [{"title": "t1", "content": "c1", "url": "u1"}]}
    )
    assert "[1] t1" in text
    assert "内容: c1" in text
    assert "来源: u1" in text


def test_get_web_search_client_supports_injected_factory_and_singleton(monkeypatch):
    web_search.web_search_client = None

    class DummyClient:
        pass

    created = web_search.get_web_search_client(client_factory=DummyClient)
    assert isinstance(created, DummyClient)
    assert web_search.get_web_search_client() is created
    web_search.web_search_client = None


def test_get_web_search_client_raises_http_exception_on_invalid_config():
    web_search.web_search_client = None

    def bad_factory():
        raise ValueError("missing key")

    with pytest.raises(HTTPException) as exc:
        web_search.get_web_search_client(client_factory=bad_factory)

    assert exc.value.status_code == 500
    assert "missing key" in exc.value.detail
    web_search.web_search_client = None
