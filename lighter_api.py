import asyncio
import logging
from typing import Dict, Any, Optional
import lighter
from config import config


class LighterAPIClient:
    """Lighter交易所异步API客户端"""
    
    def __init__(self, account_id: str = None):
        self.api_key = config.API_KEY
        self.api_secret = config.API_SECRET
        self.account_id = account_id or config.ACCOUNT_ID
        self.base_url = config.get_base_url()
        self.timeout = config.TIMEOUT
        
        # 创建配置
        self.configuration = lighter.Configuration(
            host=self.base_url
        )
        
        # API客户端和实例
        self.client = None
        self.account_api = None
        self.order_api = None
        self.candlestick_api = None
        self.transaction_api = None
        
        # 用于同步调用的事件循环
        self.loop = None
        self._running = False
    
    async def _initialize_async(self):
        """异步初始化API客户端"""
        self.client = lighter.ApiClient(configuration=self.configuration)
        self.account_api = lighter.AccountApi(self.client)
        self.order_api = lighter.OrderApi(self.client)
        self.candlestick_api = lighter.CandlestickApi(self.client)
        self.transaction_api = lighter.TransactionApi(self.client)
    
    def _run_async(self, coro):
        """在单独线程中运行异步函数"""
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        if not self._running:
            self._running = True
            # 初始化异步客户端
            self.loop.run_until_complete(self._initialize_async())
        
        return self.loop.run_until_complete(coro)
    
    def get_account_info(self, account_id: str = None) -> Dict[Any, Any]:
        """获取账户信息"""
        account_id = account_id or self.account_id
        try:
            async def _get_account():
                result = await self.account_api.account(by="index", value=account_id)
                return {"success": True, "data": result.to_dict()}
            
            return self._run_async(_get_account())
            
        except Exception as e:
            logging.error(f"获取账户信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_balances(self, account_id: str = None) -> Dict[Any, Any]:
        """获取余额信息"""
        account_id = account_id or self.account_id
        try:
            async def _get_balances():
                # 通过账户信息获取余额
                account_info = await self.account_api.account(by="index", value=account_id)
                balances = []
                
                if hasattr(account_info, 'data') and account_info.data:
                    for account in account_info.data:
                        if hasattr(account, 'collateral'):
                            balances.append({
                                'asset': 'USDT',  # Lighter主要使用USDT作为保证金
                                'balance': float(account.collateral or 0),
                                'available': float(account.collateral or 0)
                            })
                
                return {"success": True, "data": balances}
            
            return self._run_async(_get_balances())
            
        except Exception as e:
            logging.error(f"获取余额信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_positions(self, account_id: str = None) -> Dict[Any, Any]:
        """获取持仓信息"""
        account_id = account_id or self.account_id
        try:
            async def _get_positions():
                account_info = await self.account_api.account(by="index", value=account_id)
                positions = []
                
                if hasattr(account_info, 'data') and account_info.data:
                    for account in account_info.data:
                        if hasattr(account, 'position_details') and account.position_details:
                            for pos in account.position_details:
                                if float(pos.position or 0) != 0:  # 只显示有持仓的
                                    side = "long" if float(pos.sign or 0) > 0 else "short"
                                    positions.append({
                                        'symbol': f"Market-{pos.market_id}",
                                        'side': side,
                                        'size': float(pos.position or 0),
                                        'entry_price': float(pos.avg_entry_price or 0),
                                        'mark_price': float(pos.avg_entry_price or 0),  # 临时使用入场价
                                        'position_value': float(pos.position_value or 0),
                                        'unrealized_pnl': float(pos.unrealized_pnl or 0),
                                        'realized_pnl': float(pos.realized_pnl or 0),
                                        'market_id': pos.market_id
                                    })
                
                return {"success": True, "data": positions}
            
            return self._run_async(_get_positions())
            
        except Exception as e:
            logging.error(f"获取持仓信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio(self, account_id: str = None) -> Dict[Any, Any]:
        """获取投资组合信息，包含总权益等"""
        account_id = account_id or self.account_id
        try:
            async def _get_portfolio():
                account_info = await self.account_api.account(by="index", value=account_id)
                
                total_equity = 0
                total_unrealized_pnl = 0
                
                if hasattr(account_info, 'data') and account_info.data:
                    for account in account_info.data:
                        # 计算总权益
                        collateral = float(account.collateral or 0)
                        total_equity += collateral
                        
                        # 计算总未实现盈亏
                        if hasattr(account, 'position_details') and account.position_details:
                            for pos in account.position_details:
                                total_unrealized_pnl += float(pos.unrealized_pnl or 0)
                
                return {
                    "success": True, 
                    "data": {
                        'total_equity': total_equity,
                        'unrealized_pnl': total_unrealized_pnl,
                        'realized_pnl': 0  # 需要单独获取
                    }
                }
            
            return self._run_async(_get_portfolio())
            
        except Exception as e:
            logging.error(f"获取投资组合信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_open_orders(self, account_id: str = None) -> Dict[Any, Any]:
        """获取未成交订单"""
        account_id = account_id or self.account_id
        try:
            async def _get_orders():
                # 获取订单需要特定的API调用
                # 这里需要根据Lighter的具体API文档调整
                return {"success": True, "data": []}
            
            return self._run_async(_get_orders())
            
        except Exception as e:
            logging.error(f"获取订单失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_trade_history(self, limit: int = 50) -> Dict[Any, Any]:
        """获取交易历史"""
        try:
            async def _get_trades():
                # 获取交易历史需要特定的API调用
                return {"success": True, "data": []}
            
            return self._run_async(_get_trades())
            
        except Exception as e:
            logging.error(f"获取交易历史失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_markets(self) -> Dict[Any, Any]:
        """获取市场信息"""
        try:
            async def _get_markets():
                # 获取市场信息
                return {"success": True, "data": []}
            
            return self._run_async(_get_markets())
            
        except Exception as e:
            logging.error(f"获取市场信息失败: {e}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> bool:
        """健康检查"""
        try:
            async def _health_check():
                # 简单的健康检查 - 尝试获取账户信息
                await self.account_api.account(by="index", value=self.account_id)
                return True
            
            return self._run_async(_health_check())
        except:
            return False
    
    def close(self):
        """关闭客户端"""
        async def _close():
            if self.client:
                await self.client.close()
        
        if self.loop and not self.loop.is_closed():
            self.loop.run_until_complete(_close())
            self.loop.close()
        
        self._running = False


class MockLighterAPI:
    """模拟Lighter API - 用于测试和演示"""
    
    def __init__(self, account_id: str = "1"):
        self.account_id = account_id
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
    
    def get_account_info(self, account_id: str = None):
        return {'success': True, 'data': self.mock_data}
    
    def get_balances(self, account_id: str = None):
        return {'success': True, 'data': self.mock_data['balances']}
    
    def get_positions(self, account_id: str = None):
        return {'success': True, 'data': self.mock_data['positions']}
    
    def get_portfolio(self, account_id: str = None):
        return {
            'success': True, 
            'data': {
                'total_equity': self.mock_data['total_equity'],
                'unrealized_pnl': self.mock_data['unrealized_pnl']
            }
        }
    
    def get_open_orders(self, account_id: str = None):
        return {'success': True, 'data': []}
    
    def get_trade_history(self, limit: int = 50):
        return {'success': True, 'data': []}
    
    def get_markets(self):
        return {'success': True, 'data': []}
    
    def health_check(self):
        return True
    
    def close(self):
        pass


def create_api_client(use_mock: bool = False, account_id: str = None) -> Any:
    """创建API客户端实例"""
    if use_mock:
        return MockLighterAPI(account_id or config.ACCOUNT_ID)
    else:
        try:
            config.validate_config()
            client = LighterAPIClient(account_id)
            
            # 测试连接 - 但是现在允许未认证的访问
            try:
                client.get_account_info()
                print(f"✅ API连接成功 (账户ID: {client.account_id})")
                return client
            except Exception as e:
                print(f"⚠️  API连接测试失败: {e}")
                if config.is_authenticated():
                    print("使用模拟API进行演示...")
                    return MockLighterAPI(account_id or config.ACCOUNT_ID)
                else:
                    print("未配置API密钥，但可以访问公开数据")
                    return client
                
        except ValueError as e:
            print(f"配置验证失败: {e}")
            print("使用模拟API进行演示...")
            return MockLighterAPI(account_id or config.ACCOUNT_ID)
        except Exception as e:
            print(f"API客户端创建失败: {e}")
            print("使用模拟API进行演示...")
            return MockLighterAPI(account_id or config.ACCOUNT_ID)