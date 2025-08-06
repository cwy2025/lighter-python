# 🚀 Lighter交易所持仓监控系统

一个基于Python的Lighter交易所持仓监控程序，具备Rich界面、WebSocket实时数据订阅和实时日志滚动功能。

![监控界面预览](preview.png)

## ✨ 功能特点

- 🚀 **实时监控**：每分钟自动刷新持仓数据
- 💼 **投资组合**：显示总权益、未实现盈亏等关键指标
- 📊 **持仓详情**：多持仓信息展示，包含合约、方向、数量、价格等
- 📡 **实时数据**：WebSocket订阅交易回报和持仓更新
- 🎨 **美观界面**：基于Rich库的现代化终端界面
- 📋 **日志滚动**：下半部分实时滚动显示系统日志，支持多级别、多分类日志
- 🔄 **自动重连**：网络断开自动重连机制
- 🛡️ **错误处理**：完善的错误处理和日志记录
- ⚡ **异步API**：使用Lighter官方异步API客户端，性能更佳
- 🧪 **测试网络**：支持主网和测试网络切换
- 🎯 **账户管理**：支持多账户ID配置

## 📋 系统要求

- Python 3.8+
- Linux/macOS/Windows
- 网络连接

## 🔧 安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd lighter-monitor
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的API密钥和设置：

```env
# API配置
LIGHTER_API_KEY=your_api_key_here
LIGHTER_API_SECRET=your_api_secret_here
LIGHTER_ACCOUNT_ID=1

# 网络选择
LIGHTER_USE_TESTNET=false
LIGHTER_BASE_URL=https://mainnet.zklighter.elliot.ai
LIGHTER_TESTNET_URL=https://testnet.zklighter.elliot.ai

# 监控配置
REFRESH_INTERVAL=60
```

## 🚀 使用方法

### 快速演示

想要立即体验？使用交互式脚本：

```bash
chmod +x run_demo.sh
./run_demo.sh
```

选择演示模式，无需任何配置即可查看完整功能！

### 程序启动

#### 模拟模式（推荐开始）
```bash
python3 main.py --mock
```

#### 实际模式
```bash
python3 main.py
```

#### 使用测试网络
```bash
python3 main.py --testnet
```

#### 指定账户ID
```bash
python3 main.py --account-id 12345
```

#### 组合参数
```bash
python3 main.py --testnet --account-id 12345
```

### 可用参数

| 参数 | 说明 |
|------|------|
| `--mock` | 使用模拟数据模式，无需真实API |
| `--testnet` | 使用测试网络 |
| `--account-id` | 指定账户ID |
| `--config` | 指定配置文件路径 |

## 🖥️ 界面说明

监控界面分为两个主要部分：

### 上半部分：核心监控数据
- **投资组合面板**：显示总权益、未实现盈亏、盈亏率等
- **持仓面板**：显示所有持仓的详细信息，包括合约、方向、数量、价格、盈亏等

### 下半部分：实时日志滚动
- **多级别日志**：DEBUG、INFO、SUCCESS、WARNING、ERROR、CRITICAL
- **多分类日志**：SYSTEM、API、WEBSOCKET、DATA、TRADING
- **实时滚动**：最新日志实时显示，历史日志自动滚动
- **颜色编码**：不同级别和分类使用不同颜色和图标

## 📋 日志功能详情

### 日志级别
- 🔍 **DEBUG** - 调试信息（数据刷新、连接检查等）
- ℹ️ **INFO** - 一般信息（价格变化、数据更新等）
- ✅ **SUCCESS** - 成功操作（连接建立、数据获取成功等）
- ⚠️ **WARNING** - 警告信息（连接断开、数据获取失败等）
- ❌ **ERROR** - 错误信息（API调用失败、解析错误等）
- 🚨 **CRITICAL** - 严重错误（系统初始化失败等）

### 日志分类
- 🖥️ **SYSTEM** - 系统级操作（启动、停止、线程管理等）
- 🔗 **API** - API相关操作（请求、响应、连接状态等）
- 🔌 **WEBSOCKET** - WebSocket相关（连接、订阅、消息等）
- 📊 **DATA** - 数据相关（更新、变化、统计等）
- 💹 **TRADING** - 交易相关（成交、持仓变化、PNL变化等）

