#!/bin/bash

echo "🚀 Lighter交易所持仓监控系统"
echo "================================"
echo ""
echo "✨ 新特性：实时日志滚动显示！"
echo ""
echo "选择运行模式："
echo "1. 演示模式 (无需依赖，立即运行，含日志滚动)"
echo "2. 完整模式 (需要安装依赖包，Rich界面)"
echo "3. 查看项目结构"
echo "4. 查看功能特点"
echo ""
read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📋 启动演示模式 (含实时日志滚动)..."
        echo "界面说明："
        echo "• 上半部分：投资组合 + 持仓信息"
        echo "• 下半部分：实时滚动日志 (6个级别，6个分类)"
        echo "• 彩色图标：🔍DEBUG ℹ️INFO ✅SUCCESS ⚠️WARNING ❌ERROR 🚨CRITICAL"
        echo "• 日志分类：🖥️SYSTEM 🌐API 🔌WEBSOCKET 💹TRADING 📊DATA"
        echo ""
        echo "按 Ctrl+C 可退出..."
        sleep 3
        python3 demo.py
        ;;
    2)
        echo "检查依赖..."
        if command -v pip &> /dev/null; then
            echo "安装依赖包..."
            pip install -r requirements.txt
            echo ""
            echo "🎨 启动完整Rich界面监控程序..."
            echo "界面特点："
            echo "• 基于Rich库的现代化界面"
            echo "• 实时日志滚动区域"
            echo "• 美观的表格和面板设计"
            echo "• 支持颜色和样式渲染"
            echo ""
            python3 main.py --mock
        else
            echo "❌ 未找到pip，请先安装Python包管理器"
        fi
        ;;
    3)
        echo "项目结构："
        echo ""
        ls -la
        echo ""
        echo "主要文件说明："
        echo "• main.py - 主程序（Rich界面，需要依赖包）"
        echo "• demo.py - 演示程序（无需依赖，含日志滚动）"
        echo "• config.py - 配置管理"
        echo "• lighter_api.py - API客户端"
        echo "• websocket_client.py - WebSocket客户端"
        echo "• display.py - Rich界面显示（含日志组件）"
        echo "• requirements.txt - 依赖包列表"
        echo "• .env.example - 环境变量示例"
        echo "• README.md - 详细说明文档"
        ;;
    4)
        echo ""
        echo "🎯 Lighter持仓监控系统 - 功能特点"
        echo "================================================"
        echo ""
        echo "📊 核心功能："
        echo "• 🚀 实时监控 - 每分钟自动刷新持仓数据"
        echo "• 💼 投资组合 - 总权益、未实现盈亏、盈亏率"
        echo "• 📈 持仓详情 - 合约、方向、价格、盈亏信息"
        echo "• 📡 实时数据 - WebSocket订阅交易回报"
        echo ""
        echo "📋 日志系统 (重点新功能)："
        echo "• 实时滚动显示最新日志"
        echo "• 6个日志级别：DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL"
        echo "• 6个分类：SYSTEM, API, WEBSOCKET, TRADING, DATA, ERROR"
        echo "• 彩色图标和文字区分"
        echo "• 支持1000条历史记录"
        echo "• 自动清理和内存管理"
        echo ""
        echo "🎨 界面特色："
        echo "• 基于Rich库的现代化终端界面"
        echo "• 分层布局：上半部监控数据，下半部日志"
        echo "• 美观的表格、面板和颜色方案"
        echo "• 实时状态显示"
        echo ""
        echo "🔧 技术特点："
        echo "• 模块化设计，易于扩展"
        echo "• 自动重连机制"
        echo "• 完善的错误处理"
        echo "• 支持模拟模式演示"
        echo "• 配置灵活，适应不同环境"
        echo ""
        ;;
    *)
        echo "无效选择"
        ;;
esac