"""v10.30 챌린지 황금 도망자(골든 러너) 시트 → src/assets/gold/gold.webp + gold.json
사용: python3 tools/atlas/gold_build.py <시트(마젠타 배경)>
자르기 · 마젠타 배경 제거 · 칸 테두리/구분선 제거만 (재색칠·배율 없음). 캐릭터 줄은 오른쪽을 본다.
그룹: idle6 run8 hit6 sab6 jack6 death4 · coin5 exp5 slime4 trap4 · slimeO trapO(설치된 장애물) · burst8 card5"""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
A = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
BG = np.array([250, 3, 251])
D = np.abs(A - BG).sum(2)
FG = D > 90

def cut(x0, y0, x1, y1, n=0, splits=(), name='', minw=6, keep_big=False, ranges=None):
    fg = FG[y0:y1, x0:x1].copy()
    col = fg.sum(0) > 0
    runs = []; s = None
    for i, c in enumerate(col):
        if c and s is None: s = i
        if not c and s is not None: runs.append([s, i - 1]); s = None
    if s is not None: runs.append([s, len(col) - 1])
    m2 = []
    for r in runs:
        if m2 and (r[1] - r[0] < minw or r[0] - m2[-1][1] < 7): m2[-1][1] = r[1]
        else: m2.append(r)
    if m2 and len(m2) > 1 and m2[0][1] - m2[0][0] < minw: m2[1][0] = m2[0][0]; m2.pop(0)
    for sx in splits:   # 직접 준 칸 경계는 합치기 뒤에 다시 가른다
        q = sx - x0
        for i, (ra, rb) in enumerate(m2):
            if ra < q < rb: m2[i:i + 1] = [[ra, q - 1], [q + 1, rb]]; break
    if ranges: m2 = [[ra - x0, rb - x0] for ra, rb in ranges]
    if n and len(m2) != n: raise SystemExit(f'{name}: {len(m2)} (기대 {n}) {[(x0 + a, x0 + b) for a, b in m2]}')
    out = []
    for a, b in m2:
        m = fg[:, a:b + 1]
        if keep_big:   # 가장 큰 덩어리 + 가까운 조각만 (옆 칸에서 넘어온 부스러기 제거)
            lab, k = ndi.label(ndi.binary_dilation(m, iterations=6)); sz = ndi.sum(m, lab, range(1, k + 1)); big = lab == (int(np.argmax(sz)) + 1); m = m & big
        ys = np.where(m.any(1))[0]; xs = np.where(m.any(0))[0]
        sub = A[y0 + ys.min():y0 + ys.max() + 1, x0 + a + xs.min():x0 + a + xs.max() + 1]
        mm = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        dd = D[y0 + ys.min():y0 + ys.max() + 1, x0 + a + xs.min():x0 + a + xs.max() + 1]
        al = np.where(mm, np.clip((dd - 90) / 60.0, 0, 1) * 255, 0)   # 배경과 섞인 가장자리만 반투명
        al[ndi.binary_erosion(mm, iterations=1)] = 255
        out.append(Image.fromarray(np.dstack([sub, al]).astype(np.uint8), 'RGBA'))
    return out

G = {}
G['idle'] = cut(190, 186, 1440, 282, 6, name='idle', keep_big=True)
G['run'] = cut(190, 288, 1440, 398, 8, name='run', keep_big=True)
G['hit'] = cut(190, 404, 1440, 516, 6, name='hit')
G['sab'] = cut(190, 523, 1168, 642, 6, splits=(1000,), name='sab')
G['slimeO'] = cut(1180, 558, 1312, 642, 1, name='slimeO', keep_big=True)
G['trapO'] = cut(1314, 558, 1446, 642, 1, name='trapO', keep_big=True)
G['jack'] = cut(190, 648, 1440, 770, 6, splits=(345, 505, 662, 836, 1052), name='jack')
G['death'] = cut(190, 776, 1440, 873, 4, name='death')
G['coin'] = cut(190, 916, 426, 972, 5, name='coin')
G['exp'] = cut(434, 916, 704, 972, 5, name='exp')
G['slime'] = cut(712, 916, 1064, 972, 4, splits=(856,), name='slime')
G['trap'] = cut(1072, 916, 1446, 972, 4, splits=(1163,), name='trap')
G['burst'] = cut(186, 1008, 948, 1086, 8, ranges=((190, 240), (245, 330), (335, 422), (424, 526), (527, 626), (627, 737), (740, 828), (830, 940)), name='burst')
G['card'] = cut(962, 1008, 1446, 1086, 5, splits=(1303,), name='card')

W = 1500; x = y = sh = 0; F = {}; items = []
for name, ims in G.items():
    for im in ims:
        w, h = im.size
        if x + w > W: x = 0; y += sh + 2; sh = 0
        items.append((name, im, x, y)); x += w + 2; sh = max(sh, h)
C = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0))
for name, im, xx, yy in items:
    C.alpha_composite(im, (xx, yy)); F.setdefault(name, []).append([xx, yy, im.size[0], im.size[1]])
C.save('src/assets/gold/gold.webp', lossless=True, method=6)
json.dump(F, open('src/assets/gold/gold.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', C.size, (40, 120, 70, 255)); bg.alpha_composite(C); bg.save('build/gold/prev.png')
print(C.size, {k: len(v) for k, v in F.items()})
