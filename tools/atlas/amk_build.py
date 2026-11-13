"""v10.46 각성한 원숭이 마왕(bk 'amk') 아틀라스 — 받은 시트 5장을 자르기 · 배경 제거 · 배율 조정만 한다 (재색칠 없음).
사용: python3 tools/atlas/amk_build.py <시트1(기본 몸: 대기6·이동8·할퀴기6·도약4·착지4·포효6·브레스7·분신6·피격3+사망6)> <시트3(작은 몸: 돌진 줄)> <시트5(가로줄 있는 몸: 질주7·휠윈드6·대지 파열6·각성 포효6)> <시트4(이펙트)> <시트2(컨셉 판: 분노 대기6·광폭 이동8)>
 → src/assets/amk/amk.webp (몸 · 시트마다 서 있는 첫 칸 높이를 기본 대기 칸에 맞춤)  src/assets/amk/amkfx.webp (이펙트 · 원래 크기)
   + 프레임 표 JSON 출력 (src/game_template.html의 AMKF · AMKX): 칸마다 [x, y, w, h, ax, ay] — ay = 그 줄의 바닥선, ax = 몸 가운데(앞·뒤로 이펙트가 뻗는 줄은 몸 쪽 끝 기준)"""
import sys, json
import numpy as np
from PIL import Image
A = sys.argv[1:6]
OUT = 'src/assets/amk/'
K = np.array([251, 3, 252], float)

def load(p, box=None):   # 마젠타와의 색 거리만큼 투명도 + 가장자리 분홍 번짐 빼기 (색은 그대로)
    im = Image.open(p).convert('RGB')
    if box: im = im.crop(box)
    a = np.array(im).astype(float)
    d = np.sqrt(((a - K) ** 2).sum(-1)); al = np.clip((d - 45) / 110, 0, 1)
    c = np.where(al[..., None] > 0.02, (a - (1 - al[..., None]) * K) / np.maximum(al[..., None], 0.02), 0)
    return np.dstack([np.clip(c, 0, 255), al * 255]).astype(np.uint8)

def unline(img, thr):   # 시트를 가로지르는 줄 구분선(거의 전체 폭)을 지운다
    rows = (img[..., 3] > 40).sum(1)
    for y in np.where(rows > thr)[0]: img[y, :, 3] = 0
    return img

def bands(m, cut=()):
    rows = (m > 40).sum(1).copy()
    for y in cut: rows[y] = 0   # 두 줄이 세로로 붙은 곳은 직접 나눈다
    out = []; inb = False
    for y, v in enumerate(rows):
        if v > 3 and not inb: inb, y0 = True, y
        if v <= 3 and inb:
            inb = False
            if y - y0 > 24: out.append((y0, y))
    if inb: out.append((y0, len(rows)))
    return out

def cols(m, n):
    c = (m > 40).sum(0) > 0; segs = []; x = 0; W = len(c)
    while x < W:
        if c[x]:
            x0 = x
            while x < W and c[x]: x += 1
            segs.append([x0, x])
        else: x += 1
    while len(segs) > n:   # 부스러기는 가장 가까운 칸에 붙인다
        g = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]; i = int(np.argmin(g)); segs[i:i + 2] = [[segs[i][0], segs[i + 1][1]]]
    if len(segs) < n:   # 이펙트가 칸 사이를 이으면: 고르게 나눈 자리 둘레에서 가장 빈 세로줄로 자른다
        pr = (m > 40).sum(0).astype(float); a0, a1 = segs[0][0], segs[-1][1]; w = (a1 - a0) / n; cut = [a0]
        for i in range(1, n):
            e = a0 + i * w; lo, hi = int(e - w * 0.3), int(e + w * 0.3); cut.append(lo + int(np.argmin(pr[lo:hi])))
        cut.append(a1); segs = [[cut[i], cut[i + 1]] for i in range(n)]
    assert len(segs) == n, (len(segs), n)
    return segs

def frames(img, counts, cut=()):
    m = img[..., 3]; B = bands(m, cut); assert len(B) == len(counts), ([(b, len(cols(m[b[0]:b[1]], 1))) for b in B], counts); out = []
    for (y0, y1), n in zip(B, counts):
        S = cols(m[y0:y1], n); row = []; bot = []
        for x0, x1 in S:
            ys = np.where((m[y0:y1, x0:x1] > 40).any(1))[0]; bot.append(y0 + ys.max() + 1); row.append([x0, x1, y0 + ys.min(), y0 + ys.max() + 1])
        base = int(np.median(bot))
        out.append([(img[r[2]:r[3], r[0]:r[1]].copy(), (r[1] - r[0]) / 2, base - r[2]) for r in row])
    return out

