import json
import threading
import time
import websocket
from typing import Callable, Dict, Any, Optional
from config import config
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LighterWebSocketClient:
    """Lighter WebSocket客户端"""
    
    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.ws_url = config.WS_URL
        self.api_key = config.API_KEY
        self.api_secret = config.API_SECRET
        self.ws = None
        self.is_connected = False
        self.subscriptions = set()
        self.on_message_callback = on_message_callback
        self.reconnect_interval = 30
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        logger.info("WebSocket连接已建立")
        self.is_connected = True
        self.reconnect_attempts = 0
        
        # 发送认证消息
        self._authenticate()
        
        # 重新订阅之前的频道
        for subscription in self.subscriptions:
            self._send_subscription(subscription)
    
    def _on_message(self, ws, message):
        """收到消息回调"""
        try:
            data = json.loads(message)
            logger.debug(f"收到消息: {data}")
            
            if self.on_message_callback:
                self.on_message_callback(data)
                
        except json.JSONDecodeError:
            logger.error(f"无法解析消息: {message}")
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        logger.error(f"WebSocket错误: {error}")
        self.is_connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        logger.info("WebSocket连接已关闭")
        self.is_connected = False
        
        # 尝试重连
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"尝试重连 ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            time.sleep(self.reconnect_interval)
            self.connect()
    
    def _authenticate(self):
        """发送认证消息"""
        # 根据Lighter实际WebSocket认证协议调整
        auth_message = {
            "id": int(time.time() * 1000),
            "method": "auth",
            "params": {
                "api_key": self.api_key,
                "timestamp": int(time.time() * 1000)
                # 这里需要根据Lighter实际要求添加签名
            }
        }
        self._send_message(auth_message)
    
    def _send_message(self, message: Dict[str, Any]):
        """发送消息"""
        if self.ws and self.is_connected:
            try:
                self.ws.send(json.dumps(message))
                logger.debug(f"发送消息: {message}")
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
    
    def _send_subscription(self, subscription: Dict[str, Any]):
        """发送订阅消息"""
        self._send_message(subscription)
    
    def connect(self):
        """建立WebSocket连接"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 在单独线程中运行
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
    
    def disconnect(self):
        """断开WebSocket连接"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
    
    def subscribe_trades(self, symbol: Optional[str] = None):
        """订阅交易数据"""
        subscription = {
            "id": int(time.time() * 1000),
            "method": "subscribe",
            "params": {
                "channel": "trades" if not symbol else f"trades.{symbol}"
            }
        }
        self.subscriptions.add(json.dumps(subscription))
        self._send_subscription(subscription)
    
    def subscribe_positions(self):
        """订阅持仓更新"""
        subscription = {
            "id": int(time.time() * 1000),
            "method": "subscribe", 
            "params": {
                "channel": "positions"
            }
        }
        self.subscriptions.add(json.dumps(subscription))
        self._send_subscription(subscription)
    
    def subscribe_orders(self):
        """订阅订单更新"""
        subscription = {
            "id": int(time.time() * 1000),
            "method": "subscribe",
            "params": {
                "channel": "orders"
            }
        }
        self.subscriptions.add(json.dumps(subscription))
        self._send_subscription(subscription)
    
    def subscribe_account(self):
        """订阅账户更新"""
        subscription = {
            "id": int(time.time() * 1000),
            "method": "subscribe",
            "params": {
                "channel": "account"
            }
        }
        self.subscriptions.add(json.dumps(subscription))
        self._send_subscription(subscription)


class MockWebSocketClient:
    """模拟WebSocket客户端 - 用于测试"""
    
    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.on_message_callback = on_message_callback
        self.is_connected = True
        self.mock_thread = None
        self.running = False
        
    def connect(self):
        """模拟连接"""
        logger.info("模拟WebSocket连接已建立")
        self.is_connected = True
        self.running = True
        
        # 启动模拟数据发送线程
        self.mock_thread = threading.Thread(target=self._send_mock_data)
        self.mock_thread.daemon = True
        self.mock_thread.start()
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        self.is_connected = False
        logger.info("模拟WebSocket连接已断开")
    
    def _send_mock_data(self):
        """发送模拟数据"""
        counter = 0
        while self.running:
            try:
                # 模拟交易数据
                if counter % 10 == 0:  # 每10秒发送一次交易数据
                    mock_trade = {
                        "channel": "trades",
                        "data": {
                            "symbol": "BTC-PERP",
                            "price": 96000 + (counter % 100) * 10,
                            "size": 0.1,
                            "side": "buy" if counter % 2 == 0 else "sell",
                            "timestamp": int(time.time() * 1000)
                        }
                    }
                    if self.on_message_callback:
                        self.on_message_callback(mock_trade)
                
                # 模拟持仓更新
                if counter % 30 == 0:  # 每30秒发送一次持仓更新
                    mock_position = {
                        "channel": "positions",
                        "data": {
                            "symbol": "BTC-PERP",
                            "size": 1.5,
                            "unrealized_pnl": 2000 + (counter % 10) * 50,
                            "timestamp": int(time.time() * 1000)
                        }
                    }
                    if self.on_message_callback:
                        self.on_message_callback(mock_position)
                
                time.sleep(1)
                counter += 1
                
            except Exception as e:
                logger.error(f"发送模拟数据失败: {e}")
                break
    
    def subscribe_trades(self, symbol: Optional[str] = None):
        logger.info(f"订阅交易数据: {symbol or 'all'}")
    
    def subscribe_positions(self):
        logger.info("订阅持仓更新")
    
    def subscribe_orders(self):
        logger.info("订阅订单更新")
        
    def subscribe_account(self):
        logger.info("订阅账户更新")


def create_websocket_client(on_message_callback: Optional[Callable] = None, 
                          use_mock: bool = False) -> Any:
    """创建WebSocket客户端实例"""
    if use_mock:
        return MockWebSocketClient(on_message_callback)
    else:
        try:
            config.validate_config()
            return LighterWebSocketClient(on_message_callback)
        except ValueError as e:
            logger.warning(f"配置验证失败: {e}, 使用模拟WebSocket客户端")
            return MockWebSocketClient(on_message_callback)