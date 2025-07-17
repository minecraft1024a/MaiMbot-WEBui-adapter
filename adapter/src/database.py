import sqlite3
from typing import Optional
from loguru import logger

class DatabaseManager:
    """数据库管理器"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """初始化数据库并建立连接"""
        try:
            logger.info(f"正在连接数据库: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute('CREATE TABLE IF NOT EXISTS session_group (session_id TEXT PRIMARY KEY, group_id TEXT)')
            self.conn.commit()
            logger.info(f"数据库连接已建立: {self.db_path}")
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            self.conn = None

    def get_or_create_group_id(self, session_id: str) -> str:
        """获取或创建群组ID"""
        if not self.conn:
            logger.error("数据库未连接，无法操作")
            return session_id

        try:
            cur = self.conn.execute('SELECT group_id FROM session_group WHERE session_id=?', (session_id,))
            row = cur.fetchone()
            if row:
                return row[0]
            
            group_id = session_id
            self.conn.execute('INSERT INTO session_group (session_id, group_id) VALUES (?, ?)', (session_id, group_id))
            self.conn.commit()
            return group_id
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            return session_id

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
