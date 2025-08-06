# Lighter交易所持仓监控系统

一个使用Python和Rich库开发的Lighter交易所持仓监控程序，提供实时的持仓数据展示、WebSocket交易回报和**实时日志滚动**功能。

## 功能特点

- 🚀 **实时监控**：每分钟自动刷新持仓数据
- 💼 **投资组合**：显示总权益、未实现盈亏等关键指标
- 📊 **持仓详情**：多持仓信息展示，包含合约、方向、数量、价格等
- 📡 **实时数据**：WebSocket订阅交易回报和持仓更新
- 🎨 **美观界面**：基于Rich库的现代化终端界面
- 📋 **日志滚动**：下半部分实时滚动显示系统日志，支持多级别、多分类日志
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

### 快速演示（无需依赖）

```bash
# 直接运行演示版本，无需安装任何依赖包
python3 demo.py
```

### 交互式启动

```bash
./run_demo.sh
```

### 命令行参数

- `--mock`: 使用模拟数据模式，无需API密钥
- `--config PATH`: 指定配置文件路径

## 界面说明

监控界面采用分层布局设计：

### 📊 上半部分：核心监控数据

#### 左侧：投资组合面板
- **总权益**：账户总资产价值
- **未实现盈亏**：当前持仓的浮动盈亏
- **盈亏率**：盈亏占总权益的百分比
- **刷新间隔**：数据刷新频率显示

#### 右侧：持仓信息面板
- **合约**：交易对名称
- **方向**：多头(🟢)或空头(🔴)
- **数量**：持仓数量
- **入场价**：开仓平均价格
- **标记价**：当前标记价格
- **未实现盈亏**：该持仓的浮动盈亏

### 📋 下半部分：实时日志滚动区域

**日志级别**：
- 🔍 **DEBUG**：调试信息
- ℹ️ **INFO**：一般信息
- ✅ **SUCCESS**：成功操作
- ⚠️ **WARNING**：警告信息
- ❌ **ERROR**：错误信息
- 🚨 **CRITICAL**：严重错误

**日志分类**：
- 🖥️ **SYSTEM**：系统相关日志
- 🌐 **API**：API请求和响应
- 🔌 **WEBSOCKET**：WebSocket连接和消息
- 💹 **TRADING**：交易和持仓变化
- 📊 **DATA**：数据处理和更新

**功能特点**：
- 自动滚动显示最新日志（默认显示最近20条）
- 彩色图标和文字区分不同级别和分类
- 实时显示连接状态和日志统计
- 支持最多1000条日志历史记录

## 日志功能详解

### 日志监控内容

1. **系统状态**：启动、停止、初始化等系统级操作
2. **API交互**：数据获取、请求状态、连接健康检查
3. **WebSocket通信**：连接状态、消息接收、频道订阅
4. **交易活动**：价格变化、持仓更新、PNL变化
5. **数据处理**：数据刷新、计算结果、缓存操作

### 日志优势

- **实时监控**：即时了解系统运行状态
- **问题诊断**：快速定位API或连接问题
- **交易跟踪**：实时查看交易和持仓变化
- **性能监控**：观察数据刷新频率和响应时间
- **状态管理**：清晰了解各组件连接状态

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
├── main.py              # 主程序（完整功能，需要依赖包）
├── demo.py              # 演示程序（无需依赖，包含日志滚动）
├── config.py            # 配置管理
├── lighter_api.py       # REST API客户端
├── websocket_client.py  # WebSocket客户端
├── display.py           # Rich界面显示（含日志组件）
├── requirements.txt     # 依赖包列表
├── .env.example        # 环境变量示例
├── run_demo.sh         # 快速启动脚本
└── README.md           # 详细说明文档
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `.env` 文件中的API密钥是否正确
   - 确保API密钥有足够的权限
   - 查看日志区域的API错误信息

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 观察日志中的WebSocket连接状态
   - 尝试使用 `--mock` 模式测试

3. **显示问题**
   - 确保终端支持颜色显示
   - 调整终端窗口大小（建议至少100列宽）
   - 检查终端是否支持UTF-8编码

### 日志分析

程序会输出详细的运行日志，包括：
- **API请求状态**：成功/失败状态，响应时间
- **WebSocket连接状态**：连接建立、断开、重连
- **数据更新情况**：数据获取、处理、更新频率
- **错误信息**：详细的错误描述和分类
- **性能指标**：刷新次数、运行时间等

## 开发说明

### 模块化设计

- `config.py`: 配置管理，支持环境变量
- `lighter_api.py`: REST API封装，包含认证和请求处理
- `websocket_client.py`: WebSocket客户端，支持自动重连
- `display.py`: Rich界面组件，模块化布局设计，包含日志管理
- `main.py`: 主程序逻辑，集成所有模块

### 日志系统设计

- **deque数据结构**：高效的FIFO队列，自动限制历史记录数量
- **多级别分类**：支持6个级别和6个分类的日志
- **实时滚动**：自动显示最新日志，支持自定义显示行数
- **彩色显示**：不同级别和分类使用不同颜色和图标
- **性能优化**：批量更新，避免过多的终端重绘

### 扩展功能

可以轻松扩展以下功能：
- 价格预警（基于日志系统）
- 交易记录导出
- 日志文件保存
- 多账户监控
- 移动端推送通知
- 日志过滤和搜索

## 注意事项

- 本程序仅供监控使用，不包含交易功能
- 请妥善保管API密钥，不要泄露给他人
- 建议在正式使用前先使用模拟模式测试
- 根据Lighter的实际API文档调整相关配置
- 日志功能会增加少量内存使用，但设有自动清理机制

## 许可证

MIT License

## 支持

如有问题或建议，请创建Issue或联系开发者。

---

**🎯 重点特性：实时日志滚动让您清晰了解系统运行状态，实现真正的透明监控！**


