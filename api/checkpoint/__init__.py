"""Checkpoint 上下文存储 - 用于多步骤对话场景"""

import uuid
from typing import Any, Dict, Optional


class CheckpointStore:
    """内存中的 checkpoint 会话存储"""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def create_session(self, initial_context: Optional[Dict[str, Any]] = None) -> str:
        """创建新会话，返回 session_id"""
        session_id = uuid.uuid4().hex[:12]  # 短 ID 方便传递
        self._store[session_id] = {
            "context": initial_context or {},
            "step": "init",
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话数据"""
        return self._store.get(session_id)

    def update_session(self, session_id: str, context: Dict[str, Any]) -> bool:
        """更新会话上下文"""
        if session_id not in self._store:
            return False
        self._store[session_id]["context"].update(context)
        return True

    def set_step(self, session_id: str, step: str) -> bool:
        """设置当前对话步骤"""
        if session_id not in self._store:
            return False
        self._store[session_id]["step"] = step
        return True

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return self._store.pop(session_id, None) is not None


# 全局单例
checkpoint_store = CheckpointStore()
