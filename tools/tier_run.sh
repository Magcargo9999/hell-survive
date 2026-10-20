#!/bin/bash
# 새 캐릭터/루트 티어 측정 (v5.01 티어표와 같은 방식: 보스 4종 x 5판 x 2회 + 필드 3단계 x 3판 x 2회)
# 사용: tools/tier_run.sh "snail:bomb" bomb   → build/tier/<이름>_boss.txt, _field.txt
#      python3 tools/tier_an.py build/tier/bomb_boss.txt build/tier/bomb_field.txt "최종 이름" "1진화 이름"
# 변형 키는 tools/sim600.py 의 VAR 표에 있어야 함. 약 30분 걸림 (사용량 큼 — 사용자 요청 시에만)
cd "$(dirname "$0")/.."; V="[\"$1\"]"; N=$2; mkdir -p build/tier
export RANDPICK=1 PAR=2 RAW=1 SEED=17
for rep in 0 1; do
 for bk in monkey eye skel fw; do
  if [ $bk = fw ]; then FWV=1; BKV=; else FWV=; BKV=$bk; fi
  SOFF=$((rep*100)) BK=$BKV FW=$FWV python3 tools/sim600.py B "$V" 5 std 0 | sed "s/^RAW /RAW $bk /" >> build/tier/${N}_boss.txt
 done
 SOFF=$((rep*100)) STAGES='[[8,150],[15,360],[24,600]]' python3 tools/sim600.py L "$V" 3 std 0 >> build/tier/${N}_field.txt
done
echo ALLDONE >> build/tier/${N}_boss.txt
