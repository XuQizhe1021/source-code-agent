import json
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import httpx

from app.providers.base import BaseHTTPProvider, RequestBuilder, StreamResponseParser


class CustomProvider(BaseHTTPProvider):
    """
    自定义模型提供商，允许用户连接任何与OpenAI兼容的API
    """
    
    @property
    def provider_id(self) -> str:
        return "custom"
    
    @property
    def provider_name(self) -> str:
        return "自定义API"
    
    @property
    def description(self) -> str:
        return "连接任何兼容OpenAI的API服务，或自托管的模型服务"
    
    @property
    def icon(self) -> Optional[str]:
        return "https://ollama.com/public/ollama.png"
    
    @property
    def default_base_url(self) -> Optional[str]:
        return None
    
    @property
    def supported_model_types(self) -> List[str]:
        return ["chat", "completion", "embedding"]
    
    @property
    def features(self) -> List[str]:
        return ["自定义终端", "灵活配置", "本地部署", "流式输出"]
    
    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """测试与自定义API的连接"""
        if not base_url:
            return self._build_connection_failed_result("自定义API必须提供基础URL", code="missing_base_url")

        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)

        async def _operation() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{normalized_base_url}/models",
                    headers=RequestBuilder.build_headers(api_key)
                )
                if response.status_code != 200:
                    return self._build_connection_failed_result(
                        f"API返回错误: {response.status_code} - {response.text}"
                    )
                return self.build_success_result(
                    "连接成功",
                    {"model": "自定义API"}
                )

        result = await self._execute_timed_dict_call(_operation, error_prefix="连接失败", error_code="connection_failed")
        if result.get("status") == "error":
            return self._build_connection_failed_result(result.get("message", "连接失败"))
        if result.get("status") == "success":
            response = result.get("response", {})
            if isinstance(response, dict):
                response_time = result.get("response_time_ms", -1)
                response["responseTime"] = f"{response_time}ms" if isinstance(response_time, int) else "-1ms"
            return result
        return result
    
    async def chat_completion(
        self, 
        api_key: str, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        base_url: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """发送聊天完成请求到自定义API，支持流式输出"""
        if not base_url:
            return self._build_error_result("自定义API必须提供基础URL", code="missing_base_url")

        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        data = RequestBuilder.build_payload(
            required={
                "model": model,
                "messages": messages,
                "temperature": temperature,
            },
            max_tokens=max_tokens,
            stream=stream,
            passthrough_kwargs=kwargs
        )
        headers = RequestBuilder.build_headers(api_key)

        if stream:
            async def _stream_factory() -> AsyncGenerator[Dict[str, Any], None]:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream(
                        "POST",
                        f"{normalized_base_url}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=None
                    ) as response:
                        if response.status_code != 200:
                            yield self._build_error_result(f"API返回错误: {response.status_code}", code="http_error")
                            return
                        buffer = ""
                        async for chunk in response.aiter_text():
                            buffer += chunk
                            payloads, buffer = StreamResponseParser.parse_sse_buffer(buffer)
                            for payload in payloads:
                                if payload == "[DONE]":
                                    continue
                                try:
                                    yield json.loads(payload)
                                except json.JSONDecodeError:
                                    yield self._build_error_result(f"无法解析JSON: {payload}", code="invalid_stream_json")

            return self._wrap_stream_generator(_stream_factory, error_prefix="流式响应失败")

        async def _operation() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{normalized_base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code != 200:
                    return self._build_error_result(
                        f"API返回错误: {response.status_code} - {response.text}",
                        code="http_error"
                    )
                result = response.json()
                return result

        return await self._execute_timed_dict_call(_operation, error_prefix="聊天完成请求失败")
    
    async def text_completion(
        self,
        api_key: str,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        base_url: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """发送文本完成请求到自定义API，支持流式输出"""
        if not base_url:
            return self._build_error_result("自定义API必须提供基础URL", code="missing_base_url")

        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        data = RequestBuilder.build_payload(
            required={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
            },
            max_tokens=max_tokens,
            stream=stream,
            passthrough_kwargs=kwargs
        )
        headers = RequestBuilder.build_headers(api_key)

        if stream:
            async def _stream_factory() -> AsyncGenerator[Dict[str, Any], None]:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream(
                        "POST",
                        f"{normalized_base_url}/completions",
                        headers=headers,
                        json=data,
                        timeout=None
                    ) as response:
                        if response.status_code != 200:
                            yield self._build_error_result(f"API返回错误: {response.status_code}", code="http_error")
                            return
                        buffer = ""
                        async for chunk in response.aiter_text():
                            buffer += chunk
                            payloads, buffer = StreamResponseParser.parse_sse_buffer(buffer)
                            for payload in payloads:
                                if payload == "[DONE]":
                                    continue
                                try:
                                    yield json.loads(payload)
                                except json.JSONDecodeError:
                                    yield self._build_error_result(f"无法解析JSON: {payload}", code="invalid_stream_json")

            return self._wrap_stream_generator(_stream_factory, error_prefix="流式响应失败")

        async def _operation() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{normalized_base_url}/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code != 200:
                    return self._build_error_result(
                        f"API返回错误: {response.status_code} - {response.text}",
                        code="http_error"
                    )
                result = response.json()
                return result

        return await self._execute_timed_dict_call(_operation, error_prefix="文本完成请求失败")
    
    async def embedding(
        self,
        api_key: str,
        text: Union[str, List[str]],
        model: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取文本嵌入向量从自定义API"""
        if not base_url:
            return self._build_error_result("自定义API必须提供基础URL", code="missing_base_url")

        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        data = RequestBuilder.build_payload(
            required={
                "model": model,
                "input": text
            },
            passthrough_kwargs=kwargs
        )

        async def _operation() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{normalized_base_url}/embeddings",
                    headers=RequestBuilder.build_headers(api_key),
                    json=data
                )
                if response.status_code != 200:
                    return self._build_error_result(
                        f"API返回错误: {response.status_code} - {response.text}",
                        code="http_error"
                    )
                return response.json()

        return await self._execute_timed_dict_call(_operation, error_prefix="嵌入请求失败")
