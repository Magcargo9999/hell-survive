#!/bin/bash
# v6.22 밸런스 측정: bal_run22.sh <빌드 html> <출력 폴더> [N]
# 보스 4종(난이도0) + 5단계 원숭이/마안/스켈레톤, 변형 20개, 같은 시드 → 변경 전후 비교
cd "$(dirname "$0")/.."; B=$(realpath "$1"); O=$2; N=${3:-6}; mkdir -p $O
VS='["wolf:abyss","wolf:twin","wolf:blood","wolf:holy","wolf:fallen","snail:venom","snail:lava","snail:bomb","archer:red","archer:holy","archer:skel","chimera:wind","chimera:flame","chimera:dream","lizard:rage","lizard:water","lizard:guard","twins","ghost","octo"]'
export SIMURL=file://$B RANDPICK=1 PAR=2 RAW=1 SEED=17
for bk in monkey eye skel fw; do
  if [ $bk = fw ]; then FWV=1; BKV=; else FWV=; BKV=$bk; fi
  BK=$BKV FW=$FWV python3 tools/sim600.py B "$VS" $N std 0 | sed "s/^RAW /RAW $bk /" > $O/t0_$bk.txt
done
for bk in monkey eye skel; do
  BK=$bk python3 tools/sim600.py B "$VS" $N std 5 | sed "s/^RAW /RAW $bk /" > $O/t5_$bk.txt
done
echo DONE > $O/DONE
