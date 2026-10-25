"""불구렁이(snk) 도트: 컨셉 시트 한 장 → src/assets/snk/snk.webp + snk.json
사용법: python3 tools/atlas/snk_build.py <시트.png> [출력폴더]
자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 변경 없음) — 방식은 cvt_build.py 와 같다 (테두리와 이어진 배경만 지움)
- 인게임 줄: 대기 6 · 이동 8 · 잠복 6 · 돌출 6 · 공격 6 · 피격 4 · 사망 6
- 원본: 이동·공격·피격 줄은 오른쪽을 본다 (대기·잠복·돌출·사망은 정면에 가깝다)"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'cvt_build.py'), encoding='utf8').read()
pre = src.split('# ── 인게임 줄')[0].replace("sys.argv[1] if len(sys.argv) > 1 else 'build/cvt/sheet.png'", "sys.argv[1] if len(sys.argv) > 1 else 'build/snk/sheet.png'").replace("'src/assets/cvt'", "'src/assets/snk'")
exec(pre.replace('d[:, x].mean() > 0.9', 'd[:, x].mean() > 0.6'))   # 칸막이 세로줄이 흐릿해서 문턱을 낮춘다
pk = src.split('def pack(')[1].split('meta = pack(')[0]
exec('def pack(' + pk)
cut_body('idle', (12, 360, 670, 438), 6)
cut_body('walk', (687, 361, 1437, 441), 8)
cut_body('burrow', (12, 482, 695, 563), 6)
cut_body('emerge', (710, 482, 1437, 564), 6)
cut_body('atk', (12, 604, 543, 681), 6)
cut_body('hit', (557, 604, 877, 681), 4)
cut_body('death', (891, 604, 1437, 681), 6)
# ── 몸통 마디 무늬: '주요 디테일 – 체표(용암)' 칸에서 정사각형으로 잘라 둥근 마스크 (재색칠 없음)
c = S[160:236, 1250:1326].astype(np.uint8); hh, ww = c.shape[:2]; yy, xx = np.mgrid[0:hh, 0:ww]
rr = np.hypot(xx - (ww - 1) / 2, yy - (hh - 1) / 2) / (ww / 2); al = np.clip((1 - rr) / 0.08, 0, 1) * 255
info['scale'] = [(np.dstack([c[..., :3], al.astype(np.uint8)]), ww / 2, hh - 1)]
meta = pack(['idle', 'walk', 'burrow', 'emerge', 'atk', 'hit', 'death', 'scale'], os.path.join(OUT, 'snk'))
print({k: len(v) for k, v in meta.items()})
