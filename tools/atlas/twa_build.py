"""v10.61 종말의 쌍두천사(bk 'twa') 아틀라스 — 받은 아트 초안 2개(본체 zip · 파츠/이펙트 zip)를 자르기 · 배율 조정만 한다 (재색칠 없음).
사용: python3 tools/atlas/twa_build.py <body zip 푼 폴더> <parts_fx zip 푼 폴더>
 받은 시트는 1280×768 칸이 가로 한 줄이고 '정확한 2×2 픽셀 복제'(2배 nearest)라서, 2×2 한 칸에서 한 픽셀만 떠서 원래 1배 도트로 되돌려 저장한다
 (게임은 ×2 nearest로 그린다 — 화면에 보이는 크기·도트는 받은 그림과 같다).
 → src/assets/twa/twa.webp (본체 9동작 60칸 + 곧게 뻗은 팔 2칸)  src/assets/twa/twafx.webp (이펙트 13종 × 6칸)
   + 프레임 표 JSON (src/game_template.html의 TWAF · TWAX): 칸마다 [x, y, w, h, ax, ay] (1배 픽셀) — 본체 ax·ay = 받침대 바닥 가운데(피벗 640,688 ÷ 2), 이펙트 = 칸 가운데(640,384 ÷ 2)"""
import sys, json, os
import numpy as np
from PIL import Image
BODY, PARTS = sys.argv[1], sys.argv[2]
OUT = 'src/assets/twa/'; os.makedirs(OUT, exist_ok=True); os.makedirs('build/twa', exist_ok=True)

def cells(p, n):
    a = np.array(Image.open(p).convert('RGBA')); assert a.shape[1] == 1280 * n and a.shape[0] == 768, (p, a.shape, n)
    h = a[::2, ::2]; assert (a[1::2, ::2] == h).all() and (a[::2, 1::2] == h).all(), p   # 2×2 복제 확인
    return [h[:, i * 640:(i + 1) * 640] for i in range(n)]

def crop(c, px, py):   # 불투명한 곳만 + 기준점
    al = c[..., 3] > 0; ys, xs = np.where(al)
    if not len(xs): return (np.zeros((2, 2, 4), np.uint8), 1.0, 1.0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return (c[y0:y1, x0:x1].copy(), px - x0, py - y0)

def pack(G, maxw):
    x = y = rowh = 0; pos = {}; W = 0
    for k, L in G.items():
        for i, (f, ax, ay) in enumerate(L):
            h, w = f.shape[:2]
            if x + w > maxw: x = 0; y += rowh + 2; rowh = 0
            pos[(k, i)] = (x, y); x += w + 2; rowh = max(rowh, h); W = max(W, x)
    im = Image.new('RGBA', (W, y + rowh)); meta = {}
    for k, L in G.items():
        meta[k] = []
        for i, (f, ax, ay) in enumerate(L):
            px, py = pos[(k, i)]; im.paste(Image.fromarray(f), (px, py))
            meta[k].append([px, py, f.shape[1], f.shape[0], round(float(ax), 1), round(float(ay), 1)])
    return im, meta

G = {}
for k, n in [('idle', 6), ('polarity_hymn', 6), ('six_arm_scissor', 8), ('palm_strike', 6), ('blood_resonance', 6), ('halo_guillotine', 6), ('apocalypse_chant', 8), ('exposed', 6), ('death', 8)]:
    G[k] = [crop(c, 320, 344) for c in cells(f'{BODY}/body/{k}.png', n)]
for side in ('left', 'right'):   # 가위질 날 끝에 그릴 곧게 뻗은 가운데 팔 (2번째 칸) — 기준 = 어깨 관절
    c = cells(f'{PARTS}/parts/{side}_middle.png', 4)[1]
    al = c[..., 3] > 0; ys, xs = np.where(al); sx = xs.max() if side == 'left' else xs.min()
    sy = int(np.median(ys[np.abs(xs - sx) < 6]))
    G['arm_' + side[0]] = [crop(c, sx, sy)]
X = {}
for k in ['gold_stigma', 'crimson_stigma', 'gold_wave', 'crimson_wave', 'tear_drop', 'blood_pool', 'resonance_laser', 'halo_inner', 'halo_outer', 'seal_bell', 'wrist_chain', 'purification_beam', 'apocalypse_flash']:
    X[k] = [crop(c, 320, 192) for c in cells(f'{PARTS}/vfx/{k}.png', 6)]

im, meta = pack(G, 2400); im.save(OUT + 'twa.webp', quality=92, alpha_quality=100, method=6)
im2, meta2 = pack(X, 2400); im2.save(OUT + 'twafx.webp', quality=92, alpha_quality=100, method=6)
im.save('build/twa/body.png'); im2.save('build/twa/fx.png')
print('TWAF', json.dumps(meta, separators=(',', ':')))
print('TWAX', json.dumps(meta2, separators=(',', ':')))
print(im.size, im2.size, os.path.getsize(OUT + 'twa.webp'), os.path.getsize(OUT + 'twafx.webp'), file=sys.stderr)
