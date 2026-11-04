"""v10.26 8지옥 '타르타로스' 잡몹 5종 → src/assets/tar/tmob.webp (4프레임 × 5종, 칸 108×114, 발 아래·가운데 맞춤) + tmob.json([이름, 키])
시트: 9지옥(→8지옥으로 사용) 필드 몬스터 스프라이트 시트(1448×1086, 마젠타 배경) — 판마다 오른쪽 '이동/공격 4프레임'만 쓴다. 자르기 · 배경 제거 · 배율 조정만 (재색칠 없음).
  → 안 쓰는 대기 4프레임·대표 큰 그림은 src/assets/tar/tmob_spare.webp + tmob_spare.json 에 그대로 보관 (게임이 불러오지 않음)
사용: python3 tools/atlas/tmob_build.py <몬스터 시트>"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = sys.argv[1]; OUT = 'src/assets/tar/'; os.makedirs('build/h9', exist_ok=True)
A = np.array(Image.open(SRC).convert('RGB')).astype(int); BG = np.array([252, 3, 252]); CW, CH = 108, 114
NAMES = ['속박 간수', '형벌 해골병', '심연 사냥개', '타르타로스 원혼', '낙뢰석 골렘']
ROWY = [(195, 335), (385, 510), (560, 683), (738, 862), (925, 1052)]   # 이동/공격 줄(세로) — 칸 제목·테두리선 제외
MOVEX = (948, 1446); IDLEX = (540, 940); BIGX = (225, 415); ICONX = (418, 530)

def frames_of(a, n=4):
    """몸 덩어리(면적 2000+) n개를 왼쪽부터 + 몸 둘레 10px 안 작은 조각(이펙트)만 — 테두리선·모서리 장식은 버림"""
    fg = np.abs(a - BG).sum(2) > 90; lab, k = ndi.label(fg); sz = ndi.sum(fg, lab, range(1, k + 1))
    bodies = [j + 1 for j in range(k) if sz[j] >= 2000]
    if len(bodies) != n: raise SystemExit(f'몸 {len(bodies)}개 (기대 {n})')
    bodies.sort(key=lambda j: np.where((lab == j).any(0))[0][0]); out = []
    for j in bodies:
        main = lab == j; near = ndi.binary_dilation(main, iterations=10)
        keep = np.isin(lab, [t + 1 for t in range(k) if (near & (lab == t + 1)).any() and (t + 1 == j or (sz[t] < 2000 and sz[t] >= 8))])
        ys, xs = np.where(keep); sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; m = keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        out.append(Image.fromarray(np.dstack([sub.astype(np.uint8), (m * 255).astype(np.uint8)]), 'RGBA'))
    return out

def fit(sps, maxh=104, maxw=104):
    k = min(min(maxh / s.size[1], maxw / s.size[0]) for s in sps); res = []; nh = 0
    for sp in sps:
        w, h = sp.size; nw, nh2 = max(1, round(w * k)), max(1, round(h * k)); s2 = sp.resize((nw, nh2), Image.LANCZOS)
        c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.alpha_composite(s2, ((CW - nw) // 2, CH - 2 - nh2)); res.append(c); nh = max(nh, nh2)
    return res, nh

cells, meta, spare, spk = [], [], {}, {}
for i, ((y0, y1), nm) in enumerate(zip(ROWY, NAMES)):
    fr = frames_of(A[y0:y1, MOVEX[0]:MOVEX[1]])
    c4, nh = fit(fr); cells.append(c4); meta.append([nm, nh])
    # 보관: 대기 4프레임
    try: spare[nm + '·대기'] = frames_of(A[y0:y1, IDLEX[0]:IDLEX[1]])
    except SystemExit as e: print('대기 건너뜀', nm, e)
At = Image.new('RGBA', (CW * len(cells), CH * 4), (0, 0, 0, 0))
for i, fr in enumerate(cells):
    for k, c in enumerate(fr): At.alpha_composite(c, (i * CW, k * CH))
At.save(OUT + 'tmob.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'tmob.json', 'w'), ensure_ascii=False)
# 보관용 (대기 프레임)
x = y = sh = 0; items = []
for nm, ims in spare.items():
    for im in ims:
        w, h = im.size
        if x + w > 1024: x = 0; y += sh + 2; sh = 0
        items.append((nm, im, x, y)); x += w + 2; sh = max(sh, h)
S = Image.new('RGBA', (1024, y + sh), (0, 0, 0, 0)); sj = {}
for nm, im, xx, yy in items: S.alpha_composite(im, (xx, yy)); sj.setdefault(nm, []).append([xx, yy, im.size[0], im.size[1]])
S.save(OUT + 'tmob_spare.webp', lossless=True, method=6); json.dump(sj, open(OUT + 'tmob_spare.json', 'w'), ensure_ascii=False, separators=(',', ':'))
bg = Image.new('RGBA', At.size, (90, 60, 120, 255)); bg.alpha_composite(At); bg.resize((At.width * 2, At.height * 2), Image.NEAREST).save('build/h9/tmob_prev.png')
print(meta, At.size, S.size)
