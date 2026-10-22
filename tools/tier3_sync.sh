#!/bin/bash
# 15분마다 원본 로그를 data/tier3 로 복사해 커밋·푸시 (실패해도 계속)
cd "$(dirname "$0")/.."
exec 8>build/tier3/.synclock; flock -n 8 || exit 0
while true; do
  mkdir -p data/tier3/chars data/tier3/cards
  cp -f build/tier3/raw_*.jsonl data/tier3/chars/ 2>/dev/null; cp -f build/tier3/cards/raw_card.jsonl data/tier3/cards/ 2>/dev/null; cp -f build/tier3/run.log data/tier3/run.log 2>/dev/null
  git add data/tier3 tools/tier3*.py tools/tier3*.sh tools/card3.py >/dev/null 2>&1
  git -c user.name="Magcargo9999" -c user.email="gyubinpyeon@gmail.com" commit -qm "tier3: 측정 원본 로그 자동 저장 $(date +%H:%M)" >/dev/null 2>&1
  git push -q origin main >/dev/null 2>&1 || (git pull -q --rebase origin main && git push -q origin main) >/dev/null 2>&1
  [ "$(date +%s)" -gt 1792708800 ] && break
  sleep 900
done