def rs(f, k): return np.array(Image.fromarray(f).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.LANCZOS if k < 1.25 else Image.NEAREST))
def sc(L, k, anchor='c'):   # anchor: 'c' 칸 가운데 · 'l' 왼쪽 끝 + 첫 칸 절반(이펙트가 오른쪽으로 뻗음) · 'r' 오른쪽 끝 − 첫 칸 절반(왼쪽으로 뻗음)
    w0 = L[0][0].shape[1] / 2; out = []
    for f, ax, ay in L:
        ax = w0 if anchor == 'l' else f.shape[1] - w0 if anchor == 'r' else ax
        out.append((rs(f, k) if abs(k - 1) > 0.01 else f, ax * k, ay * k))
    return out

s1, s3, s5, s4, s2 = A
G = {}
F1 = frames(load(s1), [6, 8, 6, 4, 4, 6, 7, 6, 9]); ref = F1[0][0][0].shape[0]
G['idle'] = F1[0]; G['walk'] = sc(F1[1], 1); G['claw'] = sc(F1[2], 1, 'l'); G['leap'] = sc(F1[3], 1, 'r'); G['land'] = sc(F1[4], 1)
G['roar'] = sc(F1[5], 1); G['clone'] = sc(F1[7], 1); G['hit'] = sc(F1[8][:3], 1); G['death'] = sc(F1[8][3:], 1)
F5 = frames(unline(load(s5), 1250), [6, 6, 7, 6, 7, 6, 9, 7, 7]); k5 = ref / F5[0][0][0].shape[0]
G['rage'] = sc(F5[1], k5); G['run'] = sc(F5[2], k5, 'r'); G['whirl'] = sc(F5[3], k5); G['slam'] = sc(F5[5], k5)
F3 = frames(load(s3), [8, 8, 6, 5, 8, 7, 7, 8, 1]); k3 = ref / F3[0][0][0].shape[0]
G['dash'] = sc(F3[3], k3, 'r')
FX = frames(load(s4), [12, 10, 8, 9, 8, 8, 8, 9, 14], cut=(533,))   # 휠윈드 줄과 착지 고리 줄이 세로로 맞닿아 직접 나눔
kph = ref / FX[3][0][0].shape[0]; G['phantom'] = sc(FX[3], kph)
# 컨셉 판(시트2): 판 안쪽 마젠타 칸만 — 분노 대기 · 광폭 이동 · (배율 기준) 기본 대기
def panel(box, n):
    img = load(s2, box)   # 상자는 판 테두리 안쪽(마젠타 칸)만 잡는다
    m = img[..., 3]; ys = np.where((m > 40).sum(1) > 3)[0]; img = img[ys.min():ys.max() + 1]
    S = cols(img[..., 3], n); out = []; bot = []; row = []
    for x0, x1 in S:
        yy = np.where((img[:, x0:x1, 3] > 40).any(1))[0]; bot.append(yy.max() + 1); row.append([x0, x1, yy.min(), yy.max() + 1])
    base = int(np.median(bot))
    return [(img[r[2]:r[3], r[0]:r[1]].copy(), (r[1] - r[0]) / 2, base - r[2]) for r in row]
N0 = panel((14, 64, 716, 172), 6); k2 = ref / N0[0][0].shape[0]
G['ridle'] = sc(panel((748, 180, 1522, 262), 6), k2); G['rmove'] = sc(panel((748, 290, 1522, 354), 8), k2)
X = {'crack': FX[0], 'pillar': FX[1], 'wave': FX[2], 'spin': FX[4], 'ring': FX[5], 'boom': FX[6], 'aura': FX[7], 'orb': FX[8][:5], 'burst': FX[8][5:]}

def pack(D, wmax):
    x = y = rh = 0; meta = {}; place = []
    for k, L in D.items():
        meta[k] = []
        for f, ax, ay in L:
            h, w = f.shape[:2]
            if x + w > wmax: x = 0; y += rh + 2; rh = 0
            place.append((f, x, y)); meta[k].append([x, y, w, h, round(float(ax), 1), round(float(ay), 1)]); x += w + 2; rh = max(rh, h)
    can = np.zeros((y + rh, wmax, 4), np.uint8)
    for f, px, py in place: can[py:py + f.shape[0], px:px + f.shape[1]] = f
    used = max(m[0] + m[2] for L in meta.values() for m in L)
    return Image.fromarray(can[:, :used]), meta

im, meta = pack(G, 3600); im.save(OUT + 'amk.webp', quality=90, alpha_quality=100, method=6)
im2, meta2 = pack(X, 3000); im2.save(OUT + 'amkfx.webp', quality=90, alpha_quality=100, method=6)
im.save('build/amk/body.png'); im2.save('build/amk/fx.png')
print('body', im.size, 'ref h', ref, 'k5', round(k5, 3), 'k3', round(k3, 3), 'kph', round(kph, 3), 'k2', round(k2, 3)); print('fx', im2.size)
json.dump({'AMKF': meta, 'AMKX': meta2}, open('build/amk/meta.json', 'w'), separators=(',', ':'))
