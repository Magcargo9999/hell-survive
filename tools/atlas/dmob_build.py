"""v9.71 7지옥 '도산과 업경의 심판정'(지하 31~35층) 잡몹 8종 → src/assets/dosan/dmob.webp (4프레임 × 8종, 칸 108×114, 발 아래·가운데 맞춤)
시트: 7지옥 필드 몬스터 시트(1491×1055) — 판마다 아래 '이동 모션(4프레임)' 줄만 쓴다. 자르기 · 배경 제거 · 배율 조정만 (재색칠 없음).
배경 = 칸 가장자리와 이어진 어두운 픽셀, 테두리선(가늘고 긴 덩어리)은 지운다.
사용: python3 tools/atlas/dmob_build.py <몬스터 시트>"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = sys.argv[1] if len(sys.argv) > 1 else 'build/h7/mobs.png'
OUT = 'src/assets/dosan/'; os.makedirs(OUT, exist_ok=True); os.makedirs('build/h7', exist_ok=True)
A = np.array(Image.open(SRC).convert('RGB')).astype(int)
CW, CH = 108, 114
PX = [(18, 362), (384, 732), (754, 1102), (1122, 1470)]   # 판 4개(가로)
PY = [(446, 534), (894, 978)]                                 # 이동 모션 줄(세로) 위·아래 판

def fgmask(a):
    mx = a.max(2); dark = mx <= 30
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    lab2, n2 = ndi.label(fg)
    for i, sl in enumerate(ndi.find_objects(lab2)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; m = lab2[sl] == i + 1
        if (h <= 4 and w >= 25) or (w <= 4 and h >= 25) or m.sum() < 6: fg[sl][m] = False   # 테두리선 · 부스러기
    return fg

def frames(px, py):
    (x0, x1), (y0, y1) = PX[px], PY[py]
    a = A[y0:y1, x0:x1]; fg = fgmask(a)
    prof = ndi.uniform_filter1d(fg.sum(0).astype(float), 5); xs = [0]
    for i in range(1, 4):   # 4칸 경계: 기대 위치 둘레에서 가장 빈 세로줄
        c = int(len(prof) * i / 4); lo, hi = c - len(prof) // 10, c + len(prof) // 10
        xs.append(lo + int(np.argmin(prof[lo:hi])))
    xs.append(len(prof)); out = []
    for i in range(4):
        seg = fg[:, xs[i]:xs[i + 1]].copy(); lab, n = ndi.label(seg); sz = ndi.sum(seg, lab, range(1, n + 1))
        main = lab == (int(np.argmax(sz)) + 1); near = ndi.binary_dilation(main, iterations=10)
        keep = [j + 1 for j in range(n) if sz[j] >= 0.25 * sz.max() or (near & (lab == j + 1)).any()]
        seg = np.isin(lab, keep)   # 몸 + 몸 둘레 10px 안 조각(거울 파편·불꽃)만 — 칸 테두리 장식은 버림
        yy, xx = np.where(seg)
        b = (yy.min(), yy.max() + 1, xx.min(), xx.max() + 1)
        sub = a[:, xs[i]:xs[i + 1]][b[0]:b[1], b[2]:b[3]]; m = seg[b[0]:b[1], b[2]:b[3]]
        out.append(Image.fromarray(np.dstack([sub.astype(np.uint8), (m * 255).astype(np.uint8)]), 'RGBA'))
    return out

def fit(sps, maxh=104, maxw=104):   # 4프레임을 같은 배율로 (걸을 때 크기가 출렁이지 않게)
    k = min(min(maxh / s.size[1], maxw / s.size[0]) for s in sps); res = []; nh = 0
    for sp in sps:
        w, h = sp.size; nw, nh2 = max(1, round(w * k)), max(1, round(h * k)); s2 = sp.resize((nw, nh2), Image.LANCZOS)
        c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.alpha_composite(s2, ((CW - nw) // 2, CH - 2 - nh2)); res.append(c); nh = max(nh, nh2)
    return res, nh

NAMES = ['칼날도깨비', '업경망령', '부적사냥개', '검니멧귀', '파경까마귀', '쇠사슬집행귀', '칼산거미', '죄목등불령']
cells, meta = [], []
for i, nm in enumerate(NAMES):
    fr, nh = fit(frames(i % 4, i // 4)); cells.append(fr); meta.append([nm, nh])
At = Image.new('RGBA', (CW * len(cells), CH * 4), (0, 0, 0, 0))
for i, fr in enumerate(cells):
    for k, c in enumerate(fr): At.alpha_composite(c, (i * CW, k * CH))
At.save(OUT + 'dmob.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'dmob.json', 'w'), ensure_ascii=False)
bg = Image.new('RGBA', At.size, (90, 60, 120, 255)); bg.alpha_composite(At); bg.resize((At.width * 2, At.height * 2), Image.NEAREST).save('build/h7/dmob_prev.png')
print(At.size, meta)
