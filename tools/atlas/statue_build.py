"""v8.06 부패한 성상(타락천사 판 미니 보스): 시트 칸 자르기 + 배경 제거만 (재색칠 없음).
사용: python3 tools/atlas/statue_build.py build/statue/statue.png → src/assets/statue/statue.webp + statue.json
JSON: 동작 → 프레임 [x, y, w, h, 기준x(몸 가운데·발), 기준y(발)] · 이펙트(fx 칸)은 기준 = (가운데, 바닥)
패널 테두리(구릿빛 선)는 색으로 알아보고 지운다 (몸 색은 흰·붉은색이라 겹치지 않는다)."""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/statue'); os.makedirs(OUT, exist_ok=True)
S = np.array(Image.open(sys.argv[1]).convert('RGB')); RGB = S.astype(int)
R, G, B = RGB[..., 0], RGB[..., 1], RGB[..., 2]
bronze = (R > 90) & (R < 235) & (G > 55) & (G < 170) & (B > 20) & (B < 120) & (R - B > 50) & (G - B > 20) & (R - G > 10) & (R - G < 80)
bright = RGB.max(axis=2) > 24
# 구릿빛 테두리 선: 가로로 길게 이어지는 줄을 지운다 (가로 15칸 이상 연속된 구릿빛)
lines = nd.binary_opening(bronze, structure=np.ones((1, 15))); lines = nd.binary_dilation(lines, structure=np.ones((3, 5)))
mask0 = bright & ~(lines & bronze)
# 이름표(제목) 글자 판: 흰 글자 — 칸의 y 범위를 글자 아래로 잡아 피한다
# 동작 · y0 · y1 · 칸 경계(왼→오) — 칸별 y0 를 따로 줄 수 있다: (x0, x1, y0)
rows = {
 'idle':  (48, 147,  [(600,715),(715,835),(835,938),(938,1042),(1042,1152),(1152,1255),(1255,1344)]),
 'walk':  (188, 269, [(600,735),(735,875),(875,980),(980,1088),(1088,1200),(1200,1344)]),
 'atk':   (314, 409, [(600,710),(710,855),(855,1010),(1010,1195),(1195,1344,306)]),
 'p1':    (430, 546, [(600,718,462),(718,845,462),(845,977),(977,1122),(1122,1344)]),
 'p2':    (575, 676, [(600,720,594),(720,842,594),(842,938),(938,1058),(1058,1195),(1195,1344)]),
 'hit':   (706, 769, [(600,740),(740,890),(890,1030),(1030,1200)]),
 'death': (809, 868, [(600,742,812),(742,890),(890,1048),(1048,1205),(1205,1344)]),
}
FX = {'p1': (2, 3, 4), 'p2': (2, 3, 4, 5)}   # 이펙트 칸 번호: 기준 = (가운데, 바닥) · 몸 칸: 발 가운데
tiles = []; meta = {}
for k, (ry0, y1, cells) in rows.items():
    meta[k] = []
    for i, c in enumerate(cells):
        x0, x1 = c[0], c[1]; y0 = c[2] if len(c) > 2 else ry0
        m = mask0[y0:y1, x0:x1].copy(); lab, n = nd.label(m, structure=np.ones((3, 3))); sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max()
        ok = []
        for j, sl in enumerate(nd.find_objects(lab)):
            edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
            if sz[j] >= 14 and not (edge and sz[j] < 0.2 * mx) and not (sz[j] < 0.02 * mx): ok.append(j + 1)
        keep = np.isin(lab, ok)
        keep = nd.binary_closing(np.pad(keep, 4), structure=np.ones((3, 3)), iterations=1)[4:-4, 4:-4] | keep
        # 가는 가로선(남은 테두리 조각) 지우기: 가로로 12칸 이상 이어지고 두께가 3 미만인 부분
        hl = nd.binary_opening(keep, structure=np.ones((1, 12))); thick = nd.binary_dilation(nd.binary_opening(keep, structure=np.ones((3, 3))), iterations=1)
        keep &= ~(hl & ~thick)
        # 구멍 메우기는 작은 구멍만 (다리 사이 같은 곳) — 큰 빈 곳(베기 곡선 안쪽)은 비워 둔다
        hole = nd.binary_fill_holes(keep) & ~keep; hl2, hn = nd.label(hole); hs = nd.sum(hole, hl2, range(1, hn + 1))
        keep |= np.isin(hl2, [j + 1 for j in range(hn) if hs[j] <= 140])
        lab2, n2 = nd.label(keep, structure=np.ones((3, 3))); s2 = nd.sum(keep, lab2, range(1, n2 + 1)); sl2 = nd.find_objects(lab2)
        keep = np.isin(lab2, [j + 1 for j in range(n2) if s2[j] >= 14 and not ((sl2[j][0].stop - sl2[j][0].start) <= 4 and (sl2[j][1].stop - sl2[j][1].start) >= 8)])   # 떨어진 가는 가로 조각(테두리 잔여)은 버린다
        ys, xs = np.where(keep); X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = S[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * 255
        # 기준: 몸 칸 = 맨 아래 12% 줄의 가운데(발), 이펙트 칸 = 전체 가운데
        if i in FX.get(k, ()): ax = (X1 - X0) / 2
        else:
            low = np.where(keep[max(Y0, Y1 - 1 - max(4, (Y1 - Y0) // 8)):Y1, X0:X1].any(axis=0))[0]; ax = float(low.mean()) if len(low) else (X1 - X0) / 2
        tiles.append((k, Image.fromarray(t), ax)); meta[k].append(None)
W = 1024; x = y = rh = 0; place = []
for k, t, ax in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0)); cnt = {k: 0 for k in rows}
for k, t, x, y, ax in place:
    out.paste(t, (x, y)); meta[k][cnt[k]] = [int(x), int(y), t.width, t.height, round(ax, 1), t.height]; cnt[k] += 1
out.save(os.path.join(OUT, 'statue.webp'), lossless=True, method=6); json.dump(meta, open(os.path.join(OUT, 'statue.json'), 'w'), separators=(',', ':'))
bg = Image.new('RGBA', out.size, (70, 70, 80, 255)); bg.alpha_composite(out); bg.resize((out.width * 2, out.height * 2), Image.NEAREST).save('/tmp/claude-0/statue_view.png')
print(out.size, {k: len(v) for k, v in meta.items()})
