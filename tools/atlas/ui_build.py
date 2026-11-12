"""메인 화면 UI 도트 (v10.43): 받은 UI 시트(투명 배경)를 조각별로 자르기만 한다 — 색·픽셀 수정 없음.
사용: python3 tools/atlas/ui_build.py <UI 시트> → src/assets/ui/*.webp (무손실)"""
import sys, os
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA')
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'assets', 'ui'); os.makedirs(OUT, exist_ok=True)
BOX = {   # 이름: (x, y, w, h)
    'card': (127, 12, 368, 514), 'cardsel': (549, 12, 370, 514), 'cardlock': (976, 12, 370, 511),
    'arl': (1390, 221, 101, 81), 'arr': (1390, 320, 101, 80),
    'bar': (943, 559, 539, 98), 'barred': (943, 664, 539, 98), 'bardeep': (943, 769, 539, 96),
    'btnred': (114, 878, 297, 120), 'btn': (437, 881, 291, 115),
}
for k, (x, y, w, h) in BOX.items():
    im.crop((x, y, x + w, y + h)).save(os.path.join(OUT, k + '.webp'), lossless=True, quality=100)
    print(k, w, h)
