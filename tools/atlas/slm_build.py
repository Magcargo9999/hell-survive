"""v10.42 분열체 슬라임 왕(bk 'slm') 아틀라스 — 받은 시트 8장(마젠타 배경)을 자르기 · 배경 제거 · 배율 조정만 한다 (재색칠 없음).
사용: python3 tools/atlas/slm_build.py <대기6> <이동8> <도약12(준비4·공중4·착지4)> <사출6> <분열·재결합10> <피격3·사망6> <이펙트 시트> <거대화6>
 → src/assets/slm/slm.webp (몸 프레임 · 시트마다 서 있는 첫 칸 높이를 대기 칸에 맞춤)  src/assets/slm/slmfx.webp (이펙트, 원래 크기)
   + 두 파일의 프레임 표 JSON을 출력 (src/game_template.html의 SLMF · SLMX에 넣는다): 칸마다 [x, y, w, h, ax, ay] — (ax, ay)는 칸 가운데 · 그 줄의 바닥선"""
import sys, json
import numpy as np
from PIL import Image
A = sys.argv[1:9]
OUT = 'src/assets/slm/'
K = np.array([251, 3, 252], float)

def load(p):   # 마젠타와의 색 거리만큼 투명도 + 가장자리 분홍 번짐 빼기 (색은 그대로)
    a = np.array(Image.open(p).convert('RGB')).astype(float)
    d = np.sqrt(((a - K) ** 2).sum(-1)); al = np.clip((d - 45) / 110, 0, 1)
    c = np.where(al[..., None] > 0.02, (a - (1 - al[..., None]) * K) / np.maximum(al[..., None], 0.02), 0)
    return np.dstack([np.clip(c, 0, 255), al * 255]).astype(np.uint8)

def bands(m):
    rows = (m > 40).sum(1); out = []; inb = False
    for y, v in enumerate(rows):
        if v > 3 and not inb: inb, y0 = True, y
        if v <= 3 and inb: inb = False; out.append((y0, y)) if y - y0 > 8 else None
    if inb: out.append((y0, len(rows)))
    return out

def cols(m, n):   # 빈 세로줄로 나눈 덩어리를 가장 가까운 것끼리 합쳐 n칸으로
    c = (m > 40).sum(0) > 0; segs = []; x = 0; W = len(c)
    while x < W:
        if c[x]:
            x0 = x
            while x < W and c[x]: x += 1
            segs.append([x0, x])
        else: x += 1
    while len(segs) > n:
        g = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]; i = int(np.argmin(g)); segs[i:i + 2] = [[segs[i][0], segs[i + 1][1]]]
    if len(segs) < n:   # 연기·물방울이 칸 사이를 이으면: 고르게 나눈 자리 둘레에서 가장 빈 세로줄로 자른다
        pr = (m > 40).sum(0).astype(float); a0, a1 = segs[0][0], segs[-1][1]; w = (a1 - a0) / n; cut = [a0]
        for i in range(1, n):
            e = a0 + i * w; lo, hi = int(e - w * 0.3), int(e + w * 0.3); cut.append(lo + int(np.argmin(pr[lo:hi])))
        cut.append(a1); segs = [[cut[i], cut[i + 1]] for i in range(n)]
    assert len(segs) == n, (len(segs), n)
    return segs

def frames(img, counts):
    m = img[..., 3]; B = bands(m); assert len(B) == len(counts), (B, counts); out = []
    for (y0, y1), n in zip(B, counts):
        sub = m[y0:y1]; S = cols(sub, n); row = []; bot = []
        for x0, x1 in S:
            ys = np.where((m[y0:y1, x0:x1] > 40).any(1))[0]; bot.append(y0 + ys.max() + 1); row.append([x0, x1, y0 + ys.min(), y0 + ys.max() + 1])
        base = int(np.median(bot)); cx = [(r[0] + r[1]) / 2 for r in row]
        out.append([(img[r[2]:r[3], r[0]:r[1]], c - r[0], base - r[2]) for r, c in zip(row, cx)])
    return out

idle, walk, jump, spit, split, hd, fxs, giant = [load(p) for p in A]
G = {}
I = frames(idle, [6])[0]; ref = I[0][0].shape[0]
def norm(L, refi):   # 서 있는 칸 높이를 대기 첫 칸에 맞춘다
    k = ref / L[refi][0].shape[0]
    return [(np.array(Image.fromarray(f).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.LANCZOS)), ax * k, ay * k) for f, ax, ay in L], k
G['idle'] = I
G['walk'], _ = norm(frames(walk, [8])[0], 0)
J = frames(jump, [4, 4, 4]); kj = ref / J[0][0][0].shape[0]
sc = lambda L, k: [(np.array(Image.fromarray(f).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.LANCZOS)), ax * k, ay * k) for f, ax, ay in L]
G['jprep'], G['jair'], G['jland'] = sc(J[0], kj), sc(J[1], kj), sc(J[2], kj)
G['spit'], _ = norm(frames(spit, [6])[0], 0)
S = frames(split, [5, 5]); ks = ref / S[0][0][0].shape[0]; G['split'], G['merge'] = sc(S[0], ks), sc(S[1], ks)
H = frames(hd, [3, 6]); kh = ref / H[1][0][0].shape[0]; G['hit'], G['death'] = sc(H[0], kh), sc(H[1], kh)
G['giant'], kg = norm(frames(giant, [6])[0], 0)
X = frames(fxs, [10, 2, 6, 6, 5]); FX = {'ball': X[0], 'pud': X[1], 'shock': X[2], 'swirl': X[3], 'splash': X[4]}

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

im, meta = pack(G, 4000); im.save(OUT + 'slm.webp', quality=90, alpha_quality=100, method=6)
im2, meta2 = pack(FX, 3000); im2.save(OUT + 'slmfx.webp', quality=90, alpha_quality=100, method=6)
print('body', im.size, 'ref h', ref, 'giant k', round(kg, 3)); print('fx', im2.size)
print('SLMF', json.dumps(meta, separators=(',', ':'))); print('SLMX', json.dumps(meta2, separators=(',', ':')))
