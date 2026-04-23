import asyncio
import json
import time
import os
import base64
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import aiohttp
from aiohttp.client_exceptions import ClientError

from app.providers.base import BaseHTTPProvider, RequestBuilder, StreamResponseParser


class OllamaProvider(BaseHTTPProvider):
    """
    Ollama模型提供商实现
    提供对本地或远程Ollama服务的访问
    """
    
    @property
    def provider_id(self) -> str:
        return "ollama"
    
    @property
    def provider_name(self) -> str:
        return "Ollama"
    
    @property
    def description(self) -> str:
        return "Ollama提供的本地或远程运行的开源大语言模型，支持Llama、Mistral等多种模型"
    
    @property
    def icon(self) -> Optional[str]:
        return "https://ollama.com/public/ollama.png"
    
    @property
    def default_base_url(self) -> Optional[str]:
        return "http://localhost:11434"
    
    @property
    def supported_model_types(self) -> List[str]:
        return ["chat", "completion", "embedding"]
    
    @property
    def features(self) -> List[str]:
        return ["本地模型", "流式响应", "自定义模型", "图片识别"]
    
    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """测试与Ollama API的连接"""
        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)

        async def _operation() -> Dict[str, Any]:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{normalized_base_url}/api/tags") as response:
                    if response.status != 200:
                        return self._build_connection_failed_result(f"连接失败: HTTP {response.status}")
                    data = await response.json()

            models = []
            if "models" in data:
                models = [model["name"] for model in data["models"][:5]]
            return self.build_success_result(
                "连接成功",
                {
                    "model": "Ollama API",
                    "available_models": models,
                }
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
        """发送聊天完成请求到Ollama API，支持流式输出"""
        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        
        # 处理系统消息和用户消息
        formatted_messages = []
        for msg in messages:
            if "role" in msg and "content" in msg:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 设置请求参数
        params = RequestBuilder.build_payload(
            required={
                "model": model,
                "messages": formatted_messages,
            },
            stream=stream,
            passthrough_kwargs={},
        )
        params["options"] = {"temperature": temperature}
        
        # 处理max_tokens参数
        if max_tokens is not None:
            params["options"]["num_predict"] = max_tokens
        
        # 添加其他参数到options
        for key, value in kwargs.items():
            if key not in ["model", "messages", "stream", "options"]:
                params["options"][key] = value
        
        if stream:
            async def _stream_factory() -> AsyncGenerator[Dict[str, Any], None]:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{normalized_base_url}/api/chat", json=params) as response:
                        if response.status != 200:
                            yield self._build_error_result(f"请求失败: HTTP {response.status}", code="http_error")
                            return
                        buffer = ""
                        async for line in response.content:
                            if not line:
                                continue
                            buffer += line.decode("utf-8")
                            json_lines, buffer = StreamResponseParser.parse_json_line_buffer(buffer)
                            for line_text in json_lines:
                                try:
                                    chunk = json.loads(line_text)
                                    yield {
                                        "id": f"chatcmpl-{chunk.get('created_at', 'ollama')}",
                                        "object": "chat.completion.chunk",
                                        "created": 0,
                                        "model": model,
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {
                                                    "role": "assistant",
                                                    "content": chunk.get("message", {}).get("content", "")
                                                },
                                                "finish_reason": "stop" if chunk.get("done", False) else None
                                            }
                                        ],
                                    }
                                    if chunk.get("done", False):
                                        return
                                except json.JSONDecodeError:
                                    yield self._build_error_result(f"无法解析JSON: {line_text}", code="invalid_stream_json")

            return self._wrap_stream_generator(_stream_factory, error_prefix="流式响应失败")

        async def _operation() -> Dict[str, Any]:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{normalized_base_url}/api/chat", json=params) as response:
                    if response.status != 200:
                        return self._build_error_result(f"聊天完成请求失败: HTTP {response.status}", code="http_error")
                    data = await response.json()

            return {
                "id": f"chatcmpl-{time.time()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": data.get("message", {}).get("content", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": -1,  # Ollama不提供token统计
                    "completion_tokens": -1,
                    "total_tokens": -1
                }
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
        """发送文本完成请求到Ollama API，支持流式输出"""
        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        
        # 设置请求参数
        params = RequestBuilder.build_payload(
            required={
                "model": model,
                "prompt": prompt,
            },
            stream=stream,
            passthrough_kwargs={},
        )
        params["options"] = {"temperature": temperature}
        
        # 处理max_tokens参数
        if max_tokens is not None:
            params["options"]["num_predict"] = max_tokens
        
        # 添加其他参数到options
        for key, value in kwargs.items():
            if key not in ["model", "prompt", "stream", "options"]:
                params["options"][key] = value
        
        if stream:
            async def _stream_factory() -> AsyncGenerator[Dict[str, Any], None]:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{normalized_base_url}/api/generate", json=params) as response:
                        if response.status != 200:
                            yield self._build_error_result(f"请求失败: HTTP {response.status}", code="http_error")
                            return
                        buffer = ""
                        async for line in response.content:
                            if not line:
                                continue
                            buffer += line.decode("utf-8")
                            json_lines, buffer = StreamResponseParser.parse_json_line_buffer(buffer)
                            for line_text in json_lines:
                                try:
                                    chunk = json.loads(line_text)
                                    yield {
                                        "id": f"cmpl-{chunk.get('created_at', 'ollama')}",
                                        "object": "text_completion.chunk",
                                        "created": 0,
                                        "model": model,
                                        "choices": [
                                            {
                                                "text": chunk.get("response", ""),
                                                "index": 0,
                                                "finish_reason": "stop" if chunk.get("done", False) else None
                                            }
                                        ],
                                    }
                                    if chunk.get("done", False):
                                        return
                                except json.JSONDecodeError:
                                    yield self._build_error_result(f"无法解析JSON: {line_text}", code="invalid_stream_json")

            return self._wrap_stream_generator(_stream_factory, error_prefix="流式响应失败")

        async def _operation() -> Dict[str, Any]:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{normalized_base_url}/api/generate", json=params) as response:
                    if response.status != 200:
                        return self._build_error_result(f"文本完成请求失败: HTTP {response.status}", code="http_error")
                    data = await response.json()

            return {
                "id": f"cmpl-{time.time()}",
                "object": "text_completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "text": data.get("response", ""),
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": -1,  # Ollama不提供token统计
                    "completion_tokens": -1,
                    "total_tokens": -1
                }
            }

        return await self._execute_timed_dict_call(_operation, error_prefix="文本完成请求失败")
    
    async def embedding(
        self,
        api_key: str,
        text: Union[str, List[str]],
        model: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取文本嵌入向量从Ollama API"""
        normalized_base_url = RequestBuilder.normalize_base_url(base_url, self.default_base_url)
        # 处理输入文本
        input_texts = []
        if isinstance(text, str):
            input_texts = [text]
        else:
            input_texts = text
        
        # Ollama的嵌入端点一次只处理一条文本，这里统一循环聚合。
        embeddings_list = []

        async def _operation() -> Dict[str, Any]:
            async with aiohttp.ClientSession() as session:
                for input_text in input_texts:
                    params = {
                        "model": model,
                        "prompt": input_text
                    }
                    # print("请求参数::",params)
                    # 添加其他参数
                    for key, value in kwargs.items():
                        if key not in ["model", "prompt"]:
                            params[key] = value
                    
                    async with session.post(f"{normalized_base_url}/api/embeddings", json=params) as response:
                        if response.status != 200:
                            return self._build_error_result(f"嵌入请求失败: HTTP {response.status}", code="http_error")
                        data = await response.json()
                        if "embedding" in data:
                            embeddings_list.append(data["embedding"])

            return {
                "object": "embedding_list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": embedding,
                        "index": i
                    }
                    for i, embedding in enumerate(embeddings_list)
                ],
                "model": model,
                "usage": {
                    "prompt_tokens": -1,  # Ollama不提供token统计
                    "total_tokens": -1
                },
                "embeddings": embeddings_list,  # 添加直接可用的嵌入列表
            }

        return await self._execute_timed_dict_call(_operation, error_prefix="嵌入请求失败")
    
    async def image_analysis(
        self,
        api_key: str,
        image_path: str,
        prompt: str = "请详细描述这张图片的内容",
        model: str = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Ollama多模态模型分析图片内容
        
        Args:
            api_key: API密钥（Ollama不需要但保留参数以兼容接口）
            image_path: 图片文件路径或URL
            prompt: 提示文本，引导模型如何分析图片
            model: 模型名称，默认为"llava"（多模态模型）
            base_url: API基础URL，可选
            **kwargs: 其他参数
            
        Returns:
            Dict包含图片分析结果
        """
        try:
            # 设置默认多模态模型
            if model is None or not model:
                model = "llava:latest"
                
            # 日志记录
            print(f"使用Ollama多模态模型 {model} 分析图片: {image_path}")
            
            # 读取图片数据并转换为base64
            image_data = None
            if image_path.startswith(('http://', 'https://')):
                # 处理URL图片
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_path) as response:
                        if response.status != 200:
                            raise Exception(f"获取图片失败，HTTP状态码：{response.status}")
                        image_data = await response.read()
            else:
                # 处理本地图片
                if not os.path.exists(image_path):
                    raise Exception(f"图片文件不存在：{image_path}")
                with open(image_path, "rb") as f:
                    image_data = f.read()
                    
            # 确认图片数据已获取
            if not image_data:
                raise Exception("无法读取图片数据")
                
            # 将图片编码为base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Ollama的聊天API端点
            url = f"{base_url or self.default_base_url}/api/chat"
            
            # 构建带图像的消息
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64_image]
                }
            ]
            
            # 设置请求参数
            params = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            # 处理max_tokens参数
            if "max_tokens" in kwargs:
                params["options"]["num_predict"] = kwargs["max_tokens"]
                
            start_time = time.time()
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params) as response:
                    if response.status != 200:
                        return {
                            "status": "error",
                            "message": f"图片分析请求失败: HTTP {response.status}",
                            "response_time_ms": round((time.time() - start_time) * 1000)
                        }
                    
                    data = await response.json()
                    
            response_time = round((time.time() - start_time) * 1000)
            print(f"图片分析完成，响应时间: {response_time}ms")
            
            # 从响应中提取文本内容
            analysis_text = ""
            if "message" in data and "content" in data["message"]:
                analysis_text = data["message"]["content"]
            
            return {
                "status": "success",
                "model": model,
                "analysis": analysis_text,
                "response_time_ms": response_time
            }
            
        except Exception as e:
            print(f"图片分析失败: {str(e)}")
            return {
                "status": "error",
                "message": f"图片分析失败: {str(e)}",
                "response_time_ms": -1
            } 
