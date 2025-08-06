# Lighter交易所持仓监控系统

一个使用Python和Rich库开发的Lighter交易所持仓监控程序，提供实时的持仓数据展示和WebSocket交易回报功能。

## 功能特点

- 🚀 **实时监控**：每分钟自动刷新持仓数据
- 💼 **投资组合**：显示总权益、未实现盈亏等关键指标
- 📊 **持仓详情**：多持仓信息展示，包含合约、方向、数量、价格等
- 📡 **实时数据**：WebSocket订阅交易回报和持仓更新
- 🎨 **美观界面**：基于Rich库的现代化终端界面
- 🔄 **自动重连**：网络断开自动重连机制
- 🛡️ **错误处理**：完善的错误处理和日志记录

## 系统要求

- Python 3.8+
- Linux/macOS/Windows
- 终端支持颜色显示

## 安装

1. 克隆或下载项目文件
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 配置

1. 复制环境变量示例文件：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的Lighter API凭证：

```env
LIGHTER_API_KEY=your_api_key_here
LIGHTER_API_SECRET=your_api_secret_here
```

### 配置说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LIGHTER_API_KEY` | Lighter API密钥 | 必填 |
| `LIGHTER_API_SECRET` | Lighter API密钥密码 | 必填 |
| `LIGHTER_BASE_URL` | REST API端点 | https://api.lighter.xyz |
| `LIGHTER_WS_URL` | WebSocket端点 | wss://ws.lighter.xyz |
| `REFRESH_INTERVAL` | 数据刷新间隔（秒） | 60 |
| `DISPLAY_PRECISION` | 数值显示精度 | 6 |

## 使用方法

### 正常模式（需要API密钥）

```bash
python main.py
```

### 演示模式（使用模拟数据）

```bash
python main.py --mock
```

### 命令行参数

- `--mock`: 使用模拟数据模式，无需API密钥
- `--config PATH`: 指定配置文件路径

## 界面说明

监控界面分为以下几个部分：

### 📊 投资组合面板
- **总权益**：账户总资产价值
- **未实现盈亏**：当前持仓的浮动盈亏
- **盈亏率**：盈亏占总权益的百分比

### 📈 持仓信息面板
- **合约**：交易对名称
- **方向**：多头(🟢)或空头(🔴)
- **数量**：持仓数量
- **入场价**：开仓平均价格
- **标记价**：当前标记价格
- **持仓价值**：当前持仓总价值
- **未实现盈亏**：该持仓的浮动盈亏

### 📡 实时消息面板
显示最近的WebSocket消息，包括：
- 交易数据更新
- 持仓变化
- 账户更新

### ⚡ 状态信息面板
- **API状态**：REST API连接状态
- **WebSocket状态**：WebSocket连接状态
- **刷新间隔**：数据刷新频率
- **消息数量**：收到的实时消息数

## API适配说明

本程序是基于通用交易所API模式设计的框架。如需适配Lighter的具体API，请按以下步骤调整：

### 1. 更新API端点

在 `lighter_api.py` 中修改API端点URL：

```python
def get_positions(self):
    return self._make_request('GET', '/api/v1/positions')  # 修改为实际端点
```

### 2. 调整签名算法

在 `_generate_signature` 方法中实现Lighter的具体签名算法：

```python
def _generate_signature(self, timestamp: int, method: str, path: str, body: str = '') -> str:
    # 根据Lighter文档实现具体的签名算法
    pass
```

### 3. 适配WebSocket协议

在 `websocket_client.py` 中调整WebSocket消息格式：

```python
def _authenticate(self):
    # 根据Lighter WebSocket认证协议调整
    pass
```

### 4. 数据格式适配

根据Lighter API返回的实际数据格式，调整数据解析逻辑。

## 项目结构

```
lighter-monitor/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── lighter_api.py       # REST API客户端
├── websocket_client.py  # WebSocket客户端
├── display.py           # Rich界面显示
├── requirements.txt     # 依赖包列表
├── .env.example        # 环境变量示例
└── README.md           # 说明文档
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `.env` 文件中的API密钥是否正确
   - 确保API密钥有足够的权限

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 尝试使用 `--mock` 模式测试

3. **显示问题**
   - 确保终端支持颜色显示
   - 调整终端窗口大小
   - 检查终端是否支持UTF-8编码

### 日志输出

程序会输出详细的运行日志，包括：
- API请求状态
- WebSocket连接状态
- 数据更新情况
- 错误信息

## 开发说明

### 模块化设计

- `config.py`: 配置管理，支持环境变量
- `lighter_api.py`: REST API封装，包含认证和请求处理
- `websocket_client.py`: WebSocket客户端，支持自动重连
- `display.py`: Rich界面组件，模块化布局设计
- `main.py`: 主程序逻辑，集成所有模块

### 扩展功能

可以轻松扩展以下功能：
- 价格预警
- 交易记录导出
- 多账户监控
- 移动端推送通知

## 注意事项

- 本程序仅供监控使用，不包含交易功能
- 请妥善保管API密钥，不要泄露给他人
- 建议在正式使用前先使用模拟模式测试
- 根据Lighter的实际API文档调整相关配置

## 许可证

MIT License

## 支持

如有问题或建议，请创建Issue或联系开发者。


