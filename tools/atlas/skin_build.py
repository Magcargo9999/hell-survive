"""스킨 시트 → 아틀라스 + 일러스트. 자르기·배경 제거만 (색 수정 없음).
사용: python3 tools/atlas/skin_build.py <악마사냥꾼 시트> <지옥늑대 시트>
 → src/assets/skin/{gunH.webp, gunH.json, gunH_art.webp, wolfE.webp, wolfE.json, wolfE_art.webp}
프레임 [x, y, w, h, 기준x(몸통 가운데), 기준y(발)] — 키 이름은 게임 쪽 동작 이름과 같게 둔다"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin'); os.makedirs(OUT, exist_ok=True)
def build(src, name, rows, art, thr=34):
    A = np.array(Image.open(src).convert('RGBA')); RGB = A[:, :, :3].astype(int)
    tiles, frames = [], {}
    for k, (y0, y1, cells) in rows.items():
        frames[k] = []
        for (x0, x1) in cells:
            m = RGB[y0:y1, x0:x1].max(axis=2) > thr
            lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
            mx = sz.max(); ok = []
            for i, sl in enumerate(nd.find_objects(lab)):   # 칸 가장자리에 걸린 이웃 그림 조각(작은 것)은 버린다
                edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
                thin = (sl[1].stop - sl[1].start) <= 4 and (sl[0].stop - sl[0].start) >= 20   # 패널 테두리 선
                if sz[i] >= 25 and not thin and not (edge and sz[i] < 0.2 * mx): ok.append(i + 1)
            keep = np.isin(lab, ok); keep = nd.binary_fill_holes(keep)
            big = lab == (int(np.argmax(sz)) + 1)
            ys, xs = np.where(keep); by, bx = np.where(big)
            X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
            t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * 255
            tiles.append((k, len(frames[k]), Image.fromarray(t), int(round((bx.min() + bx.max()) / 2)) - X0, int(Y1 - Y0))); frames[k].append(None)
    W = 1024; x = y = rh = 0; place = []
    for k, i, t, ax, ay in tiles:
        if x + t.width > W: x = 0; y += rh + 2; rh = 0
        place.append((k, i, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
    out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
    for k, i, t, x, y, ax, ay in place: out.paste(t, (x, y)); frames[k][i] = [int(v) for v in (x, y, t.width, t.height, ax, ay)]
    out.save(os.path.join(OUT, name + '.webp'), lossless=True)
    json.dump(frames, open(os.path.join(OUT, name + '.json'), 'w'))
    Image.open(src).convert('RGB').crop(art).save(os.path.join(OUT, name + '_art.webp'), quality=90)
    print(name, out.size, {k: len(v) for k, v in frames.items()})
hunter, wolf = sys.argv[1], sys.argv[2]
# 악마 사냥꾼 (악마 총잡이 최종 진화 스킨): 원본은 오른쪽을 본다 — 게임 키 i2 w2 a2 r2 h2 d2 s2
build(hunter, 'gunH', {
    'i2': (45, 156, [(796, 911)]),
    'w2': (208, 322, [(729, 813), (818, 914)]),
    'a2': (386, 484, [(536, 622), (622, 712), (712, 797), (797, 882), (882, 967), (967, 1064)]),
    'r2': (545, 660, [(538, 615), (615, 698), (698, 780), (780, 862), (862, 948), (948, 1055)]),
    'h2': (712, 808, [(23, 107), (115, 205), (209, 297), (303, 405), (405, 511)]),
    'd2': (712, 808, [(543, 640), (640, 740), (740, 890), (890, 1055)]),
    's2': (858, 962, [(15, 205), (212, 400), (408, 700), (708, 895), (905, 1074)]),
}, (14, 92, 352, 668))
# 지옥늑대 (지옥 늑대 스킨): 이동·공격 줄은 오른쪽, 피격·사망 줄은 왼쪽을 본다 · 대기는 정면 3칸
build(wolf, 'wolfE', {
    'idle': (15, 148, [(145, 228), (246, 332), (826, 909)]),
    'walk': (160, 292, [(128, 232), (232, 352), (352, 475), (475, 595), (595, 715), (715, 838), (838, 960), (960, 1080)]),
    'attack': (305, 462, [(129, 250), (250, 405), (405, 575), (584, 750), (752, 945), (950, 1120)]),
    'hit': (465, 598, [(145, 283), (318, 450), (476, 622), (640, 800)]),
    'death': (615, 722, [(138, 280), (296, 450), (459, 602), (612, 749), (760, 895), (895, 1045)]),
}, (1118, 280, 1526, 738))
