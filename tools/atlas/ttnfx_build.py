"""v10.26 타르타로스의 티탄 이펙트 도트 → 기존 src/assets/tar/ttn.webp 아틀라스 아래에 덧붙임 (재색칠 없음: 자르기 · 마젠타 배경 제거 · 배율 없음)
사용: python3 tools/atlas/ttnfx_build.py <시트1(전체 컨셉: 사슬 투사체·봉인 UI·크로스헤어)> <시트2(액션 시트: 이펙트·환경 오브젝트)>
 - 쓰는 것(ttn.json 그룹): rift 중력의 틈 5 · quake 충격파 5 · lock 자물쇠 · lockA/lockB 봉인 폭발 · rockN 바위(온전·금 감) 2 · rockB 부서짐 3 · chainhead 사슬 투사체 머리 · crack 바닥 균열 · uiseal 봉인 UI 아이콘(상자째)
 - 안 쓰는 것은 src/assets/tar/ttn_spare.webp + ttn_spare.json 에 보관 (게임이 불러오지 않음): env 환경 오브젝트 · 사슬 투사체 성장 3칸 · 쇠사슬 구속 · 파편 이펙트 · 크로스헤어 · 바닥 균열 타일 · 봉인 UI 나머지 3칸 · 중력 구멍(시트1) · 충격파(시트1) 등
 같은 그룹 이름은 덮어쓴다 (여러 번 돌려도 같은 결과)."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
S1, S2 = sys.argv[1:3]
OUT = 'src/assets/tar/'
A1 = np.array(Image.open(S1).convert('RGB')).astype(int); A2 = np.array(Image.open(S2).convert('RGB')).astype(int)
BG = np.array([252, 3, 252])

def fgmask(a, tol=70):
    return np.abs(a - BG).sum(2) > tol

def cut_runs(A, x0, y0, x1, y1, n=0, splits=(), tol=70, name=''):
    """띠 안을 세로줄 빈 곳(또는 직접 준 splits)으로 나눠 왼쪽부터 · 마젠타만 투명 · 작은 부스러기 줄은 이웃에 합침"""
    a = A[y0:y1, x0:x1]; fg = fgmask(a, tol); col = fg.sum(0) > 0
    for sx in splits: col[sx - x0] = False
    runs = []; s = None
    for i, c in enumerate(col):
        if c and s is None: s = i
        if not c and s is not None: runs.append([s, i - 1]); s = None
    if s is not None: runs.append([s, len(col) - 1])
    merged = []
    for r in runs:   # 6px보다 좁은 부스러기는 앞 덩어리에 합침
        if merged and (r[1] - r[0] < 6): merged[-1][1] = r[1]
        else: merged.append(r)
    if n and len(merged) != n: raise SystemExit(f'{name}: {len(merged)}개 (기대 {n}) {[(x0 + r[0], x0 + r[1]) for r in merged]}')
    out = []
    for r0, r1 in merged:
        m = fg[:, r0:r1 + 1]; ys = np.where(m.any(1))[0]; sub = a[ys.min():ys.max() + 1, r0:r1 + 1]; mm = m[ys.min():ys.max() + 1]
        out.append(Image.fromarray(np.dstack([sub, (mm * 255).astype(np.uint8)]).astype(np.uint8), 'RGBA'))
    return out

def box(A, x0, y0, x1, y1):   # 불투명 상자째
    return Image.fromarray(np.dstack([A[y0:y1, x0:x1], np.full((y1 - y0, x1 - x0), 255)]).astype(np.uint8), 'RGBA')

def panel_cut(A, x0, y0, x1, y1, thr=26, merge=3):
    """어두운 판 위 이펙트: 판 색(가장자리 중앙값)과의 차이만큼 불투명 · 안쪽 구멍은 채움"""
    a = A[y0:y1, x0:x1]; bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    d = np.abs(a - bg).sum(2); fg = d > thr
    fg = ndi.binary_closing(fg, iterations=2); fg = ndi.binary_fill_holes(fg)
    lab, k = ndi.label(fg); sz = ndi.sum(fg, lab, range(1, k + 1)); fg = lab == (int(np.argmax(sz)) + 1)
    al = np.clip((d - thr) / 60.0, 0, 1) * 255; al[ndi.binary_erosion(fg, iterations=2)] = 255; al[~ndi.binary_dilation(fg, iterations=1)] = 0
    ys, xs = np.where(al > 0)
    return Image.fromarray(np.dstack([a, al]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')

G = {}; SP = {}
# ---- 시트2 (마젠타 배경) ----
G['rift'] = cut_runs(A2, 20, 795, 210, 870, 3, splits=(68, 130), name='rift1') + cut_runs(A2, 212, 780, 395, 870, 2, splits=(290,), name='rift2')   # 칸 제목 글씨(위쪽)를 피해 두 번에 나눠 자름
G['quake'] = cut_runs(A2, 410, 797, 620, 870, 3, splits=(462, 538), name='quake1') + cut_runs(A2, 620, 770, 815, 870, 2, name='quake2')
lk = cut_runs(A2, 830, 795, 1090, 870, 3, name='lock')
G['lock'] = [lk[0]]; G['lockA'] = [lk[1]]; G['lockB'] = [lk[2]]
rk = cut_runs(A2, 1105, 795, 1536, 870, 5, name='rock')
G['rockN'] = rk[:2]; G['rockB'] = rk[2:]
env = cut_runs(A2, 0, 910, 1536, 1024, 0, name='env'); env = [e for e in env if e.size[0] > 8]
SP['env'] = env   # 환경 오브젝트(비석·사슬 기둥·새장·깃발·가시·의식진·균열·가시 분출) — 줄 단위로 잘려 일부는 붙어 있음
cr = cut_runs(A2, 1308, 920, 1424, 1000, 1, name='crack'); G['crack'] = cr
# 시트2의 몸 행(새 스타일)은 몸 그림이 다른 판이라 쓰지 않고 보관하지도 않는다 (원본 시트를 다시 첨부하면 됨)
# ---- 시트1 (어두운 판 위) ----
ch = [panel_cut(A1, 22 + 0, 815, 80, 872), panel_cut(A1, 80, 815, 152, 872), panel_cut(A1, 152, 810, 238, 872), panel_cut(A1, 238, 800, 368, 880)]
G['chainhead'] = [ch[3]]; SP['chainprj'] = ch[:3]
G['uiseal'] = [box(A1, 972, 813, 1036, 877)]   # 금 자물쇠 아이콘 (상자째)
SP['uiicons'] = [box(A1, 704, 813, 768, 877), box(A1, 786, 813, 852, 877), box(A1, 869, 813, 935, 877)]
SP['crosshair'] = [panel_cut(A1, 1085, 925, 1190, 1015)]
SP['fx1gravity'] = [panel_cut(A1, x0, 658, x1, 756) for x0, x1 in ((20, 98), (100, 180), (182, 262), (264, 346), (350, 440), (445, 524))]

def pack(groups, png, js, W):
    x = y = sh = 0; frames = {}; items = []
    for name, ims in groups.items():
        for im in ims:
            w, h = im.size
            if x + w > W: x = 0; y += sh + 2; sh = 0
            items.append((name, im, x, y)); x += w + 2; sh = max(sh, h)
    A = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0))
    for name, im, xx, yy in items:
        A.alpha_composite(im, (xx, yy)); frames.setdefault(name, []).append([xx, yy, im.size[0], im.size[1]])
    return A, frames

# 사용 그룹을 기존 아틀라스 아래에 덧붙임 (같은 이름은 먼저 지움)
base = Image.open(OUT + 'ttn.webp').convert('RGBA'); fr = json.load(open(OUT + 'ttn.json'))
FXN = ['rift', 'quake', 'lock', 'lockA', 'lockB', 'rockN', 'rockB', 'chainhead', 'crack', 'uiseal']
oldy = max(r[1] + r[3] for k, v in fr.items() if k not in FXN for r in v)
base = base.crop((0, 0, base.size[0], oldy + 2)); [fr.pop(k, None) for k in FXN]
At, F = pack(G, None, None, base.size[0])
C = Image.new('RGBA', (base.size[0], base.size[1] + At.size[1]), (0, 0, 0, 0)); C.alpha_composite(base, (0, 0)); C.alpha_composite(At, (0, base.size[1]))
for k, v in F.items(): fr[k] = [[r[0], r[1] + base.size[1], r[2], r[3], r[2] / 2, r[3]] for r in v]   # 기준점 = 아래 가운데
C.save(OUT + 'ttn.webp', lossless=True, method=6); json.dump(fr, open(OUT + 'ttn.json', 'w'), separators=(',', ':'))
Sa, Fs = pack(SP, None, None, 1536); Sa.save(OUT + 'ttn_spare.webp', lossless=True, method=6); json.dump(Fs, open(OUT + 'ttn_spare.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', C.size, (60, 140, 90, 255)); bg.alpha_composite(C); bg.save('build/h9/ttn_prev2.png')
bg = Image.new('RGBA', Sa.size, (60, 140, 90, 255)); bg.alpha_composite(Sa); bg.save('build/h9/ttn_spare_prev.png')
print('atlas', C.size, {k: len(v) for k, v in F.items()}, 'spare', Sa.size, {k: len(v) for k, v in Fs.items()})
print(json.dumps({k: fr[k] for k in FXN}, separators=(',', ':')))
