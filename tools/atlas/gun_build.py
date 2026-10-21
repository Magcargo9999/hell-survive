"""악마 총잡이(gun) 도트: 0진화 시트(gun0.webp) · 1진화 시트(gun1.webp) · 최종 시트(gun2.webp) → gun.webp + gun.json
실행 폴더에 시트 3장을 두고 실행. 자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 없음)
- 몸: 어두운 옷이 배경색과 비슷해서 '테두리와 이어진 배경'만 지운다 (an_build.py 와 같은 방식)
- 탄환 · 적중 이펙트: 검은 배경 위 빛이라 배경과의 차이로 부드러운 알파
- 원본 몸은 오른쪽을 본다 (0진화 대기 · 1진화 대기는 정면)"""
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

A = load('gun0.webp')   # 악마 총잡이 (0진화)
frames('i0', A, 468, 572, [478, 562, 645, 728, 806])
frames('w0', A, 462, 572, [840, 924, 1020, 1120, 1212, 1305, 1402])
frames('a0', A, 620, 719, [482, 598, 753, 878, 1038, 1168, 1292, 1405], win=2, gap=20)   # 2번째 칸 총구 불꽃(712~750)은 2번째 칸에 넣는다
frames('h0', A, 768, 862, [474, 553, 652, 744])
frames('d0', A, 768, 862, [772, 872, 976, 1100, 1228, 1408], gap=24)
B = load('gun1.webp')   # 지옥의 무법자 (1진화)
frames('i1', B, 898, 1028, [1140, 1225, 1325, 1418])
frames('w1', B, 272, 414, [1162, 1295])
frames('w1', B, 272, 414, [636, 748])
frames('a1', B, 497, 624, [378, 533, 672, 815, 968, 1108, 1265, 1410], gap=20)
frames('r1', B, 700, 836, [378, 490, 615, 740, 870, 1000, 1147, 1290])
frames('h1', B, 902, 1026, [372, 468, 565, 665])
frames('d1', B, 902, 1026, [690, 842, 982, 1115], gap=24)
C = load('gun2.webp')   # 악마처형자 (최종)
frames('i2', C, 50, 154, [792, 915])
frames('w2', C, 213, 321, [676, 750, 818, 880, 940])
frames('a2', C, 388, 486, [537, 618, 702, 790, 882, 972, 1062], gap=20)
frames('r2', C, 544, 666, [537, 622, 700, 795, 878, 965, 1062])
frames('h2', C, 710, 810, [30, 115, 205, 302, 402, 515])
frames('d2', C, 710, 810, [545, 635, 742, 885, 1058], gap=24)
frames('s2', C, 878, 976, [25, 205, 372, 505, 782, 920, 1075], gap=24)   # 구르기 (최종 스킬)
for k, b in [('bN', (1148, 118, 1196, 142)), ('bR', (1148, 238, 1196, 262)), ('bF', (1148, 366, 1196, 392)), ('bB', (1148, 506, 1196, 532))]: piece(k, C, b)   # 날아가는 탄
for k, bs in [('xN', [(1092, 648, 1172, 728), (1088, 733, 1182, 797)]), ('xR', [(1198, 648, 1242, 688), (1250, 645, 1300, 690), (1218, 698, 1262, 732)]),
              ('xF', [(1312, 652, 1408, 722), (1312, 728, 1412, 799)]), ('xB', [(1422, 668, 1512, 732), (1428, 733, 1502, 792)]),
              ('tF', [(1198, 356, 1240, 412)]), ('tB', [(1376, 498, 1428, 548), (1432, 478, 1512, 552)])]:
    for b in bs: piece(k, C, b)   # 적중 이펙트 · 불씨탄 꼬리 · 공포탄 해골
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
pack(list(info), 'gun')
