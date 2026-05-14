#!/bin/bash
# IBM MQ Cluster Topology Generator - Linux/Mac Shell Script
# 快速執行分析並顯示結果

echo "============================================================"
echo "IBM MQ Cluster Topology Generator"
echo "============================================================"
echo ""

# 執行 Python 程式
python3 generate_mq_topology.py

echo ""
echo "============================================================"
echo "分析完成！"
echo "============================================================"
echo ""
echo "生成的檔案: mq_topology.md"
echo ""
echo "您可以使用以下命令檢視結果："
echo "  cat mq_topology.md"
echo "  或在支援 Markdown 的編輯器中開啟"
echo ""

# Made with Bob
