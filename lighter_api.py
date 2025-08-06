import hashlib
import hmac
import time
import json
import requests
from typing import Dict, Any, Optional
from config import config


class LighterAPIClient:
    """Lighter交易所API客户端"""
    
    def __init__(self):
        self.api_key = config.API_KEY
        self.api_secret = config.API_SECRET
        self.base_url = config.BASE_URL
        self.timeout = config.TIMEOUT
        self.session = requests.Session()
        
        # 设置默认headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key
        })
    
    def _generate_signature(self, timestamp: int, method: str, path: str, body: str = '') -> str:
        """生成API签名 - 根据Lighter实际签名算法调整"""
        # 这是一个通用的签名方法，需要根据Lighter的实际文档调整
        message = f"{timestamp}{method.upper()}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[Any, Any]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        timestamp = int(time.time() * 1000)
        
        # 准备请求体
        body = ''
        if data:
            body = json.dumps(data, separators=(',', ':'))
        
        # 生成签名
        signature = self._generate_signature(timestamp, method, endpoint, body)
        
        headers = {
            'X-TIMESTAMP': str(timestamp),
            'X-SIGNATURE': signature
        }
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return {}
    
    def get_account_info(self) -> Dict[Any, Any]:
        """获取账户信息"""
        return self._make_request('GET', '/api/v1/account')
    
    def get_balances(self) -> Dict[Any, Any]:
        """获取余额信息"""
        return self._make_request('GET', '/api/v1/balances')
    
    def get_positions(self) -> Dict[Any, Any]:
        """获取持仓信息"""
        return self._make_request('GET', '/api/v1/positions')
    
    def get_portfolio(self) -> Dict[Any, Any]:
        """获取投资组合信息，包含总权益等"""
        return self._make_request('GET', '/api/v1/portfolio')
    
    def get_open_orders(self) -> Dict[Any, Any]:
        """获取未成交订单"""
        return self._make_request('GET', '/api/v1/orders/open')
    
    def get_trade_history(self, limit: int = 50) -> Dict[Any, Any]:
        """获取交易历史"""
        params = {'limit': limit}
        return self._make_request('GET', '/api/v1/trades', params=params)
    
    def get_markets(self) -> Dict[Any, Any]:
        """获取市场信息"""
        return self._make_request('GET', '/api/v1/markets')

    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class MockLighterAPI:
    """模拟Lighter API - 用于测试和演示"""
    
    def __init__(self):
        self.mock_data = {
            'total_equity': 150000.0,
            'unrealized_pnl': 2500.0,
            'positions': [
                {
                    'symbol': 'BTC-PERP',
                    'size': 1.5,
                    'entry_price': 95000.0,
                    'mark_price': 96500.0,
                    'unrealized_pnl': 2250.0,
                    'position_value': 144750.0,
                    'side': 'long'
                },
                {
                    'symbol': 'ETH-PERP', 
                    'size': -10.0,
                    'entry_price': 3500.0,
                    'mark_price': 3475.0,
                    'unrealized_pnl': 250.0,
                    'position_value': -34750.0,
                    'side': 'short'
                }
            ],
            'balances': [
                {'asset': 'USDT', 'balance': 50000.0, 'available': 45000.0},
                {'asset': 'BTC', 'balance': 0.1, 'available': 0.05}
            ]
        }
    
    def get_account_info(self):
        return {'success': True, 'data': self.mock_data}
    
    def get_balances(self):
        return {'success': True, 'data': self.mock_data['balances']}
    
    def get_positions(self):
        return {'success': True, 'data': self.mock_data['positions']}
    
    def get_portfolio(self):
        return {
            'success': True, 
            'data': {
                'total_equity': self.mock_data['total_equity'],
                'unrealized_pnl': self.mock_data['unrealized_pnl']
            }
        }
    
    def health_check(self):
        return True


def create_api_client(use_mock: bool = False) -> Any:
    """创建API客户端实例"""
    if use_mock:
        return MockLighterAPI()
    else:
        try:
            config.validate_config()
            return LighterAPIClient()
        except ValueError as e:
            print(f"配置验证失败: {e}")
            print("使用模拟API进行演示...")
            return MockLighterAPI()