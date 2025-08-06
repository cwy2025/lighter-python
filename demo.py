#!/usr/bin/env python3
"""
Lighter交易所持仓监控程序 - 演示版本
无需额外依赖，直接运行展示基本功能
"""

import time
import threading
from datetime import datetime


class SimpleDisplay:
    """简化的显示界面"""
    
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
            ]
        }
        self.ws_messages = []
        
    def print_header(self):
        """打印头部信息"""
        print("=" * 80)
        print("🚀 Lighter交易所持仓监控系统 - 演示版本")
        print(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def print_portfolio(self):
        """打印投资组合信息"""
        data = self.mock_data
        total_equity = data['total_equity']
        unrealized_pnl = data['unrealized_pnl']
        pnl_rate = (unrealized_pnl / total_equity) * 100
        
        print("\n💼 投资组合")
        print("-" * 40)
        print(f"总权益:      {total_equity:,.2f} USDT")
        print(f"未实现盈亏:  {unrealized_pnl:+,.2f} USDT")
        print(f"盈亏率:      {pnl_rate:+.2f}%")
    
    def print_positions(self):
        """打印持仓信息"""
        positions = self.mock_data['positions']
        
        print("\n📊 持仓信息")
        print("-" * 80)
        print("合约        | 方向 | 数量      | 入场价    | 标记价    | 持仓价值     | 未实现盈亏")
        print("-" * 80)
        
        for pos in positions:
            symbol = pos['symbol']
            side_display = "多" if pos['side'] == 'long' else "空"
            size = abs(pos['size'])
            entry_price = pos['entry_price']
            mark_price = pos['mark_price']
            position_value = pos['position_value']
            unrealized_pnl = pos['unrealized_pnl']
            
            print(f"{symbol:<10} | {side_display:<2} | {size:8.3f} | {entry_price:8.0f} | {mark_price:8.0f} | {position_value:10.0f} | {unrealized_pnl:+9.0f}")
    
    def print_websocket_messages(self):
        """打印WebSocket消息"""
        print("\n📡 实时消息 (最近10条)")
        print("-" * 50)
        
        if not self.ws_messages:
            print("暂无实时消息")
        else:
            for msg in self.ws_messages[-10:]:
                timestamp = datetime.fromtimestamp(msg['timestamp']).strftime("%H:%M:%S")
                print(f"[{timestamp}] {msg['channel']}: {msg['content']}")
    
    def print_status(self):
        """打印状态信息"""
        print("\n⚡ 状态信息")
        print("-" * 30)
        print("API状态:      🟢 已连接")
        print("WebSocket状态: 🟢 已连接")
        print("刷新间隔:     60秒")
        print(f"消息数量:     {len(self.ws_messages)}")
    
    def add_mock_message(self, channel, content):
        """添加模拟消息"""
        message = {
            'timestamp': time.time(),
            'channel': channel,
            'content': content
        }
        self.ws_messages.append(message)
        
        # 保持消息数量限制
        if len(self.ws_messages) > 20:
            self.ws_messages = self.ws_messages[-20:]
    
    def update_mock_data(self):
        """更新模拟数据"""
        import random
        
        # 随机更新价格
        for pos in self.mock_data['positions']:
            # 模拟价格变动 ±1%
            change = random.uniform(-0.01, 0.01)
            pos['mark_price'] *= (1 + change)
            
            # 重新计算未实现盈亏
            if pos['side'] == 'long':
                pos['unrealized_pnl'] = pos['size'] * (pos['mark_price'] - pos['entry_price'])
                pos['position_value'] = pos['size'] * pos['mark_price']
            else:
                pos['unrealized_pnl'] = abs(pos['size']) * (pos['entry_price'] - pos['mark_price'])
                pos['position_value'] = pos['size'] * pos['mark_price']
        
        # 更新总盈亏
        total_pnl = sum(pos['unrealized_pnl'] for pos in self.mock_data['positions'])
        self.mock_data['unrealized_pnl'] = total_pnl
    
    def display(self):
        """显示完整界面"""
        # 清屏 (在支持的终端中)
        print("\033[2J\033[H", end="")
        
        self.print_header()
        self.print_portfolio()
        self.print_positions()
        self.print_websocket_messages()
        self.print_status()
        
        print("\n" + "=" * 80)
        print("按 Ctrl+C 退出程序")


class MockDataGenerator:
    """模拟数据生成器"""
    
    def __init__(self, display):
        self.display = display
        self.running = False
        self.counter = 0
    
    def start(self):
        """启动数据生成"""
        self.running = True
        thread = threading.Thread(target=self._generate_data)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """停止数据生成"""
        self.running = False
    
    def _generate_data(self):
        """生成模拟数据"""
        while self.running:
            try:
                # 每10秒生成一次交易消息
                if self.counter % 10 == 0:
                    self.display.add_mock_message(
                        "trades", 
                        f"BTC-PERP: 96{self.counter % 100:03d}, 0.1 BTC"
                    )
                
                # 每30秒生成一次持仓更新消息
                if self.counter % 30 == 0:
                    self.display.add_mock_message(
                        "positions",
                        "BTC-PERP 持仓更新"
                    )
                
                # 每60秒更新一次价格
                if self.counter % 60 == 0:
                    self.display.update_mock_data()
                    self.display.add_mock_message(
                        "account",
                        "账户数据更新"
                    )
                
                time.sleep(1)
                self.counter += 1
                
            except Exception as e:
                print(f"数据生成错误: {e}")
                break


def main():
    """主函数"""
    print("启动Lighter持仓监控演示程序...")
    
    # 创建显示器
    display = SimpleDisplay()
    
    # 创建数据生成器
    data_generator = MockDataGenerator(display)
    
    # 初始化一些模拟消息
    display.add_mock_message("system", "系统启动")
    display.add_mock_message("websocket", "WebSocket连接已建立")
    display.add_mock_message("trades", "订阅交易数据成功")
    display.add_mock_message("positions", "订阅持仓数据成功")
    
    # 启动数据生成
    data_generator.start()
    
    try:
        # 主循环 - 每5秒刷新一次显示
        while True:
            display.display()
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n程序退出中...")
        data_generator.stop()
        print("✅ 程序已退出")


if __name__ == "__main__":
    main()