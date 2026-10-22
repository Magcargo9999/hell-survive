"""보스 심장 도트(5종 × 4등급) → 아틀라스. 자르기·배율 조정만. 시트는 2×2: 레어 회색 · 에픽 보라 · 유니크 노랑 · 레전더리 초록
행 순서: angel(타락천사) shk(버섯괴물) skel(스켈레톤) eye(마안군주) monkey(원숭이)"""
import sys, os
from PIL import Image
S = 256
files = sys.argv[1:6]; out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'assets', 'heart', 'heart.webp')
A = Image.new('RGBA', (S * 4, S * 5), (0, 0, 0, 0))
for r, f in enumerate(files):
    im = Image.open(f).convert('RGBA'); w, h = im.size; hw, hh = w // 2, h // 2
    for c in range(4):
        q = im.crop(((c % 2) * hw, (c // 2) * hh, (c % 2 + 1) * hw, (c // 2 + 1) * hh))
        a = q.getchannel('A').point(lambda v: 255 if v > 24 else 0); bb = a.getbbox(); q = q.crop(bb)
        k = (S - 6) / max(q.size); q = q.resize((max(1, round(q.width * k)), max(1, round(q.height * k))), Image.LANCZOS)
        A.alpha_composite(q, (c * S + (S - q.width) // 2, r * S + (S - q.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB')
