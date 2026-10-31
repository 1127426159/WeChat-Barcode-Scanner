#!/bin/sh
# Finder 双击入口。实际启动逻辑仍由 start.sh 负责。

cd "$(dirname "$0")" || exit 1

sh ./start.sh "$@"
status=$?

if [ "$status" -ne 0 ] && [ "$status" -ne 130 ] && [ "$status" -ne 143 ]; then
    printf '\n启动失败，请查看上面的错误信息。\n'
    printf '按回车键关闭窗口...'
    read -r _
fi

exit "$status"
