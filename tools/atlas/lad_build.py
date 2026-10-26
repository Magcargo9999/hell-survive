"""가시관 무당벌레(지옥 식물원 15층 · 원예의 여왕 판 미니 보스) 시트 → 아틀라스 (자르기·배경 제거(체크무늬 마스크)만, 색 수정 없음)
사용: python3 tools/atlas/lad_build.py <시트.png> → src/assets/lad/lad.{webp,json}
시트는 체크무늬 배경이 그림에 박혀 있다 → 무채색(채도 낮은 밝은 회색·흰색)을 배경으로 지우고, 그 가장자리에 남은 밝은 무채색 테두리도 두 번 깎는다.
프레임 [x, y, w, h, 기준x(몸 가운데), 기준y(발)] · 시트는 오른쪽을 본다(게임에서 face<0이면 뒤집음)
그룹: port 4(큰 일러스트: 정면·옆·등·날개) · idle 6 · walk 9 · wing 3(날개 펴기·구슬 뱉기) · hover 4 · curl 1(공 모양) · bite 3 · arc 2(뿔 휘두른 호) · spike 1(가시 분출) · boom 1(폭발 연기) · bits 1 · death 9 · ball 7(점박이 구슬)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/lad'); os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.join(ROOT, 'build/lad'), exist_ok=True)
im = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); mx = im.max(2); mn = im.min(2)
bg = ((mx - mn) <= 12) & (mn >= 200)
for _ in range(2):   # 가장자리의 밝은 무채색 테두리(체크무늬와 섞인 안티앨리어싱)
    fr = ((mx - mn) <= 30) & (mn >= 165) & nd.binary_dilation(bg, structure=np.ones((3, 3)))
    bg = bg | fr
fg = ~bg
lab, n = nd.label(fg, structure=np.ones((3, 3))); sz = nd.sum(fg, lab, range(1, n + 1))
fg = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s >= 12])
A = np.zeros(im.shape[:2] + (4,), np.uint8); A[..., :3] = im; A[..., 3] = fg * 255
# 줄 → (y0, y1, [경계들], 이름 목록, 경계 다듬기 여부)
def vsplit(y0, y1, b, win=18):
    occ = fg[y0:y1].sum(axis=0); b = list(b)
    for i in range(1, len(b) - 1):
        lo, hi = b[i] - win, b[i] + win; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; b[i] = lo + int(xs[len(xs) // 2])
    return b
ROWS = [
  ('port', 13, 293, [4, 328, 722, 1005, 1530], False),
  ('idle', 299, 391, [4, 150, 295, 432, 571, 716], True),   # 앞 6칸만 (옆모습 · 오른쪽)
  ('walk', 406, 491, [4, 121, 244, 380, 512, 647, 785, 915, 1035, 1135], True),
  ('wing', 504, 661, [4, 163, 322, 592], True),
  ('hover', 504, 661, [592, 770, 962, 1162, 1345], True),
  ('curl', 504, 661, [1345, 1530], False),
  ('bite', 670, 795, [4, 159, 335, 507], True),
  ('arc', 670, 795, [507, 649, 861], True),
  ('spike', 670, 795, [861, 1103], False),
  ('boom', 670, 795, [1103, 1330], False),
  ('bits', 670, 795, [1330, 1530], False),
  ('death', 807, 930, [4, 151, 310, 480, 638, 805, 968, 1088, 1268, 1530], True),
  ('ball', 943, 1002, [885, 990, 1090, 1180, 1300, 1384, 1480, 1530], True),
]
tiles = []
for k, y0, y1, bnd, rf in ROWS:
    if rf: bnd = vsplit(y0, y1, bnd)
    for i in range(len(bnd) - 1):
        x0, x1 = bnd[i], bnd[i + 1]; m = fg[y0:y1, x0:x1]
        ys, xs = np.where(m)
        if not len(xs): continue
        X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[..., :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]; t[..., 3] = m[Y0:Y1, X0:X1] * 255
        low = ys >= Y0 + 0.82 * (Y1 - Y0); ax = int(round(float(np.median(xs[low])) - X0)) if low.any() else t.shape[1] // 2
        if k in ('arc', 'boom', 'bits', 'spike', 'port', 'curl', 'ball', 'death'): ax = t.shape[1] // 2
        tiles.append((k, Image.fromarray(t), ax, t.shape[0]))
W = 1500; x = y = rh = 0; place = []; F = {}
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place: out.paste(t, (x, y)); F.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'lad.webp'), lossless=True); json.dump(F, open(os.path.join(OUT, 'lad.json'), 'w'))
print(out.size, {k: len(v) for k, v in F.items()})
b2 = Image.new('RGBA', out.size, (60, 90, 70, 255)); b2.alpha_composite(out); b2.save(os.path.join(ROOT, 'build/lad/atlas_prev.png'))