### 日志优势
- **实时监控**：即时查看系统运行状态
- **问题诊断**：快速定位API连接、数据获取等问题
- **性能分析**：观察数据刷新频率和响应时间
- **操作记录**：完整记录所有系统操作和数据变化

## 🗂️ 项目结构

```
lighter-monitor/
├── main.py              # 主程序入口
├── lighter_api.py       # Lighter异步API客户端
├── websocket_client.py  # WebSocket客户端
├── display.py           # Rich界面显示
├── config.py            # 配置管理
├── demo.py              # 演示版本（无依赖）
├── run_demo.sh          # 交互式启动脚本
├── requirements.txt     # 依赖包列表
├── .env.example         # 环境变量模板
└── README.md            # 项目文档
```

## ⚙️ 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LIGHTER_API_KEY` | API密钥 | 空 |
| `LIGHTER_API_SECRET` | API密钥 | 空 |
| `LIGHTER_ACCOUNT_ID` | 账户ID | 1 |
| `LIGHTER_USE_TESTNET` | 使用测试网络 | false |
| `LIGHTER_BASE_URL` | 主网API端点 | https://mainnet.zklighter.elliot.ai |
| `LIGHTER_TESTNET_URL` | 测试网API端点 | https://testnet.zklighter.elliot.ai |
| `REFRESH_INTERVAL` | 刷新间隔（秒） | 60 |
| `DISPLAY_PRECISION` | 显示精度 | 6 |
| `TIMEOUT` | 请求超时（秒） | 30 |

### API适配说明

本程序使用Lighter官方Python SDK：
- **异步架构**：基于`asyncio`和`aiohttp`，提供更好的性能
- **自动重试**：内置重试机制和错误处理
- **类型安全**：使用Pydantic进行数据验证
- **官方支持**：与Lighter API完全兼容

> **注意**：由于Lighter的API需要特定的认证方式，如果没有有效的API密钥，程序会自动切换到模拟模式进行演示。

## 🐛 故障排除

### 常见问题

1. **无法连接API**
   - 检查网络连接
   - 验证API密钥是否正确
   - 确认账户ID是否有效
   - 尝试使用`--testnet`参数

2. **依赖包安装失败**
   ```bash
   # 使用虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **界面显示异常**
   - 确保终端支持Unicode字符
   - 调整终端窗口大小
   - 检查终端颜色支持

4. **模拟模式运行**
   ```bash
   python3 main.py --mock
   ```

### 日志分析

通过观察实时日志，你可以：
- 📊 **监控数据流**：查看API调用频率和成功率
- 🔍 **诊断连接**：观察WebSocket连接状态
- 💹 **跟踪变化**：实时查看价格和PNL变化
- 🚨 **发现问题**：及时发现错误和警告

## 🔒 安全说明

- ✅ API密钥存储在本地`.env`文件中
- ✅ 不会向第三方服务发送任何密钥信息
- ✅ 支持只读API权限
- ✅ 可在测试网络上安全测试

## 📝 开发说明

### 扩展功能

你可以轻松扩展以下功能：
- 添加更多持仓指标
- 自定义告警规则
- 导出数据到文件
- 集成更多交易所

### 异步编程

程序大量使用异步编程：
```python
# API调用示例
async def get_positions():
    result = await account_api.account(by="index", value="1")
    return result.to_dict()
```

### 日志集成

添加自定义日志：
```python
# 在你的代码中
display.add_log("INFO", "自定义消息", "CUSTOM")
```

## 📄 许可证

MIT License

## 🎯 主要特性总结

✨ **实时监控** | 📊 **数据可视化** | 🔄 **自动刷新** | 📋 **日志滚动**
**WebSocket订阅** | **Rich界面** | **异步API** | **错误处理**
**模拟模式** | **多账户支持** | **测试网络** | **配置灵活**

---

💡 **提示**：首次使用建议先运行 `./run_demo.sh` 查看演示效果！


