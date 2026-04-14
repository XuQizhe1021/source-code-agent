from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.application.knowledge.ports import KnowledgeRecordPort, KnowledgeRepositoryPort
from app.models.knowledge import Knowledge, KnowledgeFile


class SqlAlchemyKnowledgeRepository(KnowledgeRepositoryPort):
    """基于 SQLAlchemy 的 Repository 适配器实现。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeRecordPort]:
        return self.db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()

    def count_indexed_files(self, knowledge_id: str) -> int:
        count = self.db.query(func.count(KnowledgeFile.id)).filter(
            KnowledgeFile.knowledge_id == knowledge_id,
            KnowledgeFile.status == "indexed",
        ).scalar()
        return count or 0

    def get_knowledge_file_name(self, knowledge_file_id: str) -> Optional[str]:
        record = self.db.query(KnowledgeFile).filter(KnowledgeFile.id == knowledge_file_id).first()
        if not record:
            return None
        return record.original_filename
