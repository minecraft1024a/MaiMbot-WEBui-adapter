"""
前端启动器模块
"""
import os
import subprocess
import webbrowser
import threading
import time
from loguru import logger


class FrontendLauncher:
    """前端启动器"""
    
    def __init__(self, frontend_port: int = 5173):
        self.frontend_port = frontend_port
        self.frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
    def start_frontend(self) -> None:
        """启动前端服务"""
        def run_frontend():
            # 检查前端目录是否存在
            if not os.path.exists(os.path.join(self.frontend_dir, 'package.json')):
                logger.warning(f"未找到前端 package.json，前端未启动。路径: {self.frontend_dir}")
                return
            
            try:
                # 启动前端开发服务器
                logger.info("正在启动前端服务...")
                subprocess.Popen(
                    ["npm", "run", "dev"], 
                    cwd=self.frontend_dir, 
                    shell=True
                )
                
                # 等待前端服务启动
                time.sleep(3)
                
                # 自动打开浏览器
                browser_url = f"http://localhost:{self.frontend_port}"
                logger.info(f"打开浏览器: {browser_url}")
                webbrowser.open_new_tab(browser_url)
                
            except Exception as e:
                logger.error(f"启动前端失败: {e}")
        
        # 在后台线程中启动前端
        threading.Thread(target=run_frontend, daemon=True).start()
