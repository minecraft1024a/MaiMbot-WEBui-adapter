import asyncio
import sys
from loguru import logger
from src.app import AdapterApp

def setup_logging():
    """配置日志记录器"""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

async def main():
    """主异步函数"""
    setup_logging()
    app = AdapterApp()
    try:
        await app.run()
    except KeyboardInterrupt:
        logger.info("用户手动停止应用")
    except Exception as e:
        logger.error(f"应用出现未捕获的异常: {e}", exc_info=True)
    finally:
        await app.stop()

if __name__ == "__main__":
    # 注意：命令行发送消息的功能已移除，专注于作为服务运行
    # 如果需要该功能，可以考虑使用 `argparse` 等库进行更完善的实现
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Adapter已停止")
