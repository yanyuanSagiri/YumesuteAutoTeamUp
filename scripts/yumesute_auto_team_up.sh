#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

DATA_DIR="Data"
USER_NAME="Yumetest"
MANDATORY_CHARS=(150010 0 150020 0 150030 0 150040 0 0 0)
MANDATORY_POSTERS=(0 0 0 0 0 0 0 0 0 0)
MANDATORY_LEADER=0
UPDATE_REPO="https://github.com/esterTion/yumesute_master_db_diff"

CMD=(python "Start.py" "$DATA_DIR" "$USER_NAME")

if [ "${MANDATORY_CHARS[*]}" != "0 0 0 0 0 0 0 0 0 0" ]; then
    CMD+=(-mc "${MANDATORY_CHARS[@]}")
fi

if [ "${MANDATORY_POSTERS[*]}" != "0 0 0 0 0 0 0 0 0 0" ]; then
    CMD+=(-mp "${MANDATORY_POSTERS[@]}")
fi

if [ $MANDATORY_LEADER -ne 0 ]; then
    CMD+=(-ml "$MANDATORY_LEADER")
fi

if [ -n "$UPDATE_REPO" ]; then
    CMD+=(-u "$UPDATE_REPO")
fi

echo "执行命令：${CMD[*]}"
"${CMD[@]}"