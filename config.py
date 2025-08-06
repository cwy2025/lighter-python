import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LighterConfig:
    """Lighter交易所配置类"""
    
    # API配置
    API_KEY = os.getenv('LIGHTER_API_KEY', '')
    API_SECRET = os.getenv('LIGHTER_API_SECRET', '')
    ACCOUNT_ID = os.getenv('LIGHTER_ACCOUNT_ID', '1')  # 默认账户ID
    
    # API端点 - 使用Lighter的实际端点
    BASE_URL = os.getenv('LIGHTER_BASE_URL', 'https://mainnet.zklighter.elliot.ai')
    WS_URL = os.getenv('LIGHTER_WS_URL', 'wss://ws.lighter.xyz')
    
    # 测试网络端点
    TESTNET_BASE_URL = os.getenv('LIGHTER_TESTNET_URL', 'https://testnet.zklighter.elliot.ai')
    USE_TESTNET = os.getenv('LIGHTER_USE_TESTNET', 'false').lower() == 'true'
    
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
    def get_base_url(cls):
        """获取正确的基础URL"""
        if cls.USE_TESTNET:
            return cls.TESTNET_BASE_URL
        return cls.BASE_URL
    
    @classmethod
    def validate_config(cls):
        """验证配置是否完整"""
        # 对于Lighter，API密钥不是必须的（可以访问公开数据）
        # 但如果要访问私有数据，则需要密钥
        if cls.API_KEY and not cls.API_SECRET:
            raise ValueError("设置了API_KEY但缺少API_SECRET")
        return True
    
    @classmethod
    def is_authenticated(cls):
        """检查是否有认证信息"""
        return bool(cls.API_KEY and cls.API_SECRET)

# 创建全局配置实例
config = LighterConfig()