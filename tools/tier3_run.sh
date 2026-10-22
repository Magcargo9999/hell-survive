#!/bin/bash
# 티어 재측정 러너: 이어 돌리기(끝난 판 건너뜀) · 다시 실행해도 안전. 사용: nohup bash tools/tier3_run.sh &
cd "$(dirname "$0")/.."
export STOP=${STOP:-1792707000} PAR=${PAR:-2} PYTHONPATH=tools
exec 9>build/tier3/.lock; flock -n 9 || { echo "already running"; exit 0; }
log=build/tier3/run.log
now(){ date +%s; }
st(){ [ "$(now)" -lt "$STOP" ]; }
run(){ st || return 0; echo "[$(date +%H:%M:%S)] $*" >> $log; env "$@" >> $log 2>&1; }
while st; do
  run NA=1 python3 tools/tier3.py A
  run NB=2 python3 tools/tier3.py B
  run NE=1 python3 tools/tier3.py E
  run SEEDS=1 BOSSES=monkey python3 tools/card3.py
  run NA=2 python3 tools/tier3.py A
  run SEEDS=2 BOSSES=monkey python3 tools/card3.py
  run NA=3 python3 tools/tier3.py A
  run NB=4 python3 tools/tier3.py B
  run SEEDS=1 BOSSES=monkey,eye python3 tools/card3.py
  run NA=5 python3 tools/tier3.py A
  run NE=3 python3 tools/tier3.py E
  run NA=10 python3 tools/tier3.py A
  sleep 5
done
echo "[$(date +%H:%M:%S)] STOP reached" >> $log
