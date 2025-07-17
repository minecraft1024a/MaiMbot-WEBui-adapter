import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

class BackendClient:
    """与后端HTTP服务交互的客户端"""
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.http_client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def get_messages(self) -> Optional[List[Dict[str, Any]]]:
        """从后端获取所有消息"""
        try:
            resp = await self.http_client.get("/messages")
            resp.raise_for_status()
            msgs = resp.json()
            if not isinstance(msgs, list):
                logger.warning(f"[Adapter] /messages 返回内容不是列表: {msgs}")
                return None
            return msgs
        except httpx.RequestError as e:
            logger.error(f"[Adapter] 轮询消息失败 (Request Error): {e}")
            return None
        except Exception as e:
            logger.error(f"[Adapter] 获取消息时出错: {e}", exc_info=True)
            return None

    async def send_message(self, payload: Dict[str, Any]):
        """发送消息到后端"""
        try:
            logger.info(f"[Adapter] 正在转发消息到后端: {payload}")
            await self.http_client.post("/messages", json=payload)
        except httpx.RequestError as e:
            logger.error(f"[Adapter] 发送到后端失败 (Request Error): {e}")
        except Exception as e:
            logger.error(f"[Adapter] 发送到后端失败 (General Error): {e}")

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()
        logger.info("HTTP客户端已关闭")
