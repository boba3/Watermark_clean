@echo off
title IOPaint 环境安装程序
color 0A

echo ======================================================
echo           正在配置 AI 去水印工具运行环境
echo ======================================================
echo.

:: 1. 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 并勾选 "Add Python to PATH"！
    pause
    exit
)

:: 2. 设置国内镜像源并升级 pip
echo [1/3] 正在优化下载速度...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 3. 安装 IOPaint
echo [2/3] 正在安装核心程序 (这可能需要几分钟，请保持网络畅通)...
python -m pip install iopaint -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 4. 安装图片处理库
echo [3/3] 正在安装图像辅助库...
python -m pip install opencv-python pillow -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ======================================================
echo ✅ 环境配置完成！
echo 现在您可以直接双击运行主程序 EXE 了。
echo ======================================================
pause