"""3줄 합성 심장 도트 → src/assets/heart/hfuse3.webp (자르기 + 정사각 캔버스 배치 + 배율 조정만)
사용: python3 hfuse3_build.py <합성된 심장.png>"""
import sys, os
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
im = Image.open(sys.argv[1]).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox())
S = 320; k = min(S / im.width, S / im.height) * 0.96
im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
c = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
c.save(os.path.join(ROOT, 'src/assets/heart/hfuse3.webp'), lossless=True)
