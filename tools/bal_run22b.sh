#!/bin/bash
# v6.22: 전후 비교용 축소 측정 — 원숭이 마왕만 (0단계 N=6 · 5단계 N=4). 사용: bal_run22b.sh <빌드 html> <출력 폴더> <t0|t5|both>
cd "$(dirname "$0")/.."; B=$(realpath "$1"); O=$2; W=$3; mkdir -p $O
VS='["wolf:abyss","wolf:twin","wolf:blood","wolf:holy","wolf:fallen","snail:venom","snail:lava","snail:bomb","archer:red","archer:holy","archer:skel","chimera:wind","chimera:flame","chimera:dream","lizard:rage","lizard:water","lizard:guard","twins","ghost","octo"]'
export SIMURL=file://$B RANDPICK=1 PAR=2 RAW=1 SEED=17 BK=monkey
[ "$W" != t5 ] && python3 tools/sim600.py B "$VS" 6 std 0 | sed "s/^RAW /RAW monkey /" > $O/t0_monkey.txt
[ "$W" != t0 ] && python3 tools/sim600.py B "$VS" 4 std 5 | sed "s/^RAW /RAW monkey /" > $O/t5_monkey.txt
echo DONE > $O/DONE
