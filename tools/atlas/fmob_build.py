"""v9.30 팔열지옥(지하 26~30층) 잡몹 10종 → src/assets/fire/fmob.webp (2프레임 × 10종, 칸 108×114, 발 아래·가운데 맞춤)
시트(build/fire/mobs.png, 1536×1024 검정 배경 필드 몬스터 시트). 자르기 · 배경(검정) 제거 · 배율 조정만 — 재색칠 없음.
칸은 세로로 비어 있는 틈(가장 낮은 열)으로 나눈다."""
import numpy as np, os, json
from PIL import Image
from scipy import ndimage as ndi
os.makedirs('src/assets/fire', exist_ok=True)
img = Image.open('build/fire/mobs.png').convert('RGB'); A = np.array(img).astype(int)
CW, CH = 108, 114
ROW = [(10, 142), (148, 314), (322, 472), (472, 642), (644, 802), (808, 990)]
def fgmask(a, thr=40):
    fg = a.max(2) > thr
    lab, n = ndi.label(fg)   # 부스러기(아주 작은 불티)는 남기되 가장자리의 칸 테두리선만 제거
    for i, sl in enumerate(ndi.find_objects(lab)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (h <= 3 and w >= 30) or (w <= 3 and h >= 30): fg[lab == i + 1] = False
    return fg
def split(row, x0, x1, n):
    y0, y1 = ROW[row]; fg = fgmask(A[y0:y1, x0:x1]); prof = fg.sum(0).astype(float)
    k = np.convolve(prof, np.ones(9) / 9, 'same'); cuts = []
    for i in range(1, n):   # i번째 경계는 기대 위치 둘레에서 가장 낮은 열
        c = int(len(k) * i / n); lo, hi = max(1, c - len(k) // (n * 2)), min(len(k) - 1, c + len(k) // (n * 2))
        cuts.append(lo + int(np.argmin(k[lo:hi])))
    xs = [0] + cuts + [len(k)]; out = []
    for i in range(n):
        seg = fg[:, xs[i]:xs[i + 1]]; ys, xx = np.where(seg)
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xx.min(), xx.max() + 1
        a = A[y0:y1, x0:x1][:, xs[i]:xs[i + 1]][by0:by1, bx0:bx1]; m = seg[by0:by1, bx0:bx1]
        out.append(Image.fromarray(np.dstack([a.astype(np.uint8), (m * 255).astype(np.uint8)]), 'RGBA'))
    return out
def fit(sp, maxh=104, maxw=104):
    w, h = sp.size; k = min(maxh / h, maxw / w)
    nw, nh = max(1, round(w * k)), max(1, round(h * k)); sp = sp.resize((nw, nh), Image.LANCZOS)
    c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.alpha_composite(sp, ((CW - nw) // 2, CH - 2 - nh)); return c, nh
# 이름, 줄, x0, x1, 칸 수, 고를 프레임
SP = [('불꽃 임프', 0, 20, 700, 6, [0, 2]), ('불타는 해골 구체', 4, 12, 495, 4, [0, 2]), ('화염 박쥐 해골', 1, 10, 565, 4, [0, 2]),
      ('불꽃 눈알', 1, 585, 990, 3, [0, 1]), ('화염 로브 망령', 2, 12, 590, 4, [0, 2]), ('지옥 구울', 2, 612, 1040, 3, [0, 2]),
      ('불꽃 망령', 2, 1055, 1530, 3, [0, 2]), ('지옥 사냥개', 4, 1020, 1525, 3, [0, 1]), ('창방패 병사', 3, 15, 615, 4, [0, 2]),
      ('용암 골렘', 3, 1090, 1530, 3, [0, 1])]
cells = []; meta = []
for name, row, x0, x1, n, pick in SP:
    fr = split(row, x0, x1, n); fitted = [fit(fr[i]) for i in pick]
    cells.append([c for c, _ in fitted]); meta.append([name, max(h for _, h in fitted)])
Atl = Image.new('RGBA', (CW * len(cells), CH * 2), (0, 0, 0, 0))
for i, fr in enumerate(cells):
    for k, c in enumerate(fr): Atl.alpha_composite(c, (i * CW, k * CH))
Atl.save('src/assets/fire/fmob.webp', lossless=True, method=6); json.dump(meta, open('src/assets/fire/fmob.json', 'w'), ensure_ascii=False)
bg = Image.new('RGBA', Atl.size, (60, 40, 80, 255)); bg.alpha_composite(Atl); bg.save('build/fire/fmob_prev.png'); print(Atl.size, meta)
