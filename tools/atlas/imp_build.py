"""황금 악마 임프(지하 21층~) 시트 → src/assets/imp/imp.webp + imp.json  (자르기 + 가장자리에서 이어진 어두운 배경 제거 + 칸 정렬만, 재색칠 없음)
프레임: idle 6 · run 9 · hit 4 · col(쓰러짐) 5   사용: python3 imp_build.py <임프 시트.png>   시트는 오른쪽을 본다"""
import sys, os, json
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sh = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(sh)
# 줄: (x0, y0, x1, y1, 자르는 x들)
ROWS = {
 'idle': (545, 95, 1448, 245, [676, 788, 925, 1078, 1225, 1360]),   # 칸 사이 중간 (아래 계산에서 사용)
 'run':  (545, 300, 1448, 440, [668, 774, 867, 975, 1075, 1176, 1264, 1348]),
 'hit':  (930, 490, 1448, 640, [1064, 1199, 1319]),
 'col':  (545, 695, 1448, 840, [685, 828, 1028, 1264]),
}
ROWS['idle'] = (545, 95, 1448, 245, [692, 855, 1000, 1155, 1290])
def cells(k):
    x0, y0, x1, y1, cuts = ROWS[k]; xs = [x0] + cuts + [x1]; return [(xs[i], y0, xs[i + 1], y1) for i in range(len(xs) - 1)]
out = {}; frames = {}
for k in ROWS:
    L = []
    for (a, b, c, d) in cells(k):
        reg = A[b:d, a:c].copy(); lum = reg[..., :3].max(axis=2)
        lab, n = ndimage.label(lum < 42)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(edge)); reg[..., 3] = np.where(bg, 0, 255)
        # 가장자리에 붙은 작은 부스러기·라벨 조각 제거: 가장 큰 덩어리와 이어진(팽창) 것만
        m = reg[..., 3] > 0; big = ndimage.binary_dilation(m, iterations=3); lab2, n2 = ndimage.label(big)
        if n2 > 1:
            sz = ndimage.sum(m, lab2, range(1, n2 + 1)); keep = 1 + int(np.argmax(sz)); reg[..., 3] = np.where((lab2 == keep) & m, 255, 0)
        im = Image.fromarray(reg); bb = im.getchannel('A').getbbox()
        body = np.array(im.getchannel('A'))[: max(1, (bb[3] - 18))]   # 몸통 가로 중심: 아래쪽 먼지 제외
        cols = np.where(body.sum(axis=0) > 0)[0]; cx = (cols.min() + cols.max()) / 2 if len(cols) else (bb[0] + bb[2]) / 2
        L.append((im.crop(bb), cx - bb[0], bb[3] - bb[1]))
    frames[k] = L
# 아틀라스: 그룹마다 한 줄, 칸 = 그 줄 최대 크기(앵커가 칸 안에 오도록 여유)
W = 0; y = 0; meta = {}; pos = []
for k, L in frames.items():
    cw = int(max(max(f[1], f[0].width - f[1]) for f in L) * 2) + 4; ch = max(f[0].height for f in L) + 4
    meta[k] = []
    for i, (im, cx, h) in enumerate(L):
        meta[k].append([i * cw, y, cw, ch, cw // 2, ch - 2]); pos.append((im, i * cw + int(cw // 2 - cx), y + ch - 2 - im.height))
    W = max(W, cw * len(L)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
os.makedirs(os.path.join(ROOT, 'src/assets/imp'), exist_ok=True)
at.save(os.path.join(ROOT, 'src/assets/imp/imp.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/imp/imp.json'), 'w'))
bg = Image.new('RGBA', at.size, (70, 60, 90, 255)); bg.alpha_composite(at); bg.save(os.path.join(ROOT, 'build/imp_prev.png')); print(at.size, {k: len(v) for k, v in meta.items()})
