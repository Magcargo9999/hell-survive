#!/bin/bash
# 러너·동기화가 죽어 있으면 다시 띄운다 (락 파일로 판별)
cd /home/claude/hell-survive || exit 1
mkdir -p build/tier3
flock -n build/tier3/.lock true && nohup setsid bash tools/tier3_run.sh >/dev/null 2>&1 &
flock -n build/tier3/.synclock true && nohup setsid bash tools/tier3_sync.sh >/dev/null 2>&1 &
sleep 1
