"""스킨 시트 → 아틀라스 + 일러스트. 자르기·배경 제거만 (색 수정 없음).
사용: python3 tools/atlas/skin_build.py <악마사냥꾼(레어) 시트> <지옥늑대 시트> <악마사냥꾼(에픽) 시트> [현무 리저드 시트]
 → src/assets/skin/{gunH, gunE, wolfE}.{webp,json} + {gunH,gunE,wolfE}_art.webp
※ v8.04: 배경 판정 밝기(thr)를 낮췄다 — 어두운 검은 옷이 투명하게 뚫리던 문제(thr 34 → 16~20) + 틈 닫기(close)
프레임 [x, y, w, h, 기준x(몸통 가운데), 기준y(발)] — 키 이름은 게임 쪽 동작 이름과 같게 둔다"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin'); os.makedirs(OUT, exist_ok=True)
def build(src, name, rows, art, thr=34, close=0, valley=0, holemax=0, thin=False, hline=False):   # thr: 배경으로 볼 최대 밝기(어두운 옷이 잘리지 않게 낮게 · v8.04부터 16~22)
    if src == '-': return   # 시트를 '-'로 주면 건너뛴다
    A = np.array(Image.open(src).convert('RGBA')); RGB = A[:, :, :3].astype(int)
    tiles, frames = [], {}
    if valley:   # v8.04: 칸 경계를 '그림이 가장 비어 있는 세로줄'로 옮긴다 — 이웃 칸과 붙은 몸·꼬리·이펙트가 잘리지 않게 (경계 ±valley px 안에서)
        for k, (ry0, y1, cells) in list(rows.items()):
            occ = (RGB[ry0:y1].max(axis=2) > thr).sum(axis=0); cs = [list(c) for c in cells]
            for i in range(len(cs) - 1):
                a, b = cs[i][1], cs[i + 1][0]
                if abs(a - b) > 60: continue   # 멀리 떨어진 칸은 그대로
                lo, hi = min(a, b) - valley, max(a, b) + valley
                seg = occ[lo:hi]; m = seg.min(); xs = np.where(seg == m)[0]; v = lo + int(xs[len(xs) // 2]); cs[i][1] = cs[i + 1][0] = v
            cs[-1][1] += valley // 2   # 맨 왼쪽 칸은 패널 테두리가 들어올 수 있어 넓히지 않는다
            rows[k] = (ry0, y1, [tuple(c) for c in cs])
    for k, (ry0, y1, cells) in rows.items():
        frames[k] = []
        for cell in cells:
            x0, x1 = cell[0], cell[1]; y0 = cell[2] if len(cell) > 2 else ry0   # 칸마다 위쪽을 따로 정할 수 있다(제목 글자 피하기)
            m = RGB[y0:y1, x0:x1].max(axis=2) > thr
            lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
            mx = sz.max(); ok = []
            for i, sl in enumerate(nd.find_objects(lab)):   # 칸 가장자리에 걸린 이웃 그림 조각(작은 것)은 버린다
                edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
                thin = (sl[1].stop - sl[1].start) <= (8 if hline else 4) and (sl[0].stop - sl[0].start) >= (25 if hline else 20)   # 패널 테두리 선
                near = hline and (sl[1].stop <= 14 or sl[1].start >= m.shape[1] - 14) and sz[i] < 0.05 * mx   # v8.51: 칸 가장자리 14px 안의 작은 조각(이웃 칸 이펙트·글자 부스러기)
                if sz[i] >= 25 and not thin and not near and not (edge and sz[i] < 0.2 * mx): ok.append(i + 1)
            keep = np.isin(lab, ok)
            if close: keep = nd.binary_closing(np.pad(keep, close + 2), structure=np.ones((3, 3)), iterations=close)[close + 2:-(close + 2), close + 2:-(close + 2)] | keep   # 닫기: 가는 틈을 메워 구멍 메우기가 잘 되게
            if thin:   # 패널 테두리 조각(가는 가로·세로 선) 지우기
                th = nd.binary_dilation(nd.binary_opening(keep, structure=np.ones((3, 3))), iterations=1)
                keep &= ~((nd.binary_opening(keep, structure=np.ones((1, 12))) | nd.binary_opening(keep, structure=np.ones((12, 1)))) & ~th)
            if hline:   # v8.51: 칸 폭의 80% 넘게 이어지는 얇은 가로줄(패널 구분선·바닥선)은 발에 붙어 있어도 지운다
                cov = keep.sum(axis=1) / keep.shape[1]; H = len(cov)
                for yy in range(H):   # 줄은 칸 폭 거의 전부 + 위아래 4px 밖은 훨씬 비어 있다 (몸통은 이런 모양이 아니다)
                    up = cov[yy - 4] if yy >= 4 else 0; dn = cov[yy + 4] if yy + 4 < H else 0
                    if cov[yy] > 0.93 and keep.shape[1] > 120 and (up < 0.6 or dn < 0.6) and min(up, dn) < 0.6: keep[yy] = False
            if holemax:   # 작은 구멍만 메운다 (이펙트 사이 큰 빈 곳이 까맣게 채워지지 않게)
                hole = nd.binary_fill_holes(keep) & ~keep; hl, hn = nd.label(hole); hs = nd.sum(hole, hl, range(1, hn + 1)); keep = keep | np.isin(hl, [i + 1 for i in range(hn) if hs[i] <= holemax])
            else: keep = nd.binary_fill_holes(keep)
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
hunter, wolf, hunterE = sys.argv[1], sys.argv[2], sys.argv[3]   # '-' 이면 그 스킨은 다시 만들지 않는다 (예: python3 skin_build.py - - - 현무시트.png)
lizG = sys.argv[4] if len(sys.argv) > 4 else None
ghostG = sys.argv[5] if len(sys.argv) > 5 else None
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
    'walk': (156, 296, [(128, 232), (232, 352), (352, 475), (475, 595), (595, 715), (715, 838), (838, 960), (960, 1080)]),
    'attack': (300, 466, [(129, 250), (250, 405), (405, 575), (584, 750), (752, 945), (950, 1120)]),
    'hit': (462, 602, [(145, 283), (318, 450), (476, 622), (640, 800)]),
    'death': (612, 726, [(138, 280), (296, 450), (459, 602), (612, 749), (760, 895), (895, 1045)]),
}, (1118, 280, 1526, 738), thr=20, close=1, valley=40)
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
# 현무 리저드 (리저드 수호의 길 최종 진화 스킨, 레어): 시트 1448x1086, 원본은 오른쪽을 본다 · 키 = 게임 동작 이름
if lizG: build(lizG, 'lizG', {
    'idle':   (402, 498, [(140,338),(338,545),(545,757),(757,962),(962,1188),(1188,1405)]),
    'walk':   (502, 598, [(140,305),(305,467),(467,623),(623,770),(770,930),(930,1085),(1085,1268),(1268,1435)]),
    'attack': (602, 698, [(140,318),(318,520),(520,792),(792,1030),(1030,1232),(1232,1435)]),
    'skill':  (700, 836, [(128,335),(335,580),(580,825),(825,1048),(1048,1240),(1240,1438)]),   # v8.51: 방어 6칸 — 둥근 등껍질 이펙트가 칸 경계에서 잘리던 것을 몸 중심 사이 가운데로 옮김
    'hit':    (848, 942, [(108,252),(252,380),(380,528)]),
    'death':  (848, 948, [(652,800),(800,935),(935,1085),(1085,1235),(1235,1405)]),
}, (120, 50, 850, 402), thr=24, close=1, valley=45, holemax=160, thin=True, hline=True)
if ghostG:   # v8.13 연보라 총령 최종 레어 스킨 (수호령의 총령, 시트는 오른쪽을 봄 · 어두운 남색 배경 thr 30)
    def cells(b): return [(b[i], b[i + 1]) for i in range(len(b) - 1)]
    build(ghostG, 'ghostG', {'idle': (548, 622, cells([172, 315, 475, 635, 795, 950, 1110, 1270])),
      'walk': (637, 712, cells([172, 315, 470, 630, 785, 940, 1100, 1270])),
      'attack': (727, 805, cells([172, 300, 450, 585, 725, 855, 990, 1125, 1270])),
      'skill': (817, 897, cells([172, 335, 490, 620, 745, 895, 1050, 1200, 1440])),
      'hit': (907, 985, cells([172, 320, 480, 620, 765, 900])),
      'death': (995, 1070, cells([172, 320, 480, 650, 850, 1070, 1280]))},
      (20, 10, 560, 330), thr=30, close=1, valley=30, holemax=160, thin=True)
# v8.60 곰 후드 총령 (연보라 총령 최종 유니크 스킨, 시트 1448x1086 · 오른쪽을 봄 · 어두운 남색 배경): 사용: skin_build.py - - - - - <시트>
ghostU = sys.argv[6] if len(sys.argv) > 6 else None
if ghostU:
    def cells2(b): return [(b[i], b[i + 1]) for i in range(len(b) - 1)]
    build(ghostU, 'ghostU', {'idle': (541, 611, cells2([165, 318, 480, 640, 805, 965, 1130, 1290])),
      'walk': (627, 699, cells2([165, 320, 485, 645, 805, 970, 1135, 1300])),
      'attack': (715, 789, cells2([165, 315, 455, 588, 732, 872, 1015, 1158, 1290])),
      'skill': (803, 877, cells2([165, 320, 490, 625, 758, 915, 1070, 1220, 1424])),
      'hit': (891, 963, cells2([165, 325, 478, 620, 765, 905])),
      'death': (979, 1053, cells2([165, 328, 498, 690, 897, 1087, 1285]))},
      (15, 5, 545, 325), thr=30, close=1, valley=30, holemax=160, thin=True)
