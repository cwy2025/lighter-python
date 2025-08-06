#!/usr/bin/env python3
"""
Lighter交易所持仓监控程序
功能：
- 实时监控持仓数据
- 显示总权益、未实现盈亏等信息
- WebSocket订阅交易回报
- Rich界面展示
- 实时日志滚动显示
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
    
    def __init__(self, use_mock: bool = False, account_id: str = None):
        self.use_mock = use_mock
        self.account_id = account_id or config.ACCOUNT_ID
        self.api_client = None
        self.ws_client = None
        self.display = LighterDisplay()
        self.running = False
        self.last_portfolio_data = {}
        self.last_positions_data = []
        self.refresh_count = 0
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        self.display.add_log("WARNING", "收到退出信号，正在关闭程序...", "SYSTEM")
        self.stop()
        sys.exit(0)
    
    def _on_websocket_message(self, message: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            # 添加消息到显示队列（这会自动记录到日志）
            self.display.add_websocket_message(message)
            
            # 根据消息类型更新数据
            channel = message.get('channel', '')
            data = message.get('data', {})
            
            if channel == 'positions':
                # 更新持仓数据
                self._update_position_from_ws(data)
                self.display.add_log("SUCCESS", f"持仓数据已更新", "TRADING")
            elif channel == 'trades':
                # 处理交易数据
                self._handle_trade_message(data)
                symbol = data.get('symbol', 'N/A')
                price = data.get('price', 0)
                self.display.add_log("INFO", f"新交易: {symbol} @ {price}", "TRADING")
            elif channel == 'account':
                # 处理账户更新
                self._handle_account_message(data)
                self.display.add_log("SUCCESS", "账户数据已更新", "DATA")
                
        except Exception as e:
            self.display.add_log("ERROR", f"处理WebSocket消息失败: {e}", "WEBSOCKET")
    
    def _update_position_from_ws(self, position_data: Dict[str, Any]):
        """从WebSocket更新持仓数据"""
        symbol = position_data.get('symbol')
        if not symbol:
            return
        
        # 更新持仓列表中的对应数据
        for i, position in enumerate(self.last_positions_data):
            if position.get('symbol') == symbol:
                # 更新现有持仓
                old_pnl = position.get('unrealized_pnl', 0)
                new_pnl = position_data.get('unrealized_pnl', 0)
                
                self.last_positions_data[i].update(position_data)
                
                # 记录PNL变化
                if abs(new_pnl - old_pnl) > 0.01:  # 只有变化超过0.01时才记录
                    change = new_pnl - old_pnl
                    self.display.add_log("INFO", f"{symbol} PNL变化: {change:+.2f}", "TRADING")
                break
        else:
            # 添加新持仓
            self.last_positions_data.append(position_data)
            self.display.add_log("SUCCESS", f"新增持仓: {symbol}", "TRADING")
    
    def _handle_trade_message(self, trade_data: Dict[str, Any]):
        """处理交易消息"""
        # 可以在这里添加交易统计或通知逻辑
        pass
    
    def _handle_account_message(self, account_data: Dict[str, Any]):
        """处理账户消息"""
        # 更新账户数据
        if 'total_equity' in account_data:
            old_equity = self.last_portfolio_data.get('total_equity', 0)
            new_equity = account_data.get('total_equity', 0)
            
            self.last_portfolio_data.update(account_data)
            
            # 记录权益变化
            if abs(new_equity - old_equity) > 1.0:  # 变化超过1 USDT时记录
                change = new_equity - old_equity
                self.display.add_log("INFO", f"总权益变化: {change:+.2f} USDT", "DATA")
    
    def _fetch_data(self):
        """获取最新数据"""
        try:
            self.display.add_log("DEBUG", "开始获取API数据...", "API")
            
            # 获取投资组合数据
            portfolio_response = self.api_client.get_portfolio(self.account_id)
            if portfolio_response.get('success', False):
                old_pnl = self.last_portfolio_data.get('unrealized_pnl', 0)
                self.last_portfolio_data = portfolio_response.get('data', {})
                new_pnl = self.last_portfolio_data.get('unrealized_pnl', 0)
                
                # 记录PNL变化
                if abs(new_pnl - old_pnl) > 1.0:
                    change = new_pnl - old_pnl
                    self.display.add_log("INFO", f"投资组合PNL变化: {change:+.2f} USDT", "DATA")
                
                self.display.add_log("SUCCESS", "投资组合数据获取成功", "API")
            else:
                error_msg = portfolio_response.get('error', '未知错误')
                self.display.add_log("WARNING", f"投资组合数据获取失败: {error_msg}", "API")
            
            # 获取持仓数据
            positions_response = self.api_client.get_positions(self.account_id)
            if positions_response.get('success', False):
                self.last_positions_data = positions_response.get('data', [])
                self.display.add_log("SUCCESS", f"持仓数据获取成功 ({len(self.last_positions_data)}个持仓)", "API")
            else:
                error_msg = positions_response.get('error', '未知错误')
                self.display.add_log("WARNING", f"持仓数据获取失败: {error_msg}", "API")
            
            return True
            
        except Exception as e:
            self.display.add_log("ERROR", f"获取数据失败: {e}", "API")
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
                self.refresh_count += 1
                self.display.add_log("INFO", f"开始第{self.refresh_count}次数据刷新", "SYSTEM")
                
                # 获取最新数据
                success = self._fetch_data()
                
                if success:
                    self.display.add_log("SUCCESS", f"第{self.refresh_count}次数据刷新完成", "SYSTEM")
                else:
                    self.display.add_log("WARNING", f"第{self.refresh_count}次数据刷新部分失败", "SYSTEM")
                
                # 等待刷新间隔
                self.display.add_log("DEBUG", f"等待{config.REFRESH_INTERVAL}秒后下次刷新", "SYSTEM")
                time.sleep(config.REFRESH_INTERVAL)
                
            except Exception as e:
                self.display.add_log("ERROR", f"数据刷新循环错误: {e}", "SYSTEM")
                time.sleep(10)  # 出错时等待10秒再重试
    
    def initialize(self):
        """初始化监控程序"""
        try:
            self.display.add_log("INFO", "正在初始化监控程序...", "SYSTEM")
            self.display.add_log("INFO", f"使用账户ID: {self.account_id}", "SYSTEM")
            self.display.add_log("INFO", f"API端点: {config.get_base_url()}", "SYSTEM")
            
            # 创建API客户端
            self.display.add_log("INFO", "创建API客户端...", "API")
            self.api_client = create_api_client(use_mock=self.use_mock, account_id=self.account_id)
            mode_text = "模拟模式" if self.use_mock else "实际模式"
            
            if hasattr(self.api_client, 'account_id'):
                self.display.add_log("SUCCESS", f"API客户端初始化成功 ({mode_text}, 账户ID: {self.api_client.account_id})", "API")
            else:
                self.display.add_log("SUCCESS", f"API客户端初始化成功 ({mode_text})", "API")
            
            # 创建WebSocket客户端
            self.display.add_log("INFO", "创建WebSocket客户端...", "WEBSOCKET")
            self.ws_client = create_websocket_client(
                on_message_callback=self._on_websocket_message,
                use_mock=self.use_mock
            )
            self.display.add_log("SUCCESS", "WebSocket客户端初始化成功", "WEBSOCKET")
            
            # 连接WebSocket
            self.display.add_log("INFO", "建立WebSocket连接...", "WEBSOCKET")
            self.ws_client.connect()
            time.sleep(2)  # 等待连接建立
            
            # 订阅频道
            self.display.add_log("INFO", "订阅WebSocket频道...", "WEBSOCKET")
            self.ws_client.subscribe_positions()
            self.display.add_log("SUCCESS", "订阅持仓频道成功", "WEBSOCKET")
            
            self.ws_client.subscribe_trades()
            self.display.add_log("SUCCESS", "订阅交易频道成功", "WEBSOCKET")
            
            self.ws_client.subscribe_account()
            self.display.add_log("SUCCESS", "订阅账户频道成功", "WEBSOCKET")
            
            # 获取初始数据
            self.display.add_log("INFO", "获取初始数据...", "DATA")
            success = self._fetch_data()
            if success:
                self.display.add_log("SUCCESS", "初始数据获取完成", "DATA")
            else:
                self.display.add_log("WARNING", "初始数据获取部分失败", "DATA")
            
            return True
            
        except Exception as e:
            self.display.add_log("CRITICAL", f"初始化失败: {e}", "SYSTEM")
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
        self.display.add_log("SUCCESS", "监控程序启动成功", "SYSTEM")
        
        # 启动数据刷新线程
        self.display.add_log("INFO", "启动数据刷新线程...", "SYSTEM")
        refresh_thread = threading.Thread(target=self._data_refresh_loop)
        refresh_thread.daemon = True
        refresh_thread.start()
        self.display.add_log("SUCCESS", "数据刷新线程已启动", "SYSTEM")
        
        # 启动实时显示
        try:
            self.display.add_log("INFO", "启动实时显示界面...", "SYSTEM")
            with self.display.start_live_display():
                self.display.add_log("SUCCESS", "实时显示界面已启动", "SYSTEM")
                
                display_update_count = 0
                while self.running:
                    # 更新显示
                    self._update_display()
                    
                    # 每30次更新记录一次（降低日志噪音）
                    display_update_count += 1
                    if display_update_count % 30 == 0:
                        self.display.add_log("DEBUG", f"界面已更新{display_update_count}次", "SYSTEM")
                    
                    time.sleep(1)  # 每秒更新一次显示
                    
        except KeyboardInterrupt:
            self.display.add_log("WARNING", "用户中断程序", "SYSTEM")
        except Exception as e:
            self.display.add_log("ERROR", f"显示循环错误: {e}", "SYSTEM")
        finally:
            self.stop()
    
    def stop(self):
        """停止监控"""
        self.display.add_log("INFO", "正在停止监控程序...", "SYSTEM")
        self.running = False
        
        # 断开WebSocket连接
        if self.ws_client:
            self.display.add_log("INFO", "断开WebSocket连接...", "WEBSOCKET")
            self.ws_client.disconnect()
            self.display.add_log("SUCCESS", "WebSocket连接已断开", "WEBSOCKET")
        
        # 关闭API客户端
        if self.api_client and hasattr(self.api_client, 'close'):
            self.display.add_log("INFO", "关闭API客户端...", "API")
            self.api_client.close()
            self.display.add_log("SUCCESS", "API客户端已关闭", "API")
        
        # 停止显示
        self.display.stop_live_display()
        
        self.display.add_log("SUCCESS", "监控程序已完全停止", "SYSTEM")
        print("✅ 监控程序已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lighter交易所持仓监控程序')
    parser.add_argument('--mock', action='store_true', 
                       help='使用模拟数据模式（用于演示）')
    parser.add_argument('--account-id', type=str, 
                       help='指定账户ID')
    parser.add_argument('--testnet', action='store_true',
                       help='使用测试网络')
    parser.add_argument('--config', type=str, 
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 设置网络
    if args.testnet:
        config.USE_TESTNET = True
        print("🧪 使用测试网络")
    
    # 检查是否需要使用模拟模式
    use_mock = args.mock
    if not use_mock:
        try:
            config.validate_config()
            if not config.is_authenticated():
                print("⚠️  未配置API密钥，将尝试访问公开数据")
        except ValueError as e:
            print(f"⚠️  配置验证失败: {e}")
            print("🔄 切换到模拟数据模式进行演示")
            use_mock = True
    
    # 创建并启动监控程序
    monitor = LighterMonitor(use_mock=use_mock, account_id=args.account_id)
    
    try:
        monitor.start()
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()