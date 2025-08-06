#!/usr/bin/env python3
"""
Lighter交易所持仓监控程序 - 演示版本
无需额外依赖，直接运行展示基本功能（包括日志滚动）
"""

import time
import threading
from datetime import datetime
from collections import deque


class SimpleDisplay:
    """简化的显示界面（包含日志滚动）"""
    
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
        
        # 日志管理
        self.logs = deque(maxlen=500)  # 最多保存500条日志
        self.log_display_lines = 15    # 显示最近15行日志
        
    def add_log(self, level: str, message: str, category: str = "SYSTEM"):
        """添加日志"""
        timestamp = datetime.now()
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'category': category.upper(),
            'message': message
        }
        self.logs.append(log_entry)
    
    def get_level_symbol(self, level: str) -> str:
        """获取日志级别对应的符号"""
        symbol_map = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        return symbol_map.get(level.upper(), 'ℹ️')
    
    def get_category_symbol(self, category: str) -> str:
        """获取分类对应的符号"""
        symbol_map = {
            'SYSTEM': '🖥️',
            'API': '🌐',
            'WEBSOCKET': '🔌',
            'TRADING': '💹',
            'ERROR': '❌',
            'DATA': '📊'
        }
        return symbol_map.get(category.upper(), '📝')
        
    def print_header(self):
        """打印头部信息"""
        print("=" * 100)
        print("🚀 Lighter交易所持仓监控系统 - 演示版本 (含日志滚动)")
        print(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
    
    def print_portfolio(self):
        """打印投资组合信息"""
        data = self.mock_data
        total_equity = data['total_equity']
        unrealized_pnl = data['unrealized_pnl']
        pnl_rate = (unrealized_pnl / total_equity) * 100
        
        print("\n💼 投资组合                                    📊 持仓信息")
        print("-" * 50 + "  " + "-" * 47)
        print(f"总权益:      {total_equity:,.2f} USDT", end="")
        print("  " + "合约        | 方向 | 数量      | 入场价    | 标记价    | 未实现盈亏")
        print(f"未实现盈亏:  {unrealized_pnl:+,.2f} USDT", end="")
        print("  " + "-" * 47)
        print(f"盈亏率:      {pnl_rate:+.2f}%", end="")
        
        # 打印持仓信息（右侧）
        positions = self.mock_data['positions']
        for i, pos in enumerate(positions):
            symbol = pos['symbol']
            side_display = "多" if pos['side'] == 'long' else "空"
            size = abs(pos['size'])
            entry_price = pos['entry_price']
            mark_price = pos['mark_price']
            unrealized_pnl = pos['unrealized_pnl']
            
            if i == 0:
                print(f"  {symbol:<10} | {side_display:<2} | {size:8.3f} | {entry_price:8.0f} | {mark_price:8.0f} | {unrealized_pnl:+9.0f}")
            else:
                print(" " * 50 + f"  {symbol:<10} | {side_display:<2} | {size:8.3f} | {entry_price:8.0f} | {mark_price:8.0f} | {unrealized_pnl:+9.0f}")
        
        # 补充空行以对齐
        for i in range(len(positions), 3):
            if i == 0:
                print("")
            else:
                print(" " * 50 + "  ")
    
    def print_logs(self):
        """打印日志区域"""
        print("\n📋 系统日志 (实时滚动)")
        print("=" * 100)
        
        if not self.logs:
            print("暂无日志信息")
        else:
            # 获取最近的日志条目
            recent_logs = list(self.logs)[-self.log_display_lines:]
            
            for log in recent_logs:
                timestamp_str = log['timestamp'].strftime("%H:%M:%S")
                level = log['level']
                category = log['category']
                message = log['message']
                
                level_symbol = self.get_level_symbol(level)
                category_symbol = self.get_category_symbol(category)
                
                # 格式化日志行 (截断过长的消息)
                max_msg_len = 65
                if len(message) > max_msg_len:
                    message = message[:max_msg_len-3] + "..."
                
                print(f"[{timestamp_str}] {level_symbol} {level:<8} {category_symbol} [{category:<9}] {message}")
        
        # 状态信息
        print("-" * 100)
        print(f"🟢 API已连接 | 🟢 WebSocket已连接 | 📝 日志条数: {len(self.logs)} | 🔄 刷新间隔: 5秒")
    
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
        
        # 添加到日志
        self.add_log("INFO", f"收到{channel}消息: {content}", "WEBSOCKET")
    
    def update_mock_data(self):
        """更新模拟数据"""
        import random
        
        self.add_log("DEBUG", "开始更新模拟数据", "DATA")
        
        # 随机更新价格
        for pos in self.mock_data['positions']:
            old_mark_price = pos['mark_price']
            
            # 模拟价格变动 ±1%
            change = random.uniform(-0.01, 0.01)
            pos['mark_price'] *= (1 + change)
            
            # 重新计算未实现盈亏
            old_pnl = pos['unrealized_pnl']
            if pos['side'] == 'long':
                pos['unrealized_pnl'] = pos['size'] * (pos['mark_price'] - pos['entry_price'])
                pos['position_value'] = pos['size'] * pos['mark_price']
            else:
                pos['unrealized_pnl'] = abs(pos['size']) * (pos['entry_price'] - pos['mark_price'])
                pos['position_value'] = pos['size'] * pos['mark_price']
            
            # 记录价格变化
            price_change = pos['mark_price'] - old_mark_price
            pnl_change = pos['unrealized_pnl'] - old_pnl
            
            if abs(price_change) > 1:
                self.add_log("INFO", f"{pos['symbol']} 价格变化: {price_change:+.2f}", "TRADING")
            
            if abs(pnl_change) > 1:
                self.add_log("INFO", f"{pos['symbol']} PNL变化: {pnl_change:+.2f}", "TRADING")
        
        # 更新总盈亏
        old_total_pnl = self.mock_data['unrealized_pnl']
        total_pnl = sum(pos['unrealized_pnl'] for pos in self.mock_data['positions'])
        self.mock_data['unrealized_pnl'] = total_pnl
        
        total_change = total_pnl - old_total_pnl
        if abs(total_change) > 1:
            self.add_log("SUCCESS", f"总PNL变化: {total_change:+.2f} USDT", "DATA")
        
        self.add_log("SUCCESS", "模拟数据更新完成", "DATA")
    
    def display(self):
        """显示完整界面"""
        # 清屏 (在支持的终端中)
        print("\033[2J\033[H", end="")
        
        self.print_header()
        self.print_portfolio()
        self.print_logs()
        
        print("\n" + "=" * 100)
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
        self.display.add_log("SUCCESS", "模拟数据生成器启动", "SYSTEM")
        thread = threading.Thread(target=self._generate_data)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """停止数据生成"""
        self.running = False
        self.display.add_log("WARNING", "模拟数据生成器停止", "SYSTEM")
    
    def _generate_data(self):
        """生成模拟数据"""
        while self.running:
            try:
                # 每5秒生成一次交易消息
                if self.counter % 5 == 0:
                    import random
                    price = 96000 + random.randint(-1000, 1000)
                    size = round(random.uniform(0.01, 0.5), 3)
                    self.display.add_mock_message(
                        "trades", 
                        f"BTC-PERP: {price}, {size} BTC"
                    )
                
                # 每15秒生成一次持仓更新消息
                if self.counter % 15 == 0:
                    self.display.add_mock_message(
                        "positions",
                        "持仓数据实时更新"
                    )
                
                # 每30秒更新一次价格数据
                if self.counter % 30 == 0:
                    self.display.update_mock_data()
                    self.display.add_mock_message(
                        "account",
                        "账户数据已刷新"
                    )
                
                # 每60秒记录一次系统状态
                if self.counter % 60 == 0:
                    self.display.add_log("INFO", f"系统运行时间: {self.counter}秒", "SYSTEM")
                
                # 随机生成一些其他日志
                if self.counter % 20 == 0:
                    import random
                    messages = [
                        "API心跳检测正常",
                        "WebSocket连接稳定",
                        "数据同步完成",
                        "缓存更新成功"
                    ]
                    categories = ["API", "WEBSOCKET", "DATA", "SYSTEM"]
                    
                    msg = random.choice(messages)
                    cat = random.choice(categories)
                    self.display.add_log("SUCCESS", msg, cat)
                
                time.sleep(1)
                self.counter += 1
                
            except Exception as e:
                self.display.add_log("ERROR", f"数据生成错误: {e}", "ERROR")
                break


def main():
    """主函数"""
    print("启动Lighter持仓监控演示程序（含日志滚动）...")
    
    # 创建显示器
    display = SimpleDisplay()
    
    # 添加启动日志
    display.add_log("SUCCESS", "Lighter监控系统启动成功", "SYSTEM")
    display.add_log("INFO", "演示模式已激活", "SYSTEM")
    display.add_log("INFO", "初始化API客户端 (模拟模式)", "API")
    display.add_log("SUCCESS", "API客户端连接成功", "API")
    display.add_log("INFO", "建立WebSocket连接", "WEBSOCKET")
    display.add_log("SUCCESS", "WebSocket连接已建立", "WEBSOCKET")
    display.add_log("SUCCESS", "订阅交易数据频道", "WEBSOCKET")
    display.add_log("SUCCESS", "订阅持仓数据频道", "WEBSOCKET")
    display.add_log("SUCCESS", "订阅账户数据频道", "WEBSOCKET")
    display.add_log("INFO", "获取初始持仓数据", "DATA")
    display.add_log("SUCCESS", "初始数据加载完成", "DATA")
    
    # 创建数据生成器
    data_generator = MockDataGenerator(display)
    
    # 启动数据生成
    data_generator.start()
    
    try:
        display_count = 0
        # 主循环 - 每5秒刷新一次显示
        while True:
            display.display()
            
            display_count += 1
            if display_count % 6 == 0:  # 每30秒记录一次界面更新
                display.add_log("DEBUG", f"界面已刷新{display_count}次", "SYSTEM")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n程序退出中...")
        display.add_log("WARNING", "收到用户中断信号", "SYSTEM")
        display.add_log("INFO", "正在停止数据生成器", "SYSTEM")
        data_generator.stop()
        display.add_log("SUCCESS", "程序安全退出", "SYSTEM")
        print("✅ 程序已退出")


if __name__ == "__main__":
    main()