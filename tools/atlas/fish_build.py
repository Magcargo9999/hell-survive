"""마계 물고기(fish) 도트: 0진화 시트(fish0.png) → fish.webp + fish.json
실행 폴더에 시트를 두고 실행. 자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 없음)
- 몸: 어두운 옷이 배경색과 비슷해서 '테두리와 이어진 배경'만 지운다 (an_build.py 와 같은 방식)
- 탄환 · 적중 이펙트: 검은 배경 위 빛이라 배경과의 차이로 부드러운 알파
- 원본 몸은 오른쪽을 본다"""
import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy import ndimage as ndi
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'an_build.py'), encoding='utf8').read().split('\ninfo = {}')[0])   # load · mode_bg · unblend · body_alpha · keep_main · fx_alpha

def longest(m):   # 줄마다 가장 긴 연속 구간
    r = np.zeros(m.shape[0], int)
    for i, row in enumerate(m):
        if row.any(): d = np.diff(np.concatenate([[0], row.astype(int), [0]])); s = np.where(d == 1)[0]; e = np.where(d == -1)[0]; r[i] = (e - s).max()
    return r
def lines(band, BG):   # 칸막이 선 · 제목 상자 테두리: 가로로 아주 길게 이어진 줄 / 세로로 띠 높이만큼 이어진 줄
    m = np.abs(band - BG).max(-1) > 18; L = np.zeros(m.shape, bool)
    for y in np.where(longest(m) > 380)[0]: L[max(0, y - 1):y + 2] = True
    for x in np.where(longest(m.T) > m.shape[0] * 0.85)[0]: L[:, max(0, x - 1):x + 2] = True
    return L
info = {}
def refine(col, cuts, win):
    return [cuts[0]] + [c0 - win + int(np.argmin(col[c0 - win:c0 + win])) for c0 in cuts[1:-1]] + [cuts[-1]]
def frames(name, S, y0, y1, cuts, win=6, gap=14, keep=None):
    x0, x1 = cuts[0], cuts[-1]; band = S[y0:y1, x0:x1]; BG = mode_bg(band); L = lines(band, BG)
    col = np.convolve((np.abs(band - BG).max(-1) > 26).sum(0).astype(float), np.ones(3) / 3, 'same')
    cs = refine(col, [c - x0 for c in cuts], win); lst = []
    for j in range(len(cs) - 1):
        if keep and j not in keep: continue
        c = band[:, cs[j]:cs[j + 1]]; a, _ = body_alpha(c, BG); a[L[:, cs[j]:cs[j + 1]]] = 0; a = keep_main(a, gap)
        rgba = unblend(c, a, BG); op = rgba[..., 3] > 160; ys, xs = np.where(op)
        bot = int(np.percentile(ys, 99.7)); low = op[int(bot - (bot - ys.min()) * 0.12):bot + 1]; lx = np.where(low)[1]
        lst.append((rgba, float(np.median(lx)), bot))
    base = int(np.median([b for _, _, b in lst]))
    for rgba, ax, bot in lst:
        ys, xs = np.where(rgba[..., 3] > 6); a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        info.setdefault(name, []).append((rgba[a0:a1, b0:b1], ax - b0, base - a0))
def piece(name, S, box, lo=14, hi=70):
    x0, y0, x1, y1 = box; c = S[y0:y1, x0:x1]; BG = mode_bg(S[max(0, y0 - 6):y1 + 6, max(0, x0 - 30):x1 + 30]); a = fx_alpha(c, BG, lo, hi)
    rgba = unblend(c, a, BG); ys, xs = np.where(rgba[..., 3] > 6)
    cr = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; h, w = cr.shape[:2]
    info.setdefault(name, []).append((cr, w / 2, h / 2))

A = load('fish0.png')   # 마계 물고기 (0진화)
def blank(S, box):   # 칸 제목 상자(라벨) 영역만 주변 배경색으로 가린다 (마스크 — 도트는 그대로)
    x0, y0, x1, y1 = box; S[y0:y1, x0:x1] = mode_bg(S[y1:y1 + 30, x0:x1])
blank(A, (536, 205, 745, 250)); blank(A, (484, 556, 712, 601))
frames('i0', A, 232, 352, [535, 670, 810, 950, 1090, 1228, 1425], gap=20)          # 대기 6
frames('w0', A, 408, 538, [535, 645, 752, 862, 985, 1105, 1218, 1322, 1425], gap=20)   # 이동/팔딱이기 8
frames('a0', A, 586, 738, [485, 635, 792, 942, 1090, 1245, 1425], gap=24)          # 물오라 6 (오라 속의 물고기 — 다음 진화용으로 미리 잘라 둔다)
frames('h0', A, 790, 910, [395, 508, 612, 718, 825], gap=20)                      # 피격 4
frames('d0', A, 790, 912, [850, 948, 1042, 1142, 1242, 1338, 1430], gap=24)        # 사망 6
for b in [(42, 1025, 72, 1050), (85, 1000, 130, 1050), (145, 985, 215, 1055), (230, 975, 305, 1055), (325, 965, 430, 1055), (445, 965, 555, 1055),
          (580, 955, 690, 1055), (720, 950, 880, 1060), (900, 950, 1060, 1060), (1085, 945, 1265, 1060), (1285, 955, 1395, 1055)]: piece('fx', A, b)   # 물오라 효과 11조각 (… 7번째 오라 고리 · 9번째 물보라 고리 · 10번째 큰 고리)
def pack(names, fn, W=1360):
    x = y = sh = 0; pos = {}
    for nm in names:
        for i, (c, ax, ay) in enumerate(info[nm]):
            h, w = c.shape[:2]
            if x + w > W: x = 0; y += sh + 2; sh = 0
            pos[(nm, i)] = (x, y); x += w + 2; sh = max(sh, h)
    at = np.zeros((y + sh, W, 4), np.uint8); meta = {}
    for (nm, i), (x, y) in pos.items():
        c, ax, ay = info[nm][i]; h, w = c.shape[:2]; at[y:y + h, x:x + w] = c; meta.setdefault(nm, []).append([x, y, w, h, round(float(ax), 1), int(ay)])
    im = Image.fromarray(at); im.save(fn + '.png'); im.save(fn + '.webp', lossless=True, method=6); json.dump(meta, open(fn + '.json', 'w'), separators=(',', ':'))
    print(fn, at.shape, {k: (len(v), [f[2:4] for f in v]) for k, v in meta.items()})
pack(list(info), 'fish')
