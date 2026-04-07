import hashlib
from typing import Dict, Any, Optional, List, Union, AsyncGenerator

from app.providers.base import ModelProvider


class Lab2EchoProvider(ModelProvider):
    @property
    def provider_id(self) -> str:
        return "lab2_echo"

    @property
    def provider_name(self) -> str:
        return "Lab2 Echo Provider"

    @property
    def description(self) -> str:
        return "契约重塑验证用Provider，演示新增Provider几乎零改动主流程"

    @property
    def icon(self) -> Optional[str]:
        return "https://raw.githubusercontent.com/github/explore/main/topics/python/python.png"

    @property
    def default_base_url(self) -> Optional[str]:
        return "mock://echo"

    @property
    def supported_model_types(self) -> List[str]:
        return ["chat", "completion", "embedding"]

    @property
    def features(self) -> List[str]:
        return ["契约一致返回", "零外部依赖", "快速验收"]

    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        return self.build_success_result(
            "Lab2 Echo Provider 连接成功",
            {
                "model": "lab2-echo-chat",
                "available_models": ["lab2-echo-chat", "lab2-echo-embed"],
                "base_url": base_url or self.default_base_url
            }
        )

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
        user_messages = [msg.get("content", "") for msg in messages if msg.get("role") == "user" and isinstance(msg.get("content", ""), str)]
        user_text = user_messages[-1] if user_messages else ""
        prev_user_text = user_messages[-2] if len(user_messages) >= 2 else ""

        answer = f"Echo: {user_text}" if user_text else "Echo: empty"
        if prev_user_text:
            answer += f" | MemoryFromPrevUser: {prev_user_text}"

        if stream:
            async def stream_generator():
                yield {
                    "id": "chatcmpl-echo",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": answer}, "finish_reason": None}]
                }
                yield {
                    "id": "chatcmpl-echo",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                }

            return stream_generator()

        return {
            "id": "chatcmpl-echo",
            "object": "chat.completion",
            "created": 0,
            "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": answer}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": max(len(user_text), 1), "completion_tokens": len(answer), "total_tokens": max(len(user_text), 1) + len(answer)}
        }

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
        content = f"Echo completion: {prompt}"
        if stream:
            async def stream_generator():
                yield {
                    "id": "cmpl-echo",
                    "object": "text_completion",
                    "created": 0,
                    "model": model,
                    "choices": [{"text": content, "index": 0, "finish_reason": "stop"}]
                }

            return stream_generator()

        return {
            "id": "cmpl-echo",
            "object": "text_completion",
            "created": 0,
            "model": model,
            "choices": [{"text": content, "index": 0, "finish_reason": "stop"}]
        }

    async def embedding(
        self,
        api_key: str,
        text: Union[str, List[str]],
        model: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        texts = text if isinstance(text, list) else [text]
        vectors = []
        for item in texts:
            digest = hashlib.sha256(item.encode("utf-8")).digest()
            vectors.append([round(b / 255, 6) for b in digest[:8]])

        return {
            "object": "list",
            "model": model,
            "data": [{"object": "embedding", "embedding": vector, "index": index} for index, vector in enumerate(vectors)],
            "embeddings": vectors
        }
