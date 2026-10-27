"""심해의 시체고래(whl) 몸 도트: 보스 시트 한 장 → src/assets/whl/whl.webp + whl.json
사용법: python3 tools/atlas/whl_build.py <보스 시트.png> [출력폴더]
자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 변경 없음) — 테두리와 이어진 배경(남색)만 지우고, 둘레 물빛은 배경과의 차이만큼 반투명
- 인게임 줄: 대기 6 · 이동 8 · 물기 6 · 강력한 스킬(도약 2 + 물속 1) · 잠수/출현 6 · 피격 4 · 사망 6
- 원본은 오른쪽을 본다 (머리가 오른쪽)"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'an_build.py'), encoding='utf8').read().split('\ninfo = {}')[0])   # load · mode_bg · unblend · body_alpha · keep_main · fx_alpha · specks
SHEET = sys.argv[1] if len(sys.argv) > 1 else 'build/whl/body.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'src/assets/whl'
S = load(SHEET); Lm = S.max(-1); BG = np.array([0.4, 9.8, 17.4])
info = {}

def cuts(x0, y0, x1, y1, n, win=0.3):   # 칸 경계 = 예상 위치 둘레에서 가장 빈 세로줄
    m = (np.abs(S[y0:y1, x0:x1] - BG).max(-1) > 40).sum(0).astype(float); m = np.convolve(m, np.ones(5) / 5, 'same'); w = (x1 - x0) / n; cs = [x0]
    for k in range(1, n):
        c = int(k * w); lo, hi = c - int(w * win), c + int(w * win); cs.append(x0 + lo + int(np.argmin(m[lo:hi])))
    return cs + [x1]

def add(name, rgba):   # 알파가 있는 곳만 남기고 기준점 = 아래쪽 가운데(발)
    al = rgba[..., 3]; ys, xs = np.where(al > 6)
    if not len(ys): print('빈 칸', name); return
    a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1; c = rgba[a0:a1, b0:b1]
    op = c[..., 3] > 120; yy, xx = np.where(op); bot = int(yy.max()) if len(yy) else c.shape[0] - 1
    info.setdefault(name, []).append((c, c.shape[1] / 2, bot))

def cut(name, box, n=1, T=34, gap=10, xs=None):
    x0, y0, x1, y1 = box; cs = xs or (cuts(x0, y0, x1, y1, n) if n > 1 else [x0, x1])
    for j in range(len(cs) - 1):
        c = S[y0:y1, cs[j]:cs[j + 1]]; a, d = body_alpha(c, BG, T=T, lo=10); a = keep_main(a, gap)
        add(name, unblend(c, a, BG))

cut('idle', (12, 333, 1436, 421), 6)
cut('walk', (12, 466, 1436, 554), 8)
cut('bite', (12, 597, 1436, 684), 6)
cut('leap', (12, 730, 486, 821), xs=[12, 228, 486])
cut('dive', (12, 865, 1436, 941), 6, gap=16)
cut('hit', (12, 986, 640, 1075), 4)
cut('death', (656, 986, 1436, 1075), 6)

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
    im = Image.fromarray(at); im.save(fn + '.webp', lossless=True, method=6); json.dump(meta, open(fn + '.json', 'w'), separators=(',', ':'))
    pv = Image.new('RGBA', im.size, (90, 40, 110, 255)); pv.alpha_composite(im); pv.save('build/whl/whl_prev.png')
    return meta
meta = pack(['idle', 'walk', 'bite', 'leap', 'dive', 'hit', 'death'], os.path.join(OUT, 'whl'))
print({k: len(v) for k, v in meta.items()})
