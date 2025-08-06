#!/usr/bin/env python3
"""
Lighter交易所持仓监控程序
功能：
- 实时监控持仓数据
- 显示总权益、未实现盈亏等信息
- WebSocket订阅交易回报
- Rich界面展示
"""

import time
import signal
import sys
import threading
from typing import Dict, Any

from config import config
from lighter_api import create_api_client
from websocket_client import create_websocket_client
from display import LighterDisplay


class LighterMonitor:
    """Lighter持仓监控主程序"""
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.api_client = None
        self.ws_client = None
        self.display = LighterDisplay()
        self.running = False
        self.last_portfolio_data = {}
        self.last_positions_data = []
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        print("\n正在关闭监控程序...")
        self.stop()
        sys.exit(0)
    
    def _on_websocket_message(self, message: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            # 添加消息到显示队列
            self.display.add_websocket_message(message)
            
            # 根据消息类型更新数据
            channel = message.get('channel', '')
            data = message.get('data', {})
            
            if channel == 'positions':
                # 更新持仓数据
                self._update_position_from_ws(data)
            elif channel == 'trades':
                # 处理交易数据
                self._handle_trade_message(data)
            elif channel == 'account':
                # 处理账户更新
                self._handle_account_message(data)
                
        except Exception as e:
            print(f"处理WebSocket消息失败: {e}")
    
    def _update_position_from_ws(self, position_data: Dict[str, Any]):
        """从WebSocket更新持仓数据"""
        symbol = position_data.get('symbol')
        if not symbol:
            return
        
        # 更新持仓列表中的对应数据
        for i, position in enumerate(self.last_positions_data):
            if position.get('symbol') == symbol:
                # 更新现有持仓
                self.last_positions_data[i].update(position_data)
                break
        else:
            # 添加新持仓
            self.last_positions_data.append(position_data)
    
    def _handle_trade_message(self, trade_data: Dict[str, Any]):
        """处理交易消息"""
        # 可以在这里添加交易统计或通知逻辑
        pass
    
    def _handle_account_message(self, account_data: Dict[str, Any]):
        """处理账户消息"""
        # 更新账户数据
        if 'total_equity' in account_data:
            self.last_portfolio_data.update(account_data)
    
    def _fetch_data(self):
        """获取最新数据"""
        try:
            # 获取投资组合数据
            portfolio_response = self.api_client.get_portfolio()
            if portfolio_response.get('success', False):
                self.last_portfolio_data = portfolio_response.get('data', {})
            
            # 获取持仓数据
            positions_response = self.api_client.get_positions()
            if positions_response.get('success', False):
                self.last_positions_data = positions_response.get('data', [])
            
            return True
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            return False
    
    def _update_display(self):
        """更新显示界面"""
        api_status = self.api_client.health_check() if hasattr(self.api_client, 'health_check') else True
        ws_status = self.ws_client.is_connected if hasattr(self.ws_client, 'is_connected') else True
        
        self.display.update_display(
            portfolio_data=self.last_portfolio_data,
            positions_data=self.last_positions_data,
            api_status=api_status,
            ws_status=ws_status
        )
    
    def _data_refresh_loop(self):
        """数据刷新循环"""
        while self.running:
            try:
                # 获取最新数据
                self._fetch_data()
                
                # 等待刷新间隔
                time.sleep(config.REFRESH_INTERVAL)
                
            except Exception as e:
                print(f"数据刷新循环错误: {e}")
                time.sleep(10)  # 出错时等待10秒再重试
    
    def initialize(self):
        """初始化监控程序"""
        try:
            # 创建API客户端
            self.api_client = create_api_client(use_mock=self.use_mock)
            print("✅ API客户端初始化成功")
            
            # 创建WebSocket客户端
            self.ws_client = create_websocket_client(
                on_message_callback=self._on_websocket_message,
                use_mock=self.use_mock
            )
            print("✅ WebSocket客户端初始化成功")
            
            # 连接WebSocket
            self.ws_client.connect()
            time.sleep(2)  # 等待连接建立
            
            # 订阅频道
            self.ws_client.subscribe_positions()
            self.ws_client.subscribe_trades()
            self.ws_client.subscribe_account()
            print("✅ WebSocket频道订阅成功")
            
            # 获取初始数据
            print("📊 获取初始数据...")
            self._fetch_data()
            print("✅ 初始数据获取完成")
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def start(self):
        """启动监控"""
        # 打印启动信息
        self.display.print_startup_info()
        
        # 初始化
        if not self.initialize():
            self.display.show_error("系统初始化失败")
            return
        
        self.running = True
        
        # 启动数据刷新线程
        refresh_thread = threading.Thread(target=self._data_refresh_loop)
        refresh_thread.daemon = True
        refresh_thread.start()
        
        # 启动实时显示
        try:
            with self.display.start_live_display():
                while self.running:
                    # 更新显示
                    self._update_display()
                    time.sleep(1)  # 每秒更新一次显示
                    
        except KeyboardInterrupt:
            print("\n用户中断程序")
        except Exception as e:
            self.display.show_error(f"显示循环错误: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止监控"""
        self.running = False
        
        # 断开WebSocket连接
        if self.ws_client:
            self.ws_client.disconnect()
        
        # 停止显示
        self.display.stop_live_display()
        
        print("✅ 监控程序已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lighter交易所持仓监控程序')
    parser.add_argument('--mock', action='store_true', 
                       help='使用模拟数据模式（用于演示）')
    parser.add_argument('--config', type=str, 
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 检查是否需要使用模拟模式
    use_mock = args.mock
    if not use_mock:
        try:
            config.validate_config()
        except ValueError as e:
            print(f"⚠️  配置验证失败: {e}")
            print("🔄 切换到模拟数据模式进行演示")
            use_mock = True
    
    # 创建并启动监控程序
    monitor = LighterMonitor(use_mock=use_mock)
    
    try:
        monitor.start()
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()