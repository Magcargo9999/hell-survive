"""릴세르카 이펙트 시트(어두운 남색 배경) → src/assets/lil/lilfx.webp + lilfx.json (v9.23)
칸을 자르고, 어두운 배경은 밝기에 따라 투명하게만 한다(색은 그대로 · 재색칠 없음, 글로우는 'lighter'로 그린다)
그룹: chand 5 · needle 4 · nstar 4 · refl 4 · rstar 4 · beam 5 · bfloor 5 · eye 6 · bhead · bshaft · bend · gspike 6 · bpat 4 · bliz 4 · zone 5 · crack 5
사용: python3 lilfx_build.py <이펙트 시트.png>"""
import sys, os, json
from PIL import Image
import numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
A = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
def cut(b, soft=True):
    x0, y0, x1, y1 = b; reg = A[y0:y1, x0:x1]; L = reg.max(axis=2)
    a = np.clip((L - 22) / 60.0, 0, 1) if soft else np.full(L.shape, 1.0)
    out = np.dstack([reg.astype(np.uint8), (a * 255).astype(np.uint8)]); im = Image.fromarray(out, 'RGBA')
    bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    return im, bb
G = {}
def add(name, boxes, mode='c', soft=True, anchors=None, trim=True):
    L = []
    for i, b in enumerate(boxes):
        im, bb = cut(b, soft)
        if trim and bb: im = im.crop(bb)
        else: bb = (0, 0) + im.size
        w, h = im.size
        if anchors: ax, ay = anchors[i][0] - (b[0] + (bb[0] if trim else 0)), anchors[i][1] - (b[1] + (bb[1] if trim else 0))
        elif mode == 'c': ax, ay = w / 2, h / 2
        elif mode == 'b': ax, ay = w / 2, h
        L.append((im, ax, ay))
    G[name] = L
add('chand', [(28, 50, 192, 288), (198, 42, 308, 292), (322, 44, 432, 272), (448, 46, 556, 292), (575, 48, 800, 292)], 'b')
RX = [(822, 866), (866, 927), (927, 996), (996, 1062), (1062, 1132), (1134, 1204), (1210, 1304), (1305, 1436)]
add('needle', [(a, 40, b, 160) for a, b in RX[:4]]); add('nstar', [(a, 35, b, 165) for a, b in RX[4:]])
add('refl', [(a, 200, b, 298) for a, b in RX[:4]]); add('rstar', [(a, 188, b, 300) for a, b in RX[4:]])
SX = [(20, 130), (142, 260), (267, 400), (410, 545), (552, 730)]
add('beam', [(a, 352, b, 533) for a, b in SX], 'b'); add('bfloor', [(a, 530, b, 652) for a, b in SX])
EX = [(768, 836), (848, 926), (946, 1026), (1056, 1168), (1176, 1310), (1320, 1428)]
add('eye', [(a, 345, b, 452) for a, b in EX])
add('bhead', [(760, 458, 858, 552)], anchors=[(797, 500)]); add('bshaft', [(1100, 480, 1200, 520)], anchors=[(1100, 500)]); add('bend', [(1270, 430, 1436, 558)], anchors=[(1347, 498)])
GS = [(758, 557, 856, 650), (882, 557, 958, 650), (968, 557, 1052, 650), (1066, 557, 1148, 650), (1160, 557, 1256, 650), (1266, 557, 1436, 650)]
add('gspike', GS, 'b')
add('bpat', [(15, 735, 120, 850), (120, 735, 230, 850), (230, 735, 338, 850), (338, 712, 472, 858)])
add('bliz', [(905, 748, 1025, 840), (1035, 722, 1178, 840), (1185, 722, 1300, 840), (1308, 712, 1440, 840)], 'b')
add('zone', [(18, 940, 136, 1050), (142, 925, 262, 1064), (270, 915, 388, 1064), (398, 905, 534, 1064), (545, 896, 694, 1064)])
CK = [(738, 908, 818, 1062), (820, 908, 962, 1062), (968, 908, 1108, 1062), (1114, 908, 1268, 1062), (1274, 908, 1432, 1062)]
add('crack', CK, soft=False, trim=False)
meta = {}; pos = []; W = 0; y = 0
for k, Lf in G.items():
    cw = max(im.width for im, _, _ in Lf) + 4; ch = max(im.height for im, _, _ in Lf) + 4; meta[k] = []
    for i, (im, ax, ay) in enumerate(Lf):
        ox = i * cw + 2; oy = y + 2; meta[k].append([i * cw, y, cw, ch, round(ax) + 2, round(ay) + 2]); pos.append((im, ox, oy))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
at.save(os.path.join(ROOT, 'src/assets/lil/lilfx.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/lil/lilfx.json'), 'w'))
from PIL import ImageDraw
b2 = Image.new('RGBA', at.size, (60, 90, 70, 255)); b2.alpha_composite(at); d = ImageDraw.Draw(b2)
for kn, ms in meta.items():
    for m in ms: d.ellipse([m[0] + m[4] - 2, m[1] + m[5] - 2, m[0] + m[4] + 2, m[1] + m[5] + 2], fill=(255, 0, 0, 255))
b2.save(os.path.join(ROOT, 'build/lilfx_prev.png')); print(at.size, {k: len(v) for k, v in meta.items()})
