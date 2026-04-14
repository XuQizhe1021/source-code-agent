import logging
from dataclasses import dataclass
from typing import Optional, Any, Dict

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.models.extraction_task import ExtractionTask
from app.models.graph_file import GraphFile
from app.models.graph import Graph as GraphModel
from app.utils.config import get_neo4j_config
from app.utils.graph import extract_knowledge_with_llm_task, process_graph_file
from app.utils.neo4j_utils import get_neo4j_service


@dataclass
class CreateGraphCommand:
    """创建图谱命令对象：把接口层参数打包成用例输入。"""

    name: str
    description: Optional[str] = None
    status: str = "active"
    model_id: Optional[str] = None
    dynamic_schema: bool = True


@dataclass
class ExtractKnowledgeCommand:
    """知识抽取命令对象：收敛接口入参，避免控制器直接编排流程。"""

    graph_id: str
    data: Dict[str, Any]


class GraphAppService:
    """图谱应用服务：负责用例编排，避免 Controller 直接堆业务细节。"""

    def __init__(self, db: Session, logger_obj: Optional[logging.Logger] = None) -> None:
        self.db = db
        self.logger = logger_obj or logging.getLogger(__name__)

    def create_graph(self, cmd: CreateGraphCommand, user_id: str) -> GraphModel:
        """
        创建图谱主流程。
        为什么这么拆：
        - Endpoint 只做协议适配和异常映射，避免演变为“上帝入口”；
        - 业务编排集中在应用服务，后续加限流、指标、重试时只改一处。
        """
        try:
            graph = GraphModel(
                name=cmd.name,
                description=cmd.description or "",
                status=cmd.status,
                entity_count=0,
                relation_count=0,
                model_id=cmd.model_id,
                config={},
                neo4j_status="pending",
                dynamic_schema=cmd.dynamic_schema,
                user_id=user_id,
            )
            self.db.add(graph)
            self.db.commit()
            self.db.refresh(graph)
        except Exception as exc:
            self.db.rollback()
            raise RuntimeError(f"创建知识图谱失败: {str(exc)}") from exc

        self._try_create_neo4j_subgraph(graph)
        return graph

    def _try_create_neo4j_subgraph(self, graph: GraphModel) -> None:
        """
        尝试创建 Neo4j 子图。
        为什么异常吞掉：
        - 该步骤属于增强能力，不应阻塞“图谱创建”这个核心成功路径；
        - 保持与旧接口行为兼容，前端无需改造。
        """
        try:
            neo4j_config = get_neo4j_config()
            neo4j_service = get_neo4j_service(
                uri=neo4j_config["uri"],
                username=neo4j_config["username"],
                password=neo4j_config["password"],
                database=neo4j_config["database"],
                force_new=True,
            )
            subgraph_name = graph.id
            success = neo4j_service.create_subgraph(subgraph_name)
            if not success:
                self.logger.warning("创建Neo4j子图失败: graph_id=%s", graph.id)
                return

            graph.neo4j_subgraph = subgraph_name
            graph.neo4j_status = "created"
            neo4j_service.create_vector_index(subgraph_name)
            graph.neo4j_stats = neo4j_service.get_subgraph_statistics(subgraph_name)

            self.db.add(graph)
            self.db.commit()
            self.db.refresh(graph)
            self.logger.info("成功创建Neo4j子图: %s", subgraph_name)
        except Exception as exc:
            # 这里只记录不抛错，确保主流程“创建图谱”仍可成功返回。
            self.db.rollback()
            self.logger.warning("创建Neo4j子图时出错: graph_id=%s error=%s", graph.id, str(exc))

    def submit_extract_task(
        self,
        cmd: ExtractKnowledgeCommand,
        background_tasks: BackgroundTasks,
        db_session_maker: Any,
    ) -> Dict[str, Any]:
        """
        提交“基于图谱关联模型的知识抽取”任务。
        为什么放在应用服务：
        - 这里包含状态判断、任务创建、后台任务投递，属于典型业务编排；
        - 下沉后 Endpoint 只保留协议层职责，更容易持续压薄。
        """
        graph = self.db.query(GraphModel).filter(GraphModel.id == cmd.graph_id).first()
        if not graph:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识图谱不存在",
            )

        # 保持旧接口兼容：未绑定模型时返回业务code，而不是抛HTTP错误。
        if not graph.model_id:
            return {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "知识图谱未关联模型，请先在基本信息中关联一个对话模型",
            }

        if "fileId" not in cmd.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少必要参数: fileId",
            )

        file_id = cmd.data["fileId"]
        file = self.db.query(GraphFile).filter(
            GraphFile.id == file_id,
            GraphFile.graph_id == cmd.graph_id,
        ).first()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在",
            )

        # 兼容旧行为：待处理/失败文件会先触发解析流程，再继续投递抽取任务。
        if file.status in {"pending", "failed"}:
            file.status = "processing"
            self.db.add(file)
            self.db.commit()
            background_tasks.add_task(
                process_graph_file,
                file_id,
                cmd.graph_id,
            )

        task = ExtractionTask(
            graph_id=cmd.graph_id,
            file_id=file_id,
            task_type="llm_extraction",
            status="pending",
            parameters={"use_llm": True},
            result=None,
            model_id=graph.model_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        background_tasks.add_task(
            extract_knowledge_with_llm_task,
            db_session_maker=db_session_maker,
            task_id=task.id,
            graph_id=cmd.graph_id,
            file_id=file_id,
        )

        return {
            "code": status.HTTP_200_OK,
            "message": "大模型知识抽取任务已提交",
            "data": {
                "taskId": task.id,
                "fileId": file_id,
                "status": "pending",
            },
        }
