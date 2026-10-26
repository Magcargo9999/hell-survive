"""팔한지옥의 백곰 마왕 '패턴 이펙트 / 기믹 에셋 시트'(어두운 배경) → src/assets/bear/bearfx.webp + bearfx.json (v9.62)
빙벽 모듈 6(직선·안쪽 코너·바깥 코너·파손1·2·잔해) · 빙벽 솟는 6칸 · 눈보라 줄·결 · 동상 아이콘 3 · 균열 경고 3 · 얼음 가시 3 · 벽 충돌 · 돌진 잔상 · 발 구르기 · 얼음 숨결 · 눈 폭발 · 서리 안개 · 얼음 파편 · 고드름 · 냉기 오라
가장자리에서 이어진 어두운 배경만 지우고(재색칠 없음) 그림마다 따로 잘라 한 장에 모은다. 사용: python3 bearfx_build.py <시트.png>"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
S = Image.open(sys.argv[1]).convert('RGB'); A = np.array(S)
THR = 24
def cutreg(x0, y0, x1, y1, gap=6, minh=24, minw=24, maxn=None, thr=THR, speck=3):
    """영역 안에서 배경을 지우고, 세로로 완전히 빈 줄이 gap칸 이상 이어지는 곳에서 그림을 나눠 x 순서대로 돌려준다 (작은 부스러기 speck 이하는 지움)"""
    a = A[y0:y1, x0:x1]; dark = a.max(2) <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge)); fg = ~bg
    fl, fn = ndi.label(fg, structure=np.ones((3, 3))); sz = ndi.sum(fg, fl, range(1, fn + 1)); fg &= np.isin(fl, [i + 1 for i, v in enumerate(sz) if v > speck])
    for i, sl in enumerate(ndi.find_objects(fl), 1):   # 칸 테두리선(가늘고 긴 줄) 지움
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (hh <= 5 and ww >= 40) or (ww <= 5 and hh >= 40): fg[sl] &= ~(fl[sl] == i)
    col = fg.any(axis=0); out = []; x = 0; Wd = fg.shape[1]
    while x < Wd:
        if not col[x]: x += 1; continue
        s0 = x; e = x; empty = 0
        while x < Wd:
            if col[x]: e = x; empty = 0
            else:
                empty += 1
                if empty >= gap: break
            x += 1
        m = fg[:, s0:e + 1]; ys = np.where(m.any(axis=1))[0]; y0_, y1_ = ys[0], ys[-1] + 1
        if e - s0 + 1 < minw or y1_ - y0_ < minh: continue
        r = np.dstack([a[y0_:y1_, s0:e + 1], np.where(m[y0_:y1_], 255, 0).astype(np.uint8)]); out.append(Image.fromarray(r, 'RGBA'))
    return out[:maxn] if maxn else out
def one(x0, y0, x1, y1, lines=False):
    r = cutreg(x0, y0, x1, y1, gap=9999, minh=6, minw=6)
    if not r: return None
    im = r[0]
    if lines:   # 맨 위·아래에 붙은 칸 테두리선(가로로 길게 이어진 줄)만 지운다
        a = np.array(im); al = a[..., 3] > 0; h, w = al.shape
        for y in list(range(0, min(9, h))) + list(range(max(0, h - 9), h)):
            if w >= 30 and al[y].sum() >= 0.7 * w: a[y, :, 3] = 0
        im = Image.fromarray(a, 'RGBA'); im = im.crop(im.getchannel('A').getbbox())
    return im
GROUPS = [   # 이름, 영역(자동으로 나눔) 또는 직접 정한 사각형들
 ('wall',    ('auto', (455, 164, 965, 258, {}))),                     # 직선 · 코너(안) · 코너(밖) · 파손1 · 파손2 · 잔해
 ('wrise',   ('rects', [(458, 322, 514, 392), (522, 322, 584, 392), (590, 322, 654, 392), (664, 322, 734, 392), (735, 292, 810, 392), (818, 292, 964, 392)])),   # 빙벽이 솟는 6칸
 ('bzstrip', ('auto', (14, 468, 512, 540, {'gap': 40}))),             # 눈보라 이펙트 시트 (왼쪽→오른쪽)
 ('bzpart',  ('rects', [(524, 462, 598, 532), (598, 462, 660, 532), (664, 462, 726, 532), (734, 462, 802, 532)])),   # 강풍 줄 · 눈 가루 · 회오리 · 서리 돌풍
 ('frost',   ('rects', [(242, 608, 298, 670), (312, 608, 368, 670), (382, 608, 438, 670)])),    # 동상 아이콘 1~3단계
 ('crack',   ('rects', [(820, 462, 915, 562), (930, 462, 1025, 562), (1040, 462, 1145, 562)])),   # 균열 경고 1~3단계
 ('spike',   ('rects', [(1162, 458, 1232, 560), (1244, 458, 1332, 560), (1342, 456, 1440, 560)])),   # 지면 균열 → 가시 솟음 → 완성
 ('wallhit', ('rects', [(1174, 898, 1229, 964), (1230, 898, 1310, 964), (1311, 898, 1355, 964), (1356, 898, 1436, 964)])),   # 벽 충돌 이펙트
 ('stomp',   ('rects', [(15, 1024, 108, 1078), (108, 1024, 210, 1078)])),      # 발 구르기 충격파 · 얼음 가시 파동
 ('breath',  ('rects', [(222, 1024, 414, 1078), (416, 1024, 448, 1078)])),     # 얼음 숨결
 ('snowburst', ('rects', [(463, 1022, 525, 1078), (525, 1022, 600, 1078)])),   # 눈 폭발
 ('fog',     ('rects', [(612, 1029, 790, 1078)])),                           # 서리 안개
 ('shards',  ('rects', [(796, 1033, 824, 1078), (832, 1033, 874, 1078), (874, 1033, 908, 1078), (915, 1033, 960, 1078)])),   # 얼음 파편
 ('icicle',  ('rects', [(978, 1028, 998, 1078), (1000, 1028, 1046, 1078), (1046, 1028, 1094, 1078)])),   # 고드름 잔해
 ('aura',    ('rects', [(1264, 1028, 1376, 1078), (1376, 1028, 1436, 1078)])),   # 냉기 오라
]
sheets = []; meta = {}
for name, (kind, v) in GROUPS:
    ims = cutreg(*v[:4], **v[4]) if kind == 'auto' else [one(*r, lines=name in ('spike', 'wallhit')) for r in v]
    meta[name] = len(ims); sheets.append((name, ims)); print(name, [im.size for im in ims])
# 한 장에 모으기: 줄마다 한 그룹, 칸 사이 4px
rows = []; Wmax = 0
for name, ims in sheets:
    h = max(i.height for i in ims); w = sum(i.width for i in ims) + 4 * (len(ims) - 1); rows.append((name, ims, h, w)); Wmax = max(Wmax, w)
H = sum(r[2] + 4 for r in rows); C = Image.new('RGBA', (Wmax, H), (0, 0, 0, 0)); fr = {}; y = 0
for name, ims, h, w in rows:
    x = 0; L = []
    for im in ims:
        C.alpha_composite(im, (x, y + h - im.height)); L.append([x, y + h - im.height, im.width, im.height]); x += im.width + 4
    fr[name] = L; y += h + 4
def axis(im):   # 균열 그림의 줄기 방향(가장 밝은 줄이 뻗은 각도, 라디안) — 게임이 균열 선분 방향에 맞춰 돌린다
    a = np.array(im); m = (a[..., 3] > 0) & (a[..., :3].max(axis=2) > 170); ys, xs = np.nonzero(m)
    if len(xs) < 10: return 0.0
    c = np.cov(np.vstack([xs - xs.mean(), ys - ys.mean()])); w, v = np.linalg.eigh(c); return float(np.arctan2(v[1, 1], v[0, 1]))
fr['crackAng'] = [round(axis(im), 3) for im in dict(sheets)['crack']]
out = os.path.join(ROOT, 'src', 'assets', 'bear', 'bearfx.webp'); C.save(out, quality=95, method=6)
json.dump(fr, open(os.path.join(ROOT, 'src', 'assets', 'bear', 'bearfx.json'), 'w'))
print(out, os.path.getsize(out) // 1024, 'KB', C.size)
p = Image.new('RGBA', C.size, (70, 40, 90, 255)); p.alpha_composite(C); p.save(os.path.join(ROOT, 'build', 'bearfx_prev.png'))
