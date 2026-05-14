@echo off
REM IBM MQ Cluster Topology Generator - Windows 批次檔
REM 快速執行分析並開啟結果檔案

echo ============================================================
echo IBM MQ Cluster Topology Generator
echo ============================================================
echo.

REM 執行 Python 程式
python generate_mq_topology.py

echo.
echo ============================================================
echo 分析完成！
echo ============================================================
echo.
echo 生成的檔案: mq_topology.md
echo.
echo 按任意鍵開啟結果檔案...
pause > nul

REM 開啟生成的 Markdown 檔案
start mq_topology.md

@REM Made with Bob
