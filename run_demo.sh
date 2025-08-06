#!/bin/bash

echo "🚀 Lighter交易所持仓监控系统"
echo "================================"
echo ""
echo "选择运行模式："
echo "1. 演示模式 (无需依赖，立即运行)"
echo "2. 完整模式 (需要安装依赖包)"
echo "3. 查看项目结构"
echo ""
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo "启动演示模式..."
        python3 demo.py
        ;;
    2)
        echo "检查依赖..."
        if command -v pip &> /dev/null; then
            echo "安装依赖包..."
            pip install -r requirements.txt
            echo "启动完整监控程序..."
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
        echo "• main.py - 主程序（需要依赖包）"
        echo "• demo.py - 演示程序（无需依赖）"
        echo "• config.py - 配置管理"
        echo "• lighter_api.py - API客户端"
        echo "• websocket_client.py - WebSocket客户端"
        echo "• display.py - Rich界面显示"
        echo "• requirements.txt - 依赖包列表"
        echo "• .env.example - 环境变量示例"
        echo "• README.md - 详细说明文档"
        ;;
    *)
        echo "无效选择"
        ;;
esac