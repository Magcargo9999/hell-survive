"""v9.86 7지옥 보스맵: 받은 시트 왼쪽 큰 그림만 잘라냄 (원본 1536x1024 에서 (10,77)-(846,861), 색·도트 수정 없음) → src/assets/dmap/dmap.webp  사용: python3 tools/atlas/dmap_build.py <시트.png>"""
import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert("RGB")
im.crop((10,77,846,861)).save("src/assets/dmap/dmap.webp",quality=95,method=6)
