import os
import tomllib
from typing import Dict, Any
from loguru import logger

PLATFORM_ID = "maimai_http_adapter"

class AdapterConfig:
    """适配器配置管理"""
    def __init__(self, config_path: str = 'config.toml'):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'adapter': {
                'platform_id': PLATFORM_ID,
                'poll_interval': 2
            },
            'connection': {
                'ws_url': 'ws://127.0.0.1:8000/ws',
                'http_backend_url': 'http://127.0.0.1:8050'
            },
            'database': {
                'db_path': '../http_server/backend/chat.db'
            },
            'logging': {
                'level': 'INFO'
            }
        }

    @property
    def platform_id(self) -> str:
        return self._config['adapter']['platform_id']

    @property
    def poll_interval(self) -> int:
        return self._config['adapter']['poll_interval']

    @property
    def ws_url(self) -> str:
        return self._config['connection']['ws_url']

    @property
    def http_backend_url(self) -> str:
        url = self._config['connection']['http_backend_url']
        return url.rstrip('/')

    @property
    def db_path(self) -> str:
        # 从项目根目录的 adapter 文件夹开始计算
        base_path = os.path.dirname(self.config_path)
        return os.path.join(base_path, self._config['database']['db_path'])
