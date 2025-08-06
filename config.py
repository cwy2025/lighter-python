import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LighterConfig:
    """Lighter交易所配置类"""
    
    # API配置
    API_KEY = os.getenv('LIGHTER_API_KEY', '')
    API_SECRET = os.getenv('LIGHTER_API_SECRET', '')
    
    # API端点 - 根据Lighter实际文档调整
    BASE_URL = os.getenv('LIGHTER_BASE_URL', 'https://api.lighter.xyz')
    WS_URL = os.getenv('LIGHTER_WS_URL', 'wss://ws.lighter.xyz')
    
    # 请求配置
    TIMEOUT = int(os.getenv('TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # 监控配置
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '60'))  # 60秒刷新一次
    DISPLAY_PRECISION = int(os.getenv('DISPLAY_PRECISION', '6'))  # 显示精度
    
    # WebSocket配置
    WS_PING_INTERVAL = int(os.getenv('WS_PING_INTERVAL', '30'))
    WS_PING_TIMEOUT = int(os.getenv('WS_PING_TIMEOUT', '10'))
    
    @classmethod
    def validate_config(cls):
        """验证配置是否完整"""
        if not cls.API_KEY:
            raise ValueError("LIGHTER_API_KEY未设置")
        if not cls.API_SECRET:
            raise ValueError("LIGHTER_API_SECRET未设置")
        return True

# 创建全局配置实例
config = LighterConfig()