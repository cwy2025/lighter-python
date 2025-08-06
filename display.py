import time
from datetime import datetime
from typing import Dict, List, Any, Optional

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

from config import config


class LighterDisplay:
    """Lighter持仓监控显示界面"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.live = None
        self.last_update = None
        self.ws_messages = []
        self.max_ws_messages = 10
        
        # 设置布局
        self._setup_layout()
    
    def _setup_layout(self):
        """设置界面布局"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=5)
        )
        
        self.layout["main"].split_row(
            Layout(name="portfolio", ratio=1),
            Layout(name="positions", ratio=2)
        )
        
        self.layout["footer"].split_row(
            Layout(name="websocket", ratio=1),
            Layout(name="status", ratio=1)
        )
    
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
    
    def _create_websocket_panel(self) -> Panel:
        """创建WebSocket消息面板"""
        if not self.ws_messages:
            content = "[dim]暂无实时消息[/dim]"
        else:
            messages = []
            for msg in self.ws_messages[-self.max_ws_messages:]:
                timestamp = datetime.fromtimestamp(msg['timestamp']).strftime("%H:%M:%S")
                channel = msg.get('channel', 'unknown')
                content_preview = str(msg.get('data', {}))[:50] + "..." if len(str(msg.get('data', {}))) > 50 else str(msg.get('data', {}))
                messages.append(f"[dim]{timestamp}[/dim] [{self._get_channel_color(channel)}]{channel}[/{self._get_channel_color(channel)}]: {content_preview}")
            
            content = "\n".join(messages)
        
        return Panel(
            content,
            title="📡 实时消息",
            border_style="green",
            box=box.ROUNDED
        )
    
    def _get_channel_color(self, channel: str) -> str:
        """获取频道颜色"""
        color_map = {
            'trades': 'yellow',
            'positions': 'cyan', 
            'orders': 'magenta',
            'account': 'blue'
        }
        return color_map.get(channel, 'white')
    
    def _create_status_panel(self, api_status: bool, ws_status: bool) -> Panel:
        """创建状态面板"""
        api_indicator = "🟢 已连接" if api_status else "🔴 未连接"
        ws_indicator = "🟢 已连接" if ws_status else "🔴 未连接"
        
        refresh_interval = config.REFRESH_INTERVAL
        
        content = f"""
[bold]API状态:[/bold] {api_indicator}
[bold]WebSocket状态:[/bold] {ws_indicator}
[bold]刷新间隔:[/bold] {refresh_interval}秒
[bold]消息数量:[/bold] {len(self.ws_messages)}
        """.strip()
        
        return Panel(
            content,
            title="⚡ 状态信息",
            border_style="blue",
            box=box.ROUNDED
        )
    
    def _create_footer(self) -> Panel:
        """创建底部面板"""
        content = Text.from_markup(
            "[dim]按 Ctrl+C 退出 | 数据来源: Lighter交易所 | 刷新频率: 每分钟一次[/dim]"
        )
        
        return Panel(
            Align.center(content),
            border_style="dim blue",
            box=box.SIMPLE
        )
    
    def update_display(self, portfolio_data: Dict[str, Any], 
                      positions_data: List[Dict[str, Any]], 
                      api_status: bool = True, 
                      ws_status: bool = True):
        """更新显示内容"""
        self.last_update = time.time()
        
        # 更新各个面板
        self.layout["header"].update(self._create_header())
        self.layout["portfolio"].update(self._create_portfolio_panel(portfolio_data))
        self.layout["positions"].update(self._create_positions_panel(positions_data))
        self.layout["websocket"].update(self._create_websocket_panel())
        self.layout["status"].update(self._create_status_panel(api_status, ws_status))
        # self.layout["footer"].update(self._create_footer())
    
    def add_websocket_message(self, message: Dict[str, Any]):
        """添加WebSocket消息"""
        message['timestamp'] = time.time()
        self.ws_messages.append(message)
        
        # 保持消息数量在限制内
        if len(self.ws_messages) > self.max_ws_messages * 2:
            self.ws_messages = self.ws_messages[-self.max_ws_messages:]
    
    def start_live_display(self):
        """启动实时显示"""
        if self.live is None:
            self.live = Live(
                self.layout,
                console=self.console,
                refresh_per_second=1,
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
        error_panel = Panel(
            f"[red]错误: {error_message}[/red]",
            title="❌ 系统错误",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def show_loading(self, message: str = "正在加载数据..."):
        """显示加载状态"""
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

[green]使用说明:[/green]
• 请确保已配置API密钥
• 按 Ctrl+C 可退出程序
• 数据每分钟自动刷新一次

[dim]开始监控...[/dim]
            """.strip(),
            title="系统启动",
            border_style="blue",
            box=box.DOUBLE
        )
        self.console.print(startup_panel)