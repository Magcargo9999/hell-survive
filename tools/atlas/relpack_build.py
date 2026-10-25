"""성유물 3종(방랑자의 열쇠 부적·피닉스의 심장·포식자의 송곳니) 도트 → src/assets/final/relkey|relphoenix|relfang.webp
자르기 + 가장자리에서 이어진 어두운 배경 제거 + 정사각 배치만 (재색칠 없음)
사용: python3 relpack_build.py <성유물 3종 시트.png>"""
import sys, os
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sh = Image.open(sys.argv[1]).convert('RGBA'); K = sh.width / 2000.0
BOX = {'relkey': (80, 70, 610, 520), 'relphoenix': (740, 40, 1260, 520), 'relfang': (1410, 60, 1940, 520)}   # 표시 크기(2000폭) 기준 아이콘 구역
THR = {'relkey': 40, 'relphoenix': 44, 'relfang': 44}
S = 320
for k, b in BOX.items():
    im = sh.crop(tuple(round(v * K) for v in b)); a = np.array(im); lum = a[..., :3].max(axis=2)
    lab, n = ndimage.label(lum < THR[k])
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    a[..., 3] = np.where(np.isin(lab, list(edge)), 0, 255)
    im = Image.fromarray(a); im = im.crop(im.getchannel('A').getbbox())
    r = min(S / im.width, S / im.height) * 0.96
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    c = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
    c.save(os.path.join(ROOT, 'src/assets/final/%s.webp' % k), lossless=True)
    bg = Image.new('RGBA', (S, S), (90, 40, 120, 255)); bg.alpha_composite(c); bg.save(os.path.join(ROOT, 'build/%s_prev.png' % k))
