import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.console import Group
from rich.rule import Rule

from config import config


class LighterDisplay:
    """Lighter持仓监控显示界面"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.live = None
        self.last_update = None
        
        # 日志管理
        self.logs = deque(maxlen=1000)  # 最多保存1000条日志
        self.log_display_lines = 20     # 显示最近20行日志
        
        # WebSocket消息（用于状态显示）
        self.ws_messages = []
        self.max_ws_messages = 5
        
        # 设置布局
        self._setup_layout()
    
    def _setup_layout(self):
        """设置界面布局 - 上半部分监控数据，下半部分日志"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=3),      # 上半部分：监控数据
            Layout(name="logs", ratio=2)       # 下半部分：日志展示
        )
        
        # 上半部分分为左右两列
        self.layout["main"].split_row(
            Layout(name="portfolio", ratio=1),   # 左：投资组合
            Layout(name="positions", ratio=2)    # 右：持仓信息
        )
    
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
    
    def _get_level_color(self, level: str) -> str:
        """获取日志级别对应的颜色"""
        color_map = {
            'DEBUG': 'dim white',
            'INFO': 'blue',
            'SUCCESS': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold red'
        }
        return color_map.get(level.upper(), 'white')
    
    def _get_category_color(self, category: str) -> str:
        """获取日志分类对应的颜色"""
        color_map = {
            'SYSTEM': 'cyan',
            'API': 'blue',
            'WEBSOCKET': 'green',
            'TRADING': 'yellow',
            'ERROR': 'red',
            'DATA': 'magenta'
        }
        return color_map.get(category.upper(), 'white')
    
    def _create_header(self) -> Panel:
        """创建头部面板"""
        title = Text("🚀 Lighter交易所持仓监控系统", style="bold blue")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtitle = Text(f"最后更新: {timestamp}", style="dim")
        
        header_content = Align.center(
            Columns([title, subtitle], equal=True, expand=True)
        )
        
        return Panel(
            header_content,
            title="[bold]监控面板[/bold]",
            border_style="blue",
            box=box.ROUNDED
        )
    
    def _create_portfolio_panel(self, portfolio_data: Dict[str, Any]) -> Panel:
        """创建投资组合面板"""
        if not portfolio_data:
            return Panel(
                Align.center("暂无投资组合数据"),
                title="💼 投资组合",
                border_style="yellow"
            )
        
        total_equity = portfolio_data.get('total_equity', 0)
        unrealized_pnl = portfolio_data.get('unrealized_pnl', 0)
        
        # 确定PNL颜色
        pnl_color = "green" if unrealized_pnl >= 0 else "red"
        pnl_symbol = "+" if unrealized_pnl >= 0 else ""
        
        content = f"""
[bold]总权益:[/bold] [cyan]{total_equity:,.{config.DISPLAY_PRECISION}f}[/cyan] USDT

[bold]未实现盈亏:[/bold] [{pnl_color}]{pnl_symbol}{unrealized_pnl:,.{config.DISPLAY_PRECISION}f}[/{pnl_color}] USDT

[bold]盈亏率:[/bold] [{pnl_color}]{(unrealized_pnl/total_equity*100):+.2f}%[/{pnl_color}]

[dim]刷新间隔: {config.REFRESH_INTERVAL}秒[/dim]
        """.strip()
        
        return Panel(
            content,
            title="💼 投资组合",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def _create_positions_panel(self, positions_data: List[Dict[str, Any]]) -> Panel:
        """创建持仓面板"""
        if not positions_data:
            return Panel(
                Align.center("暂无持仓数据"),
                title="📊 持仓信息",
                border_style="yellow"
            )
        
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("合约", style="cyan", width=12)
        table.add_column("方向", justify="center", width=6)
        table.add_column("数量", justify="right", width=12)
        table.add_column("入场价", justify="right", width=12)
        table.add_column("标记价", justify="right", width=12)
        table.add_column("持仓价值", justify="right", width=15)
        table.add_column("未实现盈亏", justify="right", width=15)
        
        for position in positions_data:
            symbol = position.get('symbol', 'N/A')
            side = position.get('side', 'N/A')
            size = position.get('size', 0)
            entry_price = position.get('entry_price', 0)
            mark_price = position.get('mark_price', 0)
            position_value = position.get('position_value', 0)
            unrealized_pnl = position.get('unrealized_pnl', 0)
            
            # 方向颜色
            side_color = "green" if side == "long" else "red"
            side_display = "🟢 多" if side == "long" else "🔴 空"
            
            # PNL颜色
            pnl_color = "green" if unrealized_pnl >= 0 else "red"
            pnl_symbol = "+" if unrealized_pnl >= 0 else ""
            
            table.add_row(
                symbol,
                f"[{side_color}]{side_display}[/{side_color}]",
                f"{abs(size):.{config.DISPLAY_PRECISION}f}",
                f"{entry_price:,.{config.DISPLAY_PRECISION}f}",
                f"{mark_price:,.{config.DISPLAY_PRECISION}f}",
                f"{position_value:,.2f}",
                f"[{pnl_color}]{pnl_symbol}{unrealized_pnl:,.2f}[/{pnl_color}]"
            )
        
        return Panel(
            table,
            title="📊 持仓信息",
            border_style="magenta",
            box=box.ROUNDED
        )
    
    def _create_logs_panel(self) -> Panel:
        """创建日志面板"""
        if not self.logs:
            content = Text("暂无日志信息", style="dim")
        else:
            log_lines = []
            
            # 获取最近的日志条目
            recent_logs = list(self.logs)[-self.log_display_lines:]
            
            for log in recent_logs:
                timestamp_str = log['timestamp'].strftime("%H:%M:%S")
                level = log['level']
                category = log['category']
                message = log['message']
                
                level_color = self._get_level_color(level)
                category_color = self._get_category_color(category)
                
                # 格式化日志行
                log_line = Text()
                log_line.append(f"[{timestamp_str}] ", style="dim")
                log_line.append(f"{level:<8}", style=level_color)
                log_line.append(f"[{category}] ", style=category_color)
                log_line.append(message)
                
                log_lines.append(log_line)
            
            content = Group(*log_lines)
        
        # 添加状态信息
        api_status_text = "🟢 API已连接" if hasattr(self, '_api_status') and self._api_status else "🔴 API未连接"
        ws_status_text = "🟢 WS已连接" if hasattr(self, '_ws_status') and self._ws_status else "🔴 WS未连接"
        
        status_line = Text()
        status_line.append(f"{api_status_text} | {ws_status_text} | ", style="dim")
        status_line.append(f"日志条数: {len(self.logs)}", style="cyan")
        
        if isinstance(content, Text) and content.plain == "暂无日志信息":
            panel_content = content
        else:
            panel_content = Group(
                content,
                Rule(style="dim"),
                status_line
            )
        
        return Panel(
            panel_content,
            title="📋 系统日志 (实时滚动)",
            border_style="green",
            box=box.ROUNDED
        )
    
    def update_display(self, portfolio_data: Dict[str, Any], 
                      positions_data: List[Dict[str, Any]], 
                      api_status: bool = True, 
                      ws_status: bool = True):
        """更新显示内容"""
        self.last_update = time.time()
        self._api_status = api_status
        self._ws_status = ws_status
        
        # 更新各个面板
        self.layout["header"].update(self._create_header())
        self.layout["portfolio"].update(self._create_portfolio_panel(portfolio_data))
        self.layout["positions"].update(self._create_positions_panel(positions_data))
        self.layout["logs"].update(self._create_logs_panel())
    
    def add_websocket_message(self, message: Dict[str, Any]):
        """添加WebSocket消息并记录到日志"""
        message['timestamp'] = time.time()
        self.ws_messages.append(message)
        
        # 保持消息数量在限制内
        if len(self.ws_messages) > self.max_ws_messages * 2:
            self.ws_messages = self.ws_messages[-self.max_ws_messages:]
        
        # 添加到日志
        channel = message.get('channel', 'unknown')
        data_preview = str(message.get('data', {}))[:100]
        self.add_log("INFO", f"收到{channel}消息: {data_preview}", "WEBSOCKET")
    
    def start_live_display(self):
        """启动实时显示"""
        if self.live is None:
            self.live = Live(
                self.layout,
                console=self.console,
                refresh_per_second=2,  # 提高刷新率以便更好地显示日志滚动
                screen=True
            )
        return self.live
    
    def stop_live_display(self):
        """停止实时显示"""
        if self.live:
            self.live.stop()
            self.live = None
    
    def show_error(self, error_message: str):
        """显示错误信息"""
        self.add_log("ERROR", error_message, "SYSTEM")
        error_panel = Panel(
            f"[red]错误: {error_message}[/red]",
            title="❌ 系统错误",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def show_loading(self, message: str = "正在加载数据..."):
        """显示加载状态"""
        self.add_log("INFO", message, "SYSTEM")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(message, total=None)
            time.sleep(2)  # 模拟加载时间
    
    def print_startup_info(self):
        """打印启动信息"""
        startup_panel = Panel(
            """
[bold cyan]🚀 Lighter持仓监控系统[/bold cyan]

[yellow]功能特点:[/yellow]
• 实时显示总权益和未实现盈亏
• 多持仓信息监控
• WebSocket实时交易数据
• 自动刷新(每分钟一次)
• 实时日志滚动显示

[green]使用说明:[/green]
• 请确保已配置API密钥
• 按 Ctrl+C 可退出程序
• 数据每分钟自动刷新一次
• 下方日志区域实时显示系统状态

[dim]开始监控...[/dim]
            """.strip(),
            title="系统启动",
            border_style="blue",
            box=box.DOUBLE
        )
        self.console.print(startup_panel)
        
        # 添加启动日志
        self.add_log("SUCCESS", "Lighter监控系统启动成功", "SYSTEM")
        self.add_log("INFO", f"刷新间隔: {config.REFRESH_INTERVAL}秒", "SYSTEM")
        self.add_log("INFO", f"显示精度: {config.DISPLAY_PRECISION}位小数", "SYSTEM")