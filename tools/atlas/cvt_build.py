"""영벌의 화염죄수(cvt) 도트: 컨셉 시트 한 장 → src/assets/cvt/cvt.webp + cvt.json
사용법: python3 tools/atlas/cvt_build.py <시트.png> [출력폴더]
자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 변경 없음)
- 몸(대기·이동·공격·피격·사망·절규·광폭 변신·돌진): 어두운 숯빛 몸이 배경과 비슷해서 '테두리와 이어진 배경'만 지운다
- 이펙트(불타는 해골 5·불길 장판·쇠사슬 고리 — 폭발 그림은 주먹이 겹쳐 있어 안 쓴다): 검은 배경 위 빛이라 배경과의 차이로 부드러운 알파
- 원본: 이동·공격 줄은 왼쪽을 본다 (대기·피격·사망은 정면에 가깝다)"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'an_build.py'), encoding='utf8').read().split('\ninfo = {}')[0])   # load · mode_bg · unblend · body_alpha · keep_main · fx_alpha · specks

SHEET = sys.argv[1] if len(sys.argv) > 1 else 'build/cvt/sheet.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'src/assets/cvt'
S = load(SHEET); Lm = S.max(-1)
info = {}

def cuts(x0, y0, x1, y1, n, win=0.3):   # 칸 경계 = 예상 위치 둘레에서 불빛이 가장 적은 세로줄
    m = (Lm[y0:y1, x0:x1] > 70).sum(0).astype(float); m = np.convolve(m, np.ones(5) / 5, 'same'); w = (x1 - x0) / n; cs = [x0]
    for k in range(1, n):
        c = int(k * w); lo, hi = c - int(w * win), c + int(w * win); cs.append(x0 + lo + int(np.argmin(m[lo:hi])))
    return cs + [x1]

def bg_of(x0, y0, x1, y1):   # 판 배경색: 어두운 픽셀의 최빈값
    c = S[y0:y1, x0:x1]; return mode_bg(c)

def line_mask(x0, y0, x1, y1, BG, T=18):   # 판 테두리 · 칸막이 선: 판 전체 폭(높이)에 걸쳐 고르게 이어진 가는 줄 (몸은 색이 들쭉날쭉해서 안 걸림)
    c = S[y0:y1, x0:x1]; d = np.abs(c - BG).max(-1) > T; L = c.max(-1); m = np.zeros(d.shape, bool)
    for y in range(d.shape[0]):
        if d[y].mean() > 0.9 and L[y].std() < 18: m[max(0, y - 1):y + 2] = True
    for x in range(d.shape[1]):
        if d[:, x].mean() > 0.9 and L[:, x].std() < 18: m[:, max(0, x - 1):x + 2] = True
    return m

def no_orn(a, c, area=60):   # 판 모서리 장식(어두운 회색 작은 조각)만 지운다 — 밝은 불티는 남긴다
    m = a > 0.1; lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n < 2: return a
    sz = ndi.sum(m, lab, range(1, n + 1)); big = np.argmax(sz) + 1
    for i in range(1, n + 1):
        if i != big and sz[i - 1] < area and c[lab == i].max(-1).mean() < 90: a[lab == i] = 0
    return a

def cut_body(name, box, n=1, T=30, gap=10, xs=None):
    x0, y0, x1, y1 = box; BG = bg_of(x0, y0, x1, y1); cs = xs or cuts(x0, y0, x1, y1, n); LM = line_mask(x0, y0, x1, y1, BG)
    for j in range(len(cs) - 1):
        c = S[y0:y1, cs[j]:cs[j + 1]]; a, d = body_alpha(c, BG, T=T); a[LM[:, cs[j] - x0:cs[j + 1] - x0]] = 0; a = keep_main(a, gap); a = no_orn(a, c)
        add(name, unblend(c, a, BG))

def cut_fx(name, box, lo=30, hi=90, gap=6):
    x0, y0, x1, y1 = box; c = S[y0:y1, x0:x1]; BG = bg_of(x0, y0, x1, y1); a = fx_alpha(c, BG, lo, hi); a[line_mask(x0, y0, x1, y1, BG)] = 0; a = keep_main(a, gap)
    add(name, unblend(c, a, BG))

def add(name, rgba):   # 알파가 있는 곳만 남기고 기준점 = 발(아래쪽 가운데)
    al = rgba[..., 3]; ys, xs = np.where(al > 6)
    if not len(ys): print('빈 칸', name); return
    a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1; c = rgba[a0:a1, b0:b1]
    op = c[..., 3] > 120; yy, xx = np.where(op); bot = int(yy.max()) if len(yy) else c.shape[0] - 1
    low = op[max(0, int(bot - c.shape[0] * 0.15)):bot + 1]; lx = np.where(low)[1]; ax = float(np.median(lx)) if len(lx) else c.shape[1] / 2
    info.setdefault(name, []).append((c, ax, bot))

# ── 인게임 줄 (판 제목·테두리는 빼고 칸 안쪽만)
cut_body('idle', (514, 356, 902, 461), 6)
cut_body('walk', (914, 356, 1436, 461), 8)
cut_body('atk', (514, 499, 888, 608), 6)
cut_body('hit', (900, 499, 1089, 608), 4)
cut_body('death', (1098, 499, 1436, 608), 5)
# ── 패턴 3 아래 5칸: 무릎 꿇고 절규하며 타오른다 (칸마다 테두리가 있어 안쪽만)
for bx in [(714, 784), (788, 849), (853, 916), (922, 984), (989, 1044)]: cut_body('cast', (bx[0], 987, bx[1], 1063), T=30, gap=8)
# ── 패턴 4: 쇠사슬 파괴(페이즈 2 전환) 3장 · 광폭 돌진 2장
for bx in [(1068, 1160), (1183, 1282), (1297, 1430)]: cut_body('ph2', (bx[0], 783, bx[1], 907), T=30, gap=8)
cut_body('dash', (1066, 948, 1196, 1052), T=30, gap=8)
# ── 이펙트
for cx, cy in [(742, 773), (727, 822), (775, 957), (813, 960), (1024, 795)]:   # 화살표 · 사슬이 덜 걸린 5개
    cut_fx('skull', (cx - 24, cy - 24, cx + 24, cy + 24), 40, 110, 4)
cut_fx('fire', (236, 930, 350, 1030), 34, 100, 6)
cut_fx('hook', (632, 752, 700, 822), 40, 110, 4)

def pack(names, fn, W=1400):
    x = y = rh = 0; pos = {}
    for nm in names:
        for i, (c, ax, ay) in enumerate(info[nm]):
            h, w = c.shape[:2]
            if x + w > W: x = 0; y += rh + 2; rh = 0
            pos[(nm, i)] = (x, y); x += w + 2; rh = max(rh, h)
    at = np.zeros((y + rh, W, 4), np.uint8); meta = {}
    for (nm, i), (x, y) in pos.items():
        c, ax, ay = info[nm][i]; h, w = c.shape[:2]; at[y:y + h, x:x + w] = c; meta.setdefault(nm, []).append([x, y, w, h, round(float(ax), 1), int(ay)])
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    im = Image.fromarray(at); im.save(fn + '.png'); im.save(fn + '.webp', lossless=True, method=6); json.dump(meta, open(fn + '.json', 'w'), separators=(',', ':'))
    return meta
meta = pack(['idle', 'walk', 'atk', 'hit', 'death', 'cast', 'ph2', 'dash', 'skull', 'fire', 'hook'], os.path.join(OUT, 'cvt'))
print({k: len(v) for k, v in meta.items()}); print(json.dumps(meta, separators=(',', ':'))[:400])
