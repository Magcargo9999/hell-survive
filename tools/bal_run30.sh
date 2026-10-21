#!/bin/bash
# v6.30: 보스별 비교 측정 — 사용: bal_run30.sh <빌드 html> <출력 폴더> <단계> <N> [보스...]  (기본: monkey eye skel angel · fw = 타락한 혈랑왕)
# 결과 t<단계>_<보스>.txt (RAW <보스> {...}) → tools/bal_cmp30.py 로 표, tools/bal_cmp22.py <전> <후> 로 전후 비교. v6.22의 bal_run22*.sh 를 대신한다
cd "$(dirname "$0")/.."; B=$(realpath "$1"); command -v cygpath >/dev/null && B=$(cygpath -m "$B"); case "$B" in /*) U="file://$B";; *) U="file:///$B";; esac   # 윈도우(Git Bash)는 C:/ 경로로
O=$2; T=$3; N=$4; shift 4; BS=${@:-monkey eye skel angel}; mkdir -p $O
VS=${VSJ:-'["wolf:abyss","wolf:twin","wolf:blood","wolf:holy","wolf:fallen","snail:venom","snail:lava","snail:bomb","archer:red","archer:holy","archer:skel","chimera:wind","chimera:flame","chimera:dream","lizard:rage","lizard:water","lizard:guard","twins","ghost","octo","gun"]'}
export SIMURL=$U RANDPICK=1 PAR=${PAR:-4} RAW=1 SEED=${SEED:-17}
for k in $BS; do if [ $k = fw ]; then FWV=1; BKV=; else FWV=; BKV=$k; fi
  BK=$BKV FW=$FWV python3 tools/sim600.py B "$VS" $N std $T | sed "s/^RAW /RAW $k /" > $O/t${T}_$k.txt; done
echo DONE > $O/DONE
