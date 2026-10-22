"""스킨 시트 → 아틀라스 + 일러스트. 자르기·배경 제거만 (색 수정 없음).
사용: python3 tools/atlas/skin_build.py <악마사냥꾼(레어) 시트> <지옥늑대 시트> <악마사냥꾼(에픽) 시트>
 → src/assets/skin/{gunH, gunE, wolfE}.{webp,json} + {gunH,gunE,wolfE}_art.webp
※ v8.04: 배경 판정 밝기(thr)를 낮췄다 — 어두운 검은 옷이 투명하게 뚫리던 문제(thr 34 → 16~20) + 틈 닫기(close)
프레임 [x, y, w, h, 기준x(몸통 가운데), 기준y(발)] — 키 이름은 게임 쪽 동작 이름과 같게 둔다"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin'); os.makedirs(OUT, exist_ok=True)
def build(src, name, rows, art, thr=34, close=0):   # thr: 배경으로 볼 최대 밝기(어두운 옷이 잘리지 않게 낮게 · v8.04부터 16~22)
    A = np.array(Image.open(src).convert('RGBA')); RGB = A[:, :, :3].astype(int)
    tiles, frames = [], {}
    for k, (ry0, y1, cells) in rows.items():
        frames[k] = []
        for cell in cells:
            x0, x1 = cell[0], cell[1]; y0 = cell[2] if len(cell) > 2 else ry0   # 칸마다 위쪽을 따로 정할 수 있다(제목 글자 피하기)
            m = RGB[y0:y1, x0:x1].max(axis=2) > thr
            lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
            mx = sz.max(); ok = []
            for i, sl in enumerate(nd.find_objects(lab)):   # 칸 가장자리에 걸린 이웃 그림 조각(작은 것)은 버린다
                edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
                thin = (sl[1].stop - sl[1].start) <= 4 and (sl[0].stop - sl[0].start) >= 20   # 패널 테두리 선
                if sz[i] >= 25 and not thin and not (edge and sz[i] < 0.2 * mx): ok.append(i + 1)
            keep = np.isin(lab, ok)
            if close: keep = nd.binary_closing(np.pad(keep, close + 2), structure=np.ones((3, 3)), iterations=close)[close + 2:-(close + 2), close + 2:-(close + 2)] | keep   # 닫기: 가는 틈을 메워 구멍 메우기가 잘 되게
            keep = nd.binary_fill_holes(keep)
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
hunter, wolf, hunterE = sys.argv[1], sys.argv[2], sys.argv[3]
# 악마 사냥꾼 (악마 총잡이 최종 진화 스킨): 원본은 오른쪽을 본다 — 게임 키 i2 w2 a2 r2 h2 d2 s2
build(hunter, 'gunH', {
    'i2': (45, 156, [(796, 911)]),
    'w2': (208, 322, [(729, 813), (818, 914)]),
    'a2': (386, 484, [(536, 622), (622, 712), (712, 797), (797, 882), (882, 967), (967, 1064)]),
    'r2': (545, 660, [(538, 615), (615, 698), (698, 780), (780, 862), (862, 948), (948, 1055)]),
    'h2': (712, 808, [(23, 107), (115, 205), (209, 297), (303, 405), (405, 511)]),
    'd2': (712, 808, [(543, 640), (640, 740), (740, 890), (890, 1055)]),
    's2': (858, 962, [(15, 205), (212, 400), (408, 700), (708, 895), (905, 1074)]),
}, (14, 92, 352, 668), thr=16, close=1)
# 지옥늑대 (지옥 늑대 스킨): 이동·공격 줄은 오른쪽, 피격·사망 줄은 왼쪽을 본다 · 대기는 정면 3칸
build(wolf, 'wolfE', {
    'idle': (15, 148, [(145, 228), (246, 332), (826, 909)]),
    'walk': (160, 292, [(128, 232), (232, 352), (352, 475), (475, 595), (595, 715), (715, 838), (838, 960), (960, 1080)]),
    'attack': (305, 462, [(129, 250), (250, 405), (405, 575), (584, 750), (752, 945), (950, 1120)]),
    'hit': (465, 598, [(145, 283), (318, 450), (476, 622), (640, 800)]),
    'death': (615, 722, [(138, 280), (296, 450), (459, 602), (612, 749), (760, 895), (895, 1045)]),
}, (1118, 280, 1526, 738), thr=20, close=1)
# 악마 사냥꾼 에픽 (청염): 시트 1448x1086, 원본은 오른쪽을 본다 · 롤 6칸(오른쪽 끝 사망 롤 패널은 안 쓴다)
build(hunterE, 'gunE', {
    'i2': (42, 150, [(752, 870)]),
    'w2': (205, 318, [(697, 786), (787, 876)]),
    'a2': (385, 483, [(515, 600), (600, 679), (679, 758), (758, 837), (837, 916), (916, 998)]),
    'r2': (543, 658, [(515, 595), (596, 675), (676, 752), (752, 832), (832, 913), (910, 998)]),
    'h2': (714, 818, [(22, 104), (104, 196), (196, 284), (284, 379), (379, 495)]),
    'd2': (714, 818, [(515, 588), (589, 684), (684, 836), (836, 994)]),
    's2': (862, 1002, [(36, 202, 893), (202, 356), (356, 506), (506, 736), (738, 900), (905, 1066)]),
}, (10, 10, 345, 668), thr=20, close=1)
