"""v10.41 타르타로스 푸른 보스맵 — 받은 푸른 '타르타로스 맵 타일셋' 안내 시트(1447×1087)의 보스 아레나 예시 그림만 잘라 608×777로 맞춘다 (재색칠 없음).
사용: python3 tools/atlas/tar2_build.py <타일셋 안내 시트(푸른)> → src/assets/tar/tmap2.webp"""
import sys
from PIL import Image
Image.open(sys.argv[1]).convert('RGB').crop((824, 245, 1440, 1029)).save('src/assets/tar/tmap2.webp', lossless=True, method=6)
