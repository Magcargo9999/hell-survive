"""v7.13 쿠폰 스킨: 타락천사 여자 버전. 시트(build/horse/angel2.png)의 동작 줄을 칸 균등 분할 → 배경 제거(차이→알파·속 구멍 메움)만.
출력: src/assets/an/an2.webp (줄 = 동작) + an2.json (동작 → 프레임 [x,y,w,h,기준x,발y]). 기준 크기는 게임에서 기존 도트 높이에 맞춰 곱한다(AN2_K)"""
import numpy as np, json, os, sys
from PIL import Image
sys.path.insert(0, 'tools/atlas')
import importlib.util
spec = importlib.util.spec_from_file_location('hb', 'tools/atlas/horse_build.py')
src = open('tools/atlas/horse_build.py').read().split('# 동작 이름')[0]   # cut() 함수까지만 재사용
ns = {}; exec(src, ns); cut = ns['cut']
S = np.array(Image.open('build/horse/angel2.png').convert('RGB')).astype(float)
ROWS = [('idle', 668, 1272, 42, 126, 7), ('run', 664, 1326, 168, 266, 6), ('atk', 664, 1326, 288, 386, 6), ('hit', 664, 1326, 418, 488, 6), ('death', 664, 1326, 522, 580, 6), ('trans', 664, 1326, 612, 750, 7)]
rows = []
for an, x0, x1, y0, y1, n in ROWS:
    cw = (x1 - x0) / n; fr = [cut(S, (round(x0 + i * cw), y0, round(x0 + (i + 1) * cw), y1), 10, 26) for i in range(n)]; rows.append((an, fr))
os.makedirs('src/assets/an', exist_ok=True)
PAD = 2; W = max(sum(c.shape[1] + PAD for c in fr) for _, fr in rows); H = sum(max(c.shape[0] for c in fr) + PAD for _, fr in rows)
at = np.zeros((H, W, 4), np.uint8); y = 0; meta = {}
for an, fr in rows:
    h = max(c.shape[0] for c in fr); x = 0; out = []
    for c in fr:
        ch, cw2 = c.shape[:2]; at[y + h - ch:y + h, x:x + cw2] = c; out.append([x, y + h - ch, cw2, ch, cw2 / 2, ch]); x += cw2 + PAD
    meta[an] = out; y += h + PAD
Image.fromarray(at).save('src/assets/an/an2.webp', lossless=True, method=6); json.dump(meta, open('src/assets/an/an2.json', 'w'), separators=(',', ':'))
print(at.shape, {a: [(f[2], f[3]) for f in v] for a, v in meta.items()})
bg = Image.new('RGBA', (W, H), (70, 70, 80, 255)); bg.alpha_composite(Image.fromarray(at)); bg.save('build/horse/an2_view.png')
