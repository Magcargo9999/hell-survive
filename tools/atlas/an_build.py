"""타락천사(an) 도트: 인게임 시트(an_sheet.webp) · 이펙트 시트(anfx_sheet.webp) · 보스맵(amap.webp) → an.webp / anfx.webp / amap.webp + json
실행 폴더에 시트 3장을 두고 실행. 자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 없음)
- 몸: 어두운 갑옷이 배경색과 거의 같아서 '테두리와 이어진 배경'만 지운다 (안쪽 어두운 부분은 남김)
- 이펙트: 검은 배경 위 빛이라 배경과의 차이로 부드러운 알파"""
import numpy as np, json, shutil
from PIL import Image
from scipy import ndimage as ndi

def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
def mode_bg(c):
    q = (c.reshape(-1, 3) // 4).astype(int); k = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]; v, n = np.unique(k, return_counts=True); m = v[np.argmax(n)]
    return c.reshape(-1, 3)[k == m].mean(0)
def unblend(c, a, BG):
    A = np.clip(a, 0, 1)[..., None]
    with np.errstate(divide='ignore', invalid='ignore'): u = np.where(A > 0.999, c, (c - BG * (1 - A)) / np.maximum(A, 1e-3))
    return np.dstack([np.clip(u, 0, 255).astype(np.uint8), (np.clip(a, 0, 1) * 255).astype(np.uint8)])
def specks(a, minsz=8):
    m = a > 0.04; lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n: sz = ndi.sum(m, lab, range(1, n + 1)); a[np.isin(lab, np.where(sz < minsz)[0] + 1)] = 0
    return a
def body_alpha(c, BG, T=26, lo=8):
    d = np.abs(c - BG).max(-1); strong = d > T
    cand = ~ndi.binary_dilation(strong, iterations=2)
    lab, n = ndi.label(cand); bg = np.zeros_like(cand)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    for i in edge: bg |= lab == i
    for i, sl in enumerate(ndi.find_objects(lab), 1):   # 갇힌 어두운 구역: 크면 배경(베기 궤적 안쪽 · 후광 안쪽), 중간 크기는 푸르스름하면 배경, 작으면 갑옷
        if i in edge or sl is None: continue
        r = lab[sl] == i; area = r.sum(); px = c[sl][r]
        if area >= 400 or (area >= 120 and (px[:, 2] - px[:, 0]).mean() >= 1.0): bg[sl] |= r
    bg |= ndi.binary_dilation(bg, iterations=2) & (d <= T)
    a = np.where(bg, np.clip((d - lo) / (T - lo), 0, 1), 1.0)
    return specks(a), d
def keep_main(a, gap=14):   # 몸과 떨어진 조각(라벨 글자 등)은 버린다
    m = a > 0.1; lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n < 2: return a
    sz = ndi.sum(m, lab, range(1, n + 1)); main = ndi.binary_dilation(lab == (np.argmax(sz) + 1), iterations=gap)
    keep = set(np.unique(lab[main & m])) - {0}
    a[~np.isin(lab, list(keep))] = 0
    return a
def fx_alpha(c, BG, lo, hi):   # 조각 테두리(배경)의 무늬 밝기보다 확실히 밝은 것만 남긴다 — 'lighter'로 겹쳐 그려도 사각형 자국이 안 생기게
    d = np.abs(c - BG).max(-1); dark = d[d < 45]
    lo = max(lo, min(50.0, float(np.percentile(dark, 95)) + 6 if dark.size else lo)); hi = max(hi, lo + 45)
    a = np.clip((d - lo) / (hi - lo), 0, 1); a[a < 0.06] = 0
    return specks(a, 10)

info = {}
def refine(col, cuts, win):
    return [cuts[0]] + [lo + int(np.argmin(col[lo:hi])) for c0 in cuts[1:-1] for lo, hi in [(c0 - win, c0 + win)]] + [cuts[-1]]
def frames(name, S, y0, y1, x0, x1, n, win=26):
    band = S[y0:y1, x0:x1]; BG = mode_bg(band); col = (np.abs(band - BG).max(-1) > 26).sum(0).astype(float)
    col = np.convolve(col, np.ones(5) / 5, 'same')
    cuts = refine(col, [round(i * (x1 - x0) / n) for i in range(n + 1)], win); lst = []
    for j in range(n):
        c = band[:, cuts[j]:cuts[j + 1]]; a, _ = body_alpha(c, BG); a = keep_main(a)
        rgba = unblend(c, a, BG); op = rgba[..., 3] > 160; ys, xs = np.where(op)
        bot = int(np.percentile(ys, 99.6)); low = op[int(bot - (bot - ys.min()) * 0.14):bot + 1]; lx = np.where(low)[1]
        lst.append((rgba, float(np.median(lx)), bot))
    base = int(np.median([b for _, _, b in lst]))
    for rgba, ax, bot in lst:
        ys, xs = np.where(rgba[..., 3] > 6); a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        info.setdefault(name, []).append((rgba[a0:a1, b0:b1], ax - b0, base - a0))
def piece(name, S, box, lo=14, hi=70, ay='mid', cut=None):
    x0, y0, x1, y1 = box; c = S[y0:y1, x0:x1]; BG = mode_bg(S[y0:y1, max(0, x0 - 40):x1 + 40]); a = fx_alpha(c, BG, lo, hi)
    if cut:
        for (cy0, cy1) in cut: a[cy0 - y0:cy1 - y0] = np.where((np.abs(c[cy0 - y0:cy1 - y0] - BG).max(-1) > 110), a[cy0 - y0:cy1 - y0], 0)
    rgba = unblend(c, a, BG); ys, xs = np.where(rgba[..., 3] > 6)
    cr = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; h, w = cr.shape[:2]
    info.setdefault(name, []).append((cr, w / 2, h if ay == 'bot' else h / 2))

# ---- 몸 (원본은 오른쪽을 본다) ----
A = load('an_sheet.webp')
frames('idle', A, 126, 284, 14, 1090, 7)   # 칸막이 선(가로 124·289 / 세로 11·1092)과 바닥 줄(284) 안쪽만
frames('run', A, 336, 461, 14, 1433, 8)
frames('atk', A, 512, 646, 14, 1433, 8)
frames('hit', A, 696, 798, 14, 734, 6)
frames('death', A, 696, 798, 752, 1433, 5)
frames('trans', A, 855, 1043, 14, 1433, 7)
# ---- 이펙트 ----
F = load('anfx_sheet.webp'); LINE = [(505, 512)]   # 기둥 줄의 회색 칸막이 선
for b in [(14, 160, 118, 222), (130, 130, 248, 234), (262, 130, 388, 236)]: piece('tw', F, b)                     # ① 경고 원형
for b in [(396, 130, 512, 236), (514, 130, 634, 236)]: piece('tm', F, b)                                           # ② 타이밍 마커 (박자 표시)
piece('tf', F, (648, 130, 802, 236))                                                                              # ③ 최종 경고 (폭발 직전)
for b in [(800, 100, 906, 236), (944, 100, 1052, 236), (1052, 100, 1146, 236), (1146, 100, 1246, 236), (1246, 100, 1432, 236)]: piece('te', F, b, ay='bot')   # ④ 폭발 (마지막 = 붉은 지연 폭발)
for b in [(24, 312, 112, 438), (142, 312, 222, 438)]: piece('s0', F, b)                                            # ① 방패 생성
piece('s1', F, (226, 306, 372, 438))                                                                              # ② 완성된 방패 (정면)
for b in [(384, 306, 518, 438), (534, 306, 668, 438), (668, 305, 828, 438)]: piece('s2', F, b)                      # ③ 유지 (돌아선 모습)
for b in [(1166, 299, 1256, 438), (1252, 299, 1430, 438)]: piece('s4', F, b)                                       # ⑤ 파괴
for b in [(28, 506, 124, 606), (136, 506, 222, 606), (236, 506, 326, 606)]: piece('pm', F, b, ay='bot', cut=LINE)   # ① 추적 표시
for b in [(348, 503, 430, 606), (438, 503, 514, 606), (518, 503, 608, 606), (612, 503, 718, 606)]: piece('pf', F, b, ay='bot', cut=LINE)   # ② 낙하 준비
for b in [(716, 480, 852, 596), (852, 480, 1002, 596)]: piece('pi', F, b, ay='bot', cut=LINE)                      # ③ 충격
for b in [(1026, 514, 1114, 604), (1124, 514, 1222, 604), (1224, 514, 1322, 604), (1322, 514, 1420, 604)]: piece('pa', F, b, ay='bot', cut=LINE)   # ④ 잔상
for b in [(20, 685, 150, 796), (150, 685, 262, 796)]: piece('x0', F, b, 40, 120, ay='bot')                          # ① 타락 에너지 분출
piece('x2', F, (672, 674, 930, 796), 40, 120, ay='bot', cut=[(679, 685)])                                                           # ③ 변환의 폭발
piece('x3', F, (950, 680, 1228, 796), 40, 120, ay='bot')                                                          # ④ 주변 파동
for b in [(179, 889, 215, 925), (231, 883, 279, 931), (298, 871, 366, 939), (384, 859, 476, 946), (511, 856, 623, 946), (670, 856, 784, 946), (784, 856, 905, 946), (905, 856, 1025, 946), (1025, 856, 1140, 946)]: piece('ob', F, b, cut=[(865, 871)])   # 검은 구체 (이동 → 충돌)
for b in [(176, 984, 208, 1016), (225, 978, 269, 1022), (282, 968, 342, 1032), (366, 956, 454, 1044), (486, 952, 598, 1048), (635, 948, 755, 1048), (777, 948, 893, 1048), (928, 948, 1052, 1048), (1062, 948, 1160, 1048)]: piece('ow', F, b)   # 흰 구체 (이동 → 미접촉 폭발)
def pack(names, fn, W=1600):
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
pack(['idle', 'run', 'atk', 'hit', 'death', 'trans'], 'an')
pack(['tw', 'tm', 'tf', 'te', 's0', 's1', 's2', 's4', 'pm', 'pf', 'pi', 'pa', 'x0', 'x2', 'x3', 'ob', 'ow'], 'anfx')
shutil.copyfile('amap.webp', 'amap_out.webp')   # 보스맵: 받은 그림 그대로 (게임에서 정수 2배 nearest)
