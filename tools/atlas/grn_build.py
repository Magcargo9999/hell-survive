"""영원의 온실주(챌린지 전용 보스, grn) 시트 → src/assets/grn/grn.webp + gh.json
자르기 · 배경 제거(가장자리에서 이어진 어두운 바탕을 투명하게) · 배율 조정만. 도트는 손대지 않는다.
사용: python3 grn_build.py <시트.png>   (시트: 지옥의 식물원 보스 컨셉 시트, 애니메이션 스프라이트 5줄)"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
src = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
# 줄 영역(y0,y1) · 각 칸의 몸통 중심 x (시트 좌표, 눈으로 잡음)
ROWS = {
    'idle':  ((338, 408), [731, 793, 855, 920, 984, 1047, 1110, 1175, 1241, 1313, 1388]),
    'move':  ((411, 480), [732, 805, 880, 955, 1040, 1110, 1200, 1270, 1350]),
    'attack': ((483, 557), [737, 830, 915, 1010, 1095, 1180, 1260, 1365]),
    'hit':   ((563, 630), [740, 832, 933, 1033, 1133, 1231]),
    'death': ((634, 708), [747, 830, 935, 1025, 1140, 1250, 1370]),
}
X0, X1 = 700, 1440

def fgmask(a, thr=34):
    dark = a.max(2) <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    bgish = np.abs(a - np.array([11, 12, 16])).max(2) <= 13   # 몸 사이에 갇힌 바탕(잎·뿌리 사이 검은 구멍)도 투명하게: 바탕색과 거의 같은 덩어리
    lb, nb = ndi.label(bgish)
    if nb:
        sb = ndi.sum(bgish, lb, range(1, nb + 1)); fg &= ~np.isin(lb, [i + 1 for i, q in enumerate(sb) if q >= 14])
    for y in range(a.shape[0]):   # 칸 사이 가로 구분선(가늘고 긴 줄) 제거
        pass
    lab2, n2 = ndi.label(fg)
    if n2:
        sz = ndi.sum(fg, lab2, range(1, n2 + 1)); fg &= ~np.isin(lab2, [i + 1 for i, s in enumerate(sz) if s < 5])
    return fg

frames = {}; out = []; y_off = 0; atlas_items = []
for name, ((y0, y1), cs) in ROWS.items():
    band = src[y0:y1, X0:X1]; fg = fgmask(band); col = fg.sum(0)
    cuts = [0]
    for a, b in zip(cs[:-1], cs[1:]):
        m = (a + b) // 2 - X0; lo, hi = max(1, m - 14), min(fg.shape[1] - 1, m + 14); cuts.append(lo + int(np.argmin(col[lo:hi])))
    cuts.append(fg.shape[1])
    L = []
    for i, c in enumerate(cs):
        xa, xb = cuts[i], cuts[i + 1]; sub = fg[:, xa:xb]; lab, n = ndi.label(ndi.binary_dilation(sub, iterations=2))
        # 가운데 몸통과 이어진 덩어리만 (이웃 칸 조각 제외)
        cx = c - X0 - xa; keep = np.zeros_like(sub)
        ids = set(np.unique(lab[:, max(0, cx - 4):cx + 5])) - {0}
        for k in ids: keep |= (lab == k) & sub
        if not keep.any(): keep = sub
        ys, xs = np.where(keep); ya, yb, xl, xr = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.zeros((yb - ya, xr - xl, 4), np.uint8)
        rgba[..., :3] = band[ya:yb, xa + xl:xa + xr]; rgba[..., 3] = (keep[ya:yb, xl:xr] * 255).astype(np.uint8)
        L.append((rgba, cx - xl, yb - ya))   # 앵커 x = 몸통 중심, 앵커 y = 발(뿌리 끝)
    frames[name] = L
# 한 줄에 줄별로 이어 붙이기
W = max(sum(f[0].shape[1] + 2 for f in L) for L in frames.values()); H = sum(max(f[0].shape[0] for f in L) + 2 for L in frames.values())
atlas = Image.new('RGBA', (W, H), (0, 0, 0, 0)); js = {}; y = 0
for name, L in frames.items():
    x = 0; rh = max(f[0].shape[0] for f in L); js[name] = []
    for rgba, ax, ay in L:
        atlas.paste(Image.fromarray(rgba), (x, y)); js[name].append([x, y, rgba.shape[1], rgba.shape[0], int(ax), int(ay)]); x += rgba.shape[1] + 2
    y += rh + 2
os.makedirs(os.path.join(ROOT, 'src/assets/grn'), exist_ok=True)
atlas.save(os.path.join(ROOT, 'src/assets/grn/grn.webp'), lossless=True)
json.dump(js, open(os.path.join(ROOT, 'src/assets/grn/grn.json'), 'w'), separators=(',', ':'))
prev = Image.new('RGBA', atlas.size, (60, 40, 90, 255)); prev.alpha_composite(atlas); prev = prev.resize((prev.width * 2, prev.height * 2), Image.NEAREST); prev.save(os.path.join(ROOT, 'build/grn/preview.png'))
print(atlas.size, {k: len(v) for k, v in js.items()})
