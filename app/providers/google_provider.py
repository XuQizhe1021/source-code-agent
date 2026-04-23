import asyncio
import time
from typing import Dict, Any, Optional, List, Union, AsyncGenerator

from google.generativeai import configure, GenerativeModel
import google.generativeai as genai

from app.providers.base import BaseHTTPProvider


class GoogleProvider(BaseHTTPProvider):
    """
    Google模型提供商实现
    """
    
    @property
    def provider_id(self) -> str:
        return "google"
    
    @property
    def provider_name(self) -> str:
        return "Google"
    
    @property
    def description(self) -> str:
        return "Google提供的AI模型，包括Gemini系列"
    
    @property
    def icon(self) -> Optional[str]:
        return "https://g.autoimg.cn/@img/car2/cardfs/series/g28/M07/14/D1/300x300_autohomecar__ChxkmmTCOmCABVVvAADqUrllBts727.png?format=webp"
    @property
    def default_base_url(self) -> Optional[str]:
        return None  # Google API不需要自定义base_url
    
    @property
    def supported_model_types(self) -> List[str]:
        return ["chat", "embedding"]
    
    @property
    def features(self) -> List[str]:
        return ["流式响应", "函数调用", "多模态"]
    
    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """测试与Google AI API的连接"""
        try:
            start_time = time.time()
            
            # 配置Google API
            configure(api_key=api_key)
            
            # 获取模型列表
            models = genai.list_models()
            available_models = [model.name for model in models if "generateContent" in model.supported_generation_methods]
            
            response_time = round((time.time() - start_time) * 1000)
            
            return {
                "status": "success",
                "message": "连接成功",
                "response": {
                    "model": "Google AI API",
                    "available_models": available_models[:5],
                    "responseTime": f"{response_time}ms"
                }
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"连接失败: {str(e)}"
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
        """发送聊天完成请求到Google AI API，支持流式输出"""
        configure(api_key=api_key)

        google_messages = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "assistant":
                role = "model"
            google_messages.append({"role": role, "parts": [content]})

        generation_config = {"temperature": temperature}
        if max_tokens is not None:
            generation_config["max_output_tokens"] = max_tokens
        gemini_model = GenerativeModel(model, generation_config=generation_config)

        if stream:
            async def stream_generator():
                start_time = time.time()
                try:
                    chat = gemini_model.start_chat(history=google_messages[:-1])
                    last_message = google_messages[-1]["parts"][0] if google_messages else ""
                    response_stream = chat.send_message(last_message, stream=True)
                    for chunk in response_stream:
                        if hasattr(chunk, "text") and chunk.text:
                            current_time = time.time()
                            response_time = round((current_time - start_time) * 1000)
                            yield {
                                "choices": [{"delta": {"content": chunk.text, "role": "assistant"}}],
                                "response_time_ms": response_time
                            }
                except Exception as e:
                    yield self._build_error_result(f"流式响应失败: {str(e)}", code="provider_stream_error")

            return stream_generator()

        async def _operation() -> Dict[str, Any]:
            chat = gemini_model.start_chat(history=google_messages[:-1])
            last_message = google_messages[-1]["parts"][0] if google_messages else ""
            response = chat.send_message(last_message)
            return {
                "choices": [{"message": {"content": response.text, "role": "assistant"}}],
                "model": model,
            }

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
        """发送文本完成请求到Google AI API，实际上是封装聊天API"""
        # 将文本提示转换为聊天消息格式
        messages = [{"role": "user", "content": prompt}]
        
        # 调用聊天API
        return await self.chat_completion(
            api_key=api_key,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            stream=stream,
            **kwargs
        )
    
    async def embedding(
        self,
        api_key: str,
        text: Union[str, List[str]],
        model: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取文本嵌入向量从Google AI API"""
        configure(api_key=api_key)

        async def _operation() -> Dict[str, Any]:
            texts = [text] if isinstance(text, str) else text
            embeddings = []
            for t in texts:
                result = genai.embed_content(
                    model=model,
                    content=t,
                    task_type="retrieval_document",
                    **kwargs
                )
                embeddings.append({
                    "embedding": result["embedding"],
                    "index": len(embeddings)
                })
            return {
                "data": embeddings,
                "model": model,
            }

        return await self._execute_timed_dict_call(_operation, error_prefix="嵌入请求失败")
