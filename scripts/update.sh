#!/bin/bash
# 数据更新脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT" || { echo "切换至更新文件目录失败，请检查是否移动了脚本或更新文件位置"; exit 1; }

PYTHON_CMD=""
for cmd in python python3 python3.9 python3.8; do  # check by priority
    if command -v "$cmd" &> /dev/null; then
        # 进一步检查这个命令不是 Windows 的假别名(optional)
        if "$cmd" -c "print('test')" &> /dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "未找到可用的 Python 解释器，请检查 Python 安装。"
    read -r -p "按回车键退出..."
    exit 1
fi

"$PYTHON_CMD" update.py

read -r -p "按回车键退出..."