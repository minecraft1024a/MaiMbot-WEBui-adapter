"""
配置管理模块
"""
import os
import json
from typing import Dict, Any


class Config:
    """应用配置管理"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(self.base_dir, 'chat.db')
        self.config_path = os.path.join(self.base_dir, '../public/server_config.json')
        
        # 默认配置
        self.host = '127.0.0.1'
        self.port = 8050
        
        # 加载服务器配置
        self._load_server_config()
    
    def _load_server_config(self) -> None:
        """加载服务器配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.host = config.get('host', self.host)
                    self.port = int(config.get('port', self.port))
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return self.db_path


# 全局配置实例
config = Config()
