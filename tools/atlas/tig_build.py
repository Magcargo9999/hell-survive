"""지옥의 화염 호랑이(tig) 몸 도트: 보스 시트(마젠타 배경) → src/assets/tig/tig.webp + tig.json
사용법: python3 tools/atlas/tig_build.py <시트.png> [출력폴더]
자르기 · 배경(마젠타) 제거 · 1/3 축소만 (재색칠 없음)
- 줄: 1 대기 6(앞 3칸 정면 · 뒤 3칸 포효) · 2 이동 8 · 3 공격 4(웅크림→도약→포효→내려찍기) · 4 돌진 6(웅크림 2 → 잔상 3 → 급정지)
- 칸끼리 불꽃 꼬리가 겹쳐서, 칸 경계는 겹친 픽셀이 가장 적은 굽은 세로선(seam)으로 자른다
- 이동·공격·돌진 줄은 오른쪽을 본다"""
import os, sys, json
import numpy as np
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else 'build/tig/sheet.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'src/assets/tig'
os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(SRC).convert('RGB')).astype(int)
R, G, B = A[..., 0], A[..., 1], A[..., 2]
FG = ~(((B > 140) & (G < 120) & (R > 140)) | ((B > 105) & (B > G + 40)))   # 마젠타 배경 + 배경이 섞인 분홍 테두리
K = 3                                              # 1/3 로 줄인다 (그릴 때 ×3 nearest)

def seam(y0, y1, gx, win=55):
    """y0~y1 사이를 위에서 아래로 내려가는, 전경을 가장 적게 지나는 세로선 (행마다 x)"""
    f = FG[y0:y1, gx - win:gx + win].astype(float); h, w = f.shape
    cost = f.copy(); back = np.zeros((h, w), int)
    for y in range(1, h):
        prev = cost[y - 1]; best = prev.copy(); arg = np.arange(w)
        l = np.r_[np.inf, prev[:-1]]; r = np.r_[prev[1:], np.inf]
        m = l < best; best[m] = l[m]; arg[m] = (np.arange(w) - 1)[m]
        m = r < best; best[m] = r[m]; arg[m] = (np.arange(w) + 1)[m]
        cost[y] += best + 0.002 * np.abs(np.arange(w) - w / 2); back[y] = arg
    xs = np.zeros(h, int); xs[-1] = int(np.argmin(cost[-1]))
    for y in range(h - 1, 0, -1): xs[y - 1] = back[y, xs[y]]
    return xs + gx - win

def row(y0, y1, x0, x1, n):
    c = FG[y0:y1].sum(0); seams = [np.full(y1 - y0, x0)]
    for i in range(1, n):
        g = int(x0 + (x1 - x0) * i / n); lo, hi = g - 50, g + 50; v = lo + int(np.argmin(c[lo:hi]))
        seams.append(seam(y0, y1, v))
    seams.append(np.full(y1 - y0, x1)); out = []
    for i in range(n):
        L, Rr = seams[i], seams[i + 1]; xa, xb = int(L.min()), int(Rr.max()) + 1
        m = np.zeros((y1 - y0, xb - xa), bool)
        for yy in range(y1 - y0): m[yy, L[yy] - xa:Rr[yy] - xa] = True
        m &= FG[y0:y1, xa:xb]
        ys, xs = np.nonzero(m); ya, yb = ys.min(), ys.max() + 1; xa2, xb2 = xs.min(), xs.max() + 1
        rgb = A[y0 + ya:y0 + yb, xa + xa2:xa + xb2].astype(np.uint8); al = (m[ya:yb, xa2:xb2] * 255).astype(np.uint8)
        im = Image.fromarray(np.dstack([rgb, al]), 'RGBA')
        # 발 기준: 아래 12% 줄의 전경 가운데 x
        mm = m[ya:yb, xa2:xb2]; hh = mm.shape[0]; fy, fx = np.nonzero(mm[int(hh * 0.88):])
        ax = float(fx.mean()) if len(fx) else mm.shape[1] / 2
        w2, h2 = max(1, round(im.width / K)), max(1, round(im.height / K))
        out.append((im.resize((w2, h2), Image.LANCZOS), ax / K, h2 - 1))
    return out

G2 = {
    'idle': row(6, 298, 12, 1437, 6),
    'walk': row(316, 532, 6, 1444, 8),
    'atk': row(543, 780, 39, 1414, 4),
    'dash': row(790, 1070, 10, 1432, 6),
}
# 줄마다 한 장에 쌓기
Wd = max(sum(f[0].width for f in L) for L in G2.values()); y = 0; meta = {}; sheet = []
for k, L in G2.items():
    x = 0; hmax = max(f[0].height for f in L); meta[k] = []
    for im, ax, ay in L: sheet.append((im, x, y)); meta[k].append([x, y, im.width, im.height, round(ax, 1), ay]); x += im.width + 1
    y += hmax + 1
at = Image.new('RGBA', (Wd + len(L) + 8, y))
for im, x, yy in sheet: at.paste(im, (x, yy))
at.save(os.path.join(OUT, 'tig.webp'), lossless=True); json.dump(meta, open(os.path.join(OUT, 'tig.json'), 'w'))
pv = Image.new('RGBA', (at.width * 3, at.height * 3), (40, 30, 60, 255)); pv.alpha_composite(at.resize((at.width * 3, at.height * 3), Image.NEAREST)); pv.save('build/tig_prev.png')
print({k: len(v) for k, v in meta.items()}, at.size)
