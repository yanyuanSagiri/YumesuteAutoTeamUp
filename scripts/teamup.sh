#!/bin/bash
# 构建配队状态, 并将结果自动上传至服务器并接收返回的结果. 服务器那边暂时鸽掉了.
# DATA_DIR 为存储游戏内的 json 文件地址
# USER_NAME 为根目录下你的 json 文件游戏数据地址
# MANDATORY_CHARS 为角色输入. 每两个选项为一组, 第一个是必上场的角色 ID, 随后是其必须站的位置. 五组输入之间无需顾虑顺序.
# MANDATORY_POSTERS 为海报输入, 与上面相同.
# MANDATORY_LEADER 为队长位置, 暂未适配.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

DATA_DIR="data"
USER_NAME="Yumesute.json"
MANDATORY_CHARS=(150010 0 150020 0 150030 0 150040 0 0 0)
MANDATORY_POSTERS=(330380 0 230120 0 0 0 0 0 0 0)
MANDATORY_LEADER=0

CMD=(python "StartForServer.py" "$USER_NAME")

CMD+=(-d "$DATA_DIR")

if [ "${MANDATORY_CHARS[*]}" != "0 0 0 0 0 0 0 0 0 0" ]; then
    CMD+=(-mc "${MANDATORY_CHARS[@]}")
fi

if [ "${MANDATORY_POSTERS[*]}" != "0 0 0 0 0 0 0 0 0 0" ]; then
    CMD+=(-mp "${MANDATORY_POSTERS[@]}")
fi

if [ $MANDATORY_LEADER -ne 0 ]; then
    CMD+=(-ml "$MANDATORY_LEADER")
fi

echo "Execute command: ${CMD[*]}"
"${CMD[@]}"

read -r -p "按回车键退出..."