"""v7.13 말 미니보스 2종: 혈혼마 리고르(rig) · 네르칸(nerk).
시트(build/horse/rigor.png · nerkan.png)에서 프레임 칸을 균등 분할해 자르고 배경 제거(배경색과의 차이 → 알파, 속 구멍 메움)만 — 재색칠 없음.
출력: src/assets/horse/horse.webp(동작마다 한 줄) + horse.json(동작 → 프레임 [x, y, w, h, 기준x(몸 가운데), 기준y(발)])"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/horse/'; OUT = 'src/assets/horse/'; os.makedirs(OUT, exist_ok=True)
def mode_bg(c):
    q = (c.reshape(-1, 3) // 4).astype(int); k = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]; v, n = np.unique(k, return_counts=True); m = v[np.argmax(n)]
    return c.reshape(-1, 3)[k == m].mean(0)
def cut(S, box, lo=10, hi=26):
    x0, y0, x1, y1 = box; pad = 4; c = S[y0 - pad:y1 + pad, x0 - pad:x1 + pad]; BG = mode_bg(c)
    d = np.abs(c - BG).max(-1); core = d > hi; a = np.where(d <= lo, 0.0, np.where(core | ndi.binary_dilation(core, iterations=1), 1.0, (d - lo) / (hi - lo)))
    a[:pad] = 0; a[-pad:] = 0; a[:, :pad] = 0; a[:, -pad:] = 0
    m = a > 0.3; lab, n = ndi.label(ndi.binary_dilation(m, iterations=2), structure=np.ones((3, 3))); h, w = a.shape
    cen = lab[int(h * 0.3):int(h * 0.8), int(w * 0.3):int(w * 0.7)]; cnt = np.bincount(cen[cen > 0]) if (cen > 0).any() else np.array([0])
    keep = {int(np.argmax(cnt))} if cnt.max() > 0 else set(); keepm = np.isin(lab, list(keep)); keepm &= ndi.binary_dilation(m, iterations=2)
    a[~keepm] = 0
    solid = ndi.binary_fill_holes(a > 0.3); a = np.maximum(a, solid.astype(float) * (keepm | solid))   # 어두운 몸통 속 구멍 메움
    A = np.clip(a, 0, 1)[..., None]
    with np.errstate(divide='ignore', invalid='ignore'): u = np.where(A > 0.999, c, (c - BG * (1 - A)) / np.maximum(A, 1e-3))
    r = np.dstack([np.clip(u, 0, 255).astype(np.uint8), (A[..., 0] * 255).astype(np.uint8)]); ys, xs = np.where(r[..., 3] > 8)
    return r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
# 동작 이름 · x0 · x1 · y0 · y1 · 칸 수
RIG = [('idle', 520, 1185, 48, 168, 4), ('walk', 517, 1440, 207, 297, 8), ('dash', 512, 1512, 338, 428, 6), ('slash', 512, 1512, 466, 556, 6), ('curse', 512, 1512, 590, 696, 7), ('hit', 508, 878, 744, 834, 4), ('death', 898, 1516, 744, 834, 6)]
NER = [('idle', 592, 858, 328, 400, 4), ('walk', 878, 1430, 328, 400, 8), ('atk', 596, 1426, 452, 520, 6), ('dash', 542, 946, 572, 654, 6), ('summon', 966, 1430, 572, 654, 8), ('howl', 546, 1430, 708, 810, 8), ('hit', 532, 810, 862, 924, 4), ('death', 832, 1426, 862, 924, 6)]
SHEETS = {'rig': ('rigor.png', RIG, 1.0), 'nerk': ('nerkan.png', NER, 2.0)}   # 네르칸은 작아서 정수 2배(NEAREST)
rows = []; meta = {}
for key, (f, spec, mul) in SHEETS.items():
    S = np.array(Image.open(IN + f).convert('RGB')).astype(float); meta[key] = {}
    for an, x0, x1, y0, y1, n in spec:
        cw = (x1 - x0) / n; fr = []
        for i in range(n):
            c = cut(S, (round(x0 + i * cw), y0, round(x0 + (i + 1) * cw), y1))
            if mul != 1: c = np.array(Image.fromarray(c).resize((c.shape[1] * int(mul), c.shape[0] * int(mul)), Image.NEAREST))
            fr.append(c)
        rows.append((key, an, fr))
# 아틀라스: 줄마다 한 동작, 프레임은 가로로. 기준점 = (프레임 가운데 x, 바닥 y)
PAD = 2; W = max(sum(c.shape[1] + PAD for c in fr) for _, _, fr in rows); H = sum(max(c.shape[0] for c in fr) + PAD for _, _, fr in rows)
at = np.zeros((H, W, 4), np.uint8); y = 0
for key, an, fr in rows:
    h = max(c.shape[0] for c in fr); x = 0; out = []
    for c in fr:
        ch, cw2 = c.shape[:2]; at[y + h - ch:y + h, x:x + cw2] = c; out.append([x, y + h - ch, cw2, ch, cw2 / 2, ch]); x += cw2 + PAD
    meta[key][an] = out; y += h + PAD
Image.fromarray(at).save(OUT + 'horse.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'horse.json', 'w'), separators=(',', ':'))
print(at.shape, {k: {a: [(f[2], f[3]) for f in v][:3] for a, v in m.items()} for k, m in meta.items()})
bg = Image.new('RGBA', (W, H), (70, 70, 80, 255)); bg.alpha_composite(Image.fromarray(at)); bg.save('build/horse/atlas_view.png')
