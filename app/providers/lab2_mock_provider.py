import hashlib
import time
from typing import Dict, Any, Optional, List, Union, AsyncGenerator

from app.providers.base import ModelProvider


class Lab2MockProvider(ModelProvider):
    @property
    def provider_id(self) -> str:
        return "lab2_mock"

    @property
    def provider_name(self) -> str:
        return "Lab2 Mock Provider"

    @property
    def description(self) -> str:
        return "实验二用本地Mock Provider，无需外部网络，可用于OOP扩展链路验证"

    @property
    def icon(self) -> Optional[str]:
        return "https://raw.githubusercontent.com/github/explore/main/topics/python/python.png"

    @property
    def default_base_url(self) -> Optional[str]:
        return "mock://lab2"

    @property
    def supported_model_types(self) -> List[str]:
        return ["chat", "completion", "embedding"]

    @property
    def features(self) -> List[str]:
        return ["无外部依赖", "可流式输出", "可重复测试"]

    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        response_time = round((time.time() - start_time) * 1000)
        return {
            "status": "success",
            "message": "Lab2 Mock Provider 连接成功",
            "response": {
                "model": "lab2-mock-chat",
                "available_models": ["lab2-mock-chat", "lab2-mock-embed"],
                "base_url": base_url or self.default_base_url,
                "responseTime": f"{response_time}ms"
            }
        }

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
        user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_text = msg.get("content", "")
                break

        answer = f"Lab2Mock已收到：{user_text}" if user_text else "Lab2Mock已收到请求。"

        if stream:
            async def stream_generator():
                chunk_size = 8
                for i in range(0, len(answer), chunk_size):
                    part = answer[i:i + chunk_size]
                    yield {
                        "id": f"chatcmpl-lab2-{int(time.time() * 1000)}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": part},
                                "finish_reason": None
                            }
                        ]
                    }
                yield {
                    "id": f"chatcmpl-lab2-{int(time.time() * 1000)}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }
                    ]
                }

            return stream_generator()

        return {
            "id": f"chatcmpl-lab2-{int(time.time() * 1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": max(len(user_text), 1),
                "completion_tokens": len(answer),
                "total_tokens": max(len(user_text), 1) + len(answer)
            }
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
        content = f"Lab2Mock completion: {prompt}"
        if stream:
            async def stream_generator():
                yield {
                    "id": f"cmpl-lab2-{int(time.time() * 1000)}",
                    "object": "text_completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{"text": content, "index": 0, "finish_reason": "stop"}]
                }

            return stream_generator()

        return {
            "id": f"cmpl-lab2-{int(time.time() * 1000)}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{"text": content, "index": 0, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": len(prompt),
                "completion_tokens": len(content),
                "total_tokens": len(prompt) + len(content)
            }
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
            vec = [round(b / 255, 6) for b in digest[:16]]
            vectors.append(vec)

        return {
            "object": "list",
            "data": [{"object": "embedding", "embedding": v, "index": i} for i, v in enumerate(vectors)],
            "model": model,
            "embeddings": vectors
        }
