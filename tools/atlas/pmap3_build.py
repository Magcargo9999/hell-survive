#!/usr/bin/env python3
"""v10.60 10지옥 판데모니움 보스맵 v3 — 받은 '지옥 성당' 그림(build/pan/cathedral.png 1067×1474, 다시 그린 원본)을
픽셀 그대로 보스맵 그림으로 쓴다(×3 nearest → 월드 3201×4422). 그림은 손대지 않고, 걷는 곳 다각형·시작·보스·출구만 여기서 정한다.
출력: src/assets/pan/pmap.webp(무손실) · build/pan/pmap3.json(IMAP_PAN에 붙임) · build/pan/pmap3_prev.png(걷는 곳 미리보기)"""
import json, os
import numpy as np, cv2
from PIL import Image, ImageDraw

R = os.path.dirname(os.path.abspath(__file__)) + '/../../'
S = Image.open(R + 'build/pan/cathedral.png').convert('RGB'); IW, IH = S.size; k = 3
CX = IW / 2.0   # 좌우 대칭

def octo(cx, cy, hw, hh, c): return [(cx - hw + c, cy - hh), (cx + hw - c, cy - hh), (cx + hw, cy - hh + c), (cx + hw, cy + hh - c), (cx + hw - c, cy + hh), (cx - hw + c, cy + hh), (cx - hw, cy + hh - c), (cx - hw, cy - hh + c)]
def band(x0, y0, x1, y1, w):   # (x0,y0)→(x1,y1) 방향 폭 w 띠
    dx, dy = x1 - x0, y1 - y0; L = (dx * dx + dy * dy) ** .5; nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
def mirror(p): return [(2 * CX - x, y) for x, y in p]

# 광장 팔각형 (룬 고리 중심 (533,878))
X0, X1, Y0, Y1, c = 225, 842, 600, 1160, 180
cx, cy = 533, 880
REG = []
REG.append(octo(cx, cy, (X1 - X0) / 2, (Y1 - Y0) / 2, c))
# 위 계단 → 옥좌 단상
REG.append([(497, 330), (572, 330), (572, 610), (497, 610)])
REG.append([(295, 335), (772, 335), (772, 436), (295, 436)])
# 아래 길·계단 → 아래 단상(시작) → 출구 계단
REG.append([(497, 1150), (572, 1150), (572, 1310), (497, 1310)])
REG.append([(300, 1298), (768, 1298), (768, 1396), (700, 1396), (700, IH), (368, IH), (368, 1396), (300, 1396)])
# 왼쪽: 모서리 팔각 단상 3개 + 다리 + 옆 판석
L = [octo(167, 604, 58, 46, 20), octo(165, 905, 55, 46, 20), octo(165, 1180, 55, 48, 20),
     band(340, 695, 205, 575, 44), band(340, 1062, 205, 1192, 44), [(205, 885), (240, 885), (240, 925), (205, 925)],
     [(28, 778), (205, 778), (205, 872), (28, 872)]]
REG += L + [mirror(p) for p in L]

WM = Image.new('L', (IW, IH), 0); d = ImageDraw.Draw(WM)
for p in REG: d.polygon(p, fill=255)
M = np.array(WM) > 0
cs, _ = cv2.findContours(M.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cnt = max(cs, key=cv2.contourArea)
assert len(cs) == 1, len(cs)   # 모두 이어져 있어야 한다
ap = cv2.approxPolyDP(cnt, 2.0, True)[:, 0, :].tolist()

start = (533, 1372); bx, by = cx, Y0 + 100
J = {'iw': IW, 'ih': IH, 'X0': X0 * k, 'X1': X1 * k, 'Y0': Y0 * k, 'Y1': Y1 * k, 'c': c * k, 'cx': cx * k, 'cy': cy * k, 'bx': bx * k, 'by': by * k,
     'start': [start[0] * k, start[1] * k], 'exitY': 1452 * k, 'itemY': (Y1 - 40) * k, 'skp': [[(X0 + 80) * k, cy * k], [(X1 - 80) * k, cy * k], [cx * k, (Y0 + 120) * k]],
     'poly': [[int(x * k), int(y * k)] for x, y in ap]}
OUT = R + 'src/assets/pan/'; S.save(OUT + 'pmap.webp', lossless=True, quality=100, method=6)
json.dump(J, open(R + 'build/pan/pmap3.json', 'w'), separators=(',', ':'))
pv = S.convert('RGBA'); ov = Image.new('RGBA', pv.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
dd.polygon([(x, y) for x, y in ap], fill=(40, 255, 90, 60), outline=(40, 255, 90, 255))
for (x, y), col in [(start, (60, 140, 255, 255)), ((bx, by), (255, 60, 60, 255)), ((cx, cy), (255, 230, 0, 255))]: dd.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col)
for x, y in J['skp']: dd.ellipse((x / k - 5, y / k - 5, x / k + 5, y / k + 5), fill=(255, 120, 255, 255))
Image.alpha_composite(pv, ov).convert('RGB').save(R + 'build/pan/pmap3_prev.png')
print(S.size, os.path.getsize(OUT + 'pmap.webp'), 'poly', len(ap))
