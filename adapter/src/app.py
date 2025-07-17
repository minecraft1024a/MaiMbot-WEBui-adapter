import asyncio
from loguru import logger
from maim_message import Router, RouteConfig, TargetConfig

from .config import AdapterConfig
from .database import DatabaseManager
from .client import BackendClient
from . import handlers

class AdapterApp:
    """适配器主应用"""
    def __init__(self):
        self.config = AdapterConfig()
        self.db_manager = DatabaseManager(self.config.db_path)
        self.backend_client = BackendClient(self.config.http_backend_url)
        
        route_config = RouteConfig(
            route_config={
                self.config.platform_id: TargetConfig(
                    url=self.config.ws_url,
                    token=None
                )
            }
        )
        self.router = Router(route_config)
        self._register_handlers()
        
        self.last_message_count = 0
        self.is_running = False

    def _register_handlers(self):
        """注册消息处理器"""
        async def maibot_handler(message):
            await handlers.handle_from_maibot(message, self.backend_client)
        
        self.router.register_class_handler(maibot_handler)

    async def _poll_messages(self):
        """轮询来自后端的消息"""
        # 初始化消息计数
        initial_msgs = await self.backend_client.get_messages()
        self.last_message_count = len(initial_msgs) if initial_msgs else 0
        logger.info(f"消息轮询器初始化完成，当前消息数: {self.last_message_count}")

        while self.is_running:
            try:
                all_msgs = await self.backend_client.get_messages()
                if all_msgs is None:
                    await asyncio.sleep(self.config.poll_interval)
                    continue

                if self.last_message_count < 0 or self.last_message_count > len(all_msgs):
                    logger.warning(f"消息计数异常，重置计数器 from {self.last_message_count} to 0")
                    self.last_message_count = 0

                new_messages = all_msgs[self.last_message_count:]
                if new_messages:
                    logger.info(f"发现 {len(new_messages)} 条新消息")
                    for msg in new_messages:
                        maibot_msg = handlers.create_maibot_message(msg, self.config, self.db_manager)
                        if maibot_msg:
                            await self.router.send_message(maibot_msg)
                            logger.info(f"成功转发消息到 MaiBot Core (Session: {msg.get('session_id')})")
                
                self.last_message_count = len(all_msgs)
            except Exception as e:
                logger.error(f"[Adapter] 轮询或转发消息出错: {e}", exc_info=True)
            
            await asyncio.sleep(self.config.poll_interval)

    async def run(self):
        """启动应用"""
        self.is_running = True
        router_task = asyncio.create_task(self.router.run())
        poll_task = asyncio.create_task(self._poll_messages())
        
        logger.info("Adapter应用已启动")
        try:
            await asyncio.gather(router_task, poll_task)
        except asyncio.CancelledError:
            logger.info("应用任务被取消")
        finally:
            await self.stop()

    async def stop(self):
        """停止应用并清理资源"""
        self.is_running = False
        await self.backend_client.close()
        self.db_manager.close()
        # 取消正在运行的任务
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Adapter应用已优雅关闭")
