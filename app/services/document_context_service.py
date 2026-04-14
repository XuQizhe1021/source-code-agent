from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.file import File as FileModel
from app.utils.file_processor import extract_text_from_file_path


@dataclass
class DocumentProcessResult:
    """文件上下文处理结果。"""

    events: List[Dict[str, Any]] = field(default_factory=list)
    system_message: Optional[str] = None
    has_file_content: bool = False


class DocumentContextService:
    """
    文件上下文服务。

    这层拆分的目的不是“搬代码”，而是把“文件读取/降级/截断规则”
    从聊天编排函数中隔离出来，避免主流程被 I/O 细节淹没。
    """

    def __init__(self, max_content_length: int = 3000) -> None:
        self.max_content_length = max_content_length

    async def process_files(self, file_ids: List[str], db: Session) -> DocumentProcessResult:
        result = DocumentProcessResult()
        if not file_ids:
            return result

        processed_chunks: List[str] = []
        result.events.append(self._event("status", {"object": "chat.completion.status", "status": "正在处理上传文件"}))

        for file_id in file_ids:
            file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
            if not file_record:
                result.events.append(self._event("file_processing", {"status": f"文件不存在: {file_id}"}))
                continue

            if file_record.status != "processed":
                if file_record.status == "processing":
                    status_text = f"文件 {file_record.original_filename} 正在处理中，请稍后再试"
                else:
                    status_text = f"文件 {file_record.original_filename} 未处理完成，状态: {file_record.status}"
                result.events.append(self._event("file_processing", {"status": status_text}))
                continue

            file_content = await self._load_file_content(file_record)
            if not file_content:
                result.events.append(
                    self._event(
                        "file_processing",
                        {"status": f"文件 {file_record.original_filename} 没有可用文本内容"},
                    )
                )
                continue

            if len(file_content) > self.max_content_length:
                file_content = (
                    file_content[: self.max_content_length]
                    + f"\n\n[内容过长，已截断。原文共 {len(file_content)} 字符]"
                )

            processed_chunks.append(
                f"--- 文件: {file_record.original_filename} ({file_record.file_type}) ---\n\n{file_content}\n"
            )
            result.events.append(
                self._event("file_processing", {"status": f"已处理文件: {file_record.original_filename}"})
            )

        if processed_chunks:
            combined = "\n".join(processed_chunks)
            result.system_message = (
                "以下是用户上传的文件内容，这是非常重要的上下文信息，请务必仔细阅读并在回答问题时参考这些内容。"
                f"\n\n{combined}"
            )
            result.has_file_content = True

        return result

    async def _load_file_content(self, file_record: FileModel) -> str:
        if file_record.text_content:
            return file_record.text_content

        # 为什么要做 MinIO 兜底：历史数据可能只存了对象路径，没有回写 text_content，
        # 如果直接放弃会导致“上传成功但问答读不到内容”的体验断层。
        if not file_record.path or "/" not in file_record.path:
            return ""

        from app.core.minio_client import get_file_stream

        bucket, object_name = file_record.path.split("/", 1)
        response = get_file_stream(bucket, object_name)
        if not response:
            return ""

        temp_file_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_record.file_type}") as temp_file:
                temp_file.write(response.read())
                temp_file_path = temp_file.name

            file_content = await extract_text_from_file_path(temp_file_path)
            if file_content and not file_content.startswith("提取文件文本内容时出错"):
                return file_content

            for encoding in ("utf-8", "latin-1"):
                try:
                    with open(temp_file_path, "r", encoding=encoding) as file_obj:
                        return file_obj.read()
                except UnicodeDecodeError:
                    continue
            return ""
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @staticmethod
    def _event(event: str, payload: Dict[str, Any]) -> Dict[str, str]:
        import json

        return {"event": event, "data": json.dumps(payload, ensure_ascii=False)}

