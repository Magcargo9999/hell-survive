"""v6.52 지하 6~10층 '버섯' 세트: 바닥 타일 · 소품 · 버섯형 악마(잡몹) · 보스맵.
시트(실행 폴더): map_sheet.png(버섯형 악마 맵 타일셋) · mob_sheet.png(악마 도감, 버섯형만) · bmap_sheet.png(보스맵)
자르기 · 배경 제거(배경색과의 차이로 알파) · 배율(작은 버섯 정수 2배)만 — 재색칠 없음.
출력: mfloor.webp(바닥 36칸 42px 띠) · mprops.webp/json · mmob.webp(108×114 칸, 8종 × 2프레임) · mmap.webp"""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
def clean(a,minsz=6):
    m=a>0; lab,n=ndi.label(m,structure=np.ones((3,3)))
    if n: sz=ndi.sum(m,lab,range(1,n+1)); a[np.isin(lab,np.where(sz<minsz)[0]+1)]=0
    return a
def mode_bg(c):
    q=(c.reshape(-1,3)//4).astype(int); k=q[:,0]*4096+q[:,1]*64+q[:,2]; v,n=np.unique(k,return_counts=True); m=v[np.argmax(n)]
    return c.reshape(-1,3)[k==m].mean(0)
def alpha(c,BG,lo,hi):
    d=np.abs(c-BG).max(-1); core=d>hi; near=ndi.binary_dilation(core,iterations=1)
    return clean(np.where(d<=lo,0.0,np.where(core|near,1.0,(d-lo)/(hi-lo))))
def unblend(c,a,BG):
    A=np.clip(a,0,1)[...,None]
    with np.errstate(divide='ignore',invalid='ignore'): u=np.where(A>0.999,c,(c-BG*(1-A))/np.maximum(A,1e-3))
    return np.dstack([np.clip(u,0,255).astype(np.uint8),(np.clip(a,0,1)*255).astype(np.uint8)])
def cut(S,box,lo=14,hi=34,center=True):
    x0,y0,x1,y1=box; pad=6; c=S[y0-pad:y1+pad,x0-pad:x1+pad]; BG=mode_bg(c); a=alpha(c,BG,lo,hi)
    a[:pad]=0; a[-pad:]=0; a[:,:pad]=0; a[:,-pad:]=0
    if center:   # 칸 가운데와 겹치는 덩어리만 남긴다 (옆 그림 조각 제거)
        lab,n=ndi.label(a>0.3,structure=np.ones((3,3))); h,w=a.shape
        keep=set(np.unique(lab[int(h*0.2):int(h*0.85),int(w*0.2):int(w*0.8)]))-{0}
        a[~np.isin(lab,list(keep))&(lab>0)]=0
        a[(a<=0.3)&~ndi.binary_dilation(np.isin(lab,list(keep)),iterations=2)]=0
    rgba=unblend(c,a,BG); ys,xs=np.where(rgba[...,3]>8)
    return rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
# ---- 바닥 타일 36칸 (9×4, 칸 간격 47.67 × 48, 테두리 선 3px 안쪽만) ----
M=load('map_sheet.png'); T=[]
for r in range(4):
    for c in range(9):
        x=round(16+c*47.667)+3; y=146+r*48+3; T.append(M[y:y+42,x:x+42])
Image.fromarray(np.hstack(T).astype(np.uint8)).save('mfloor.webp',lossless=True,method=6)
# ---- 소품 (장식 · 나무/식물) ----
PROPS=[(18,406,60,462),(66,402,90,462),(96,406,125,463),(132,400,176,462),(180,400,206,463),
 (20,470,59,521),(64,472,95,521),(100,470,143,521),(145,471,193,521),(198,471,219,521),
 (17,529,59,579),(62,529,110,579),(115,529,151,577),(159,529,183,579),(189,533,219,579),
 (17,589,59,641),(60,585,115,641),(175,604,216,641),
 (212,392,273,463),(280,396,351,464),(356,399,399,463),(407,399,436,463),
 (225,464,254,521),(259,469,301,521),(307,469,334,521),(342,473,366,518),(374,471,401,521),(407,469,434,521),
 (227,529,266,579),(271,529,294,579),(299,529,330,579),(334,529,363,579),(365,524,401,579),(406,529,435,591),
 (219,585,258,643),(264,589,299,643),(305,585,360,643),(367,583,393,643),(399,597,434,643),
 (377,693,431,749),(431,688,523,766),(529,688,603,766),(597,688,656,766),(654,694,709,761),(701,688,766,826),(757,688,833,766),
 (371,759,434,826),(441,769,486,826),(491,769,548,826),(554,774,589,826),(590,769,636,826),(639,764,696,826),(762,769,796,826),(796,769,831,826)]
info=[cut(M,b,14,30) for b in PROPS]
W=1024; x=y=sh=0; pos=[]
for c in info:
    h,w=c.shape[:2]
    if x+w>W: x=0; y+=sh+2; sh=0
    pos.append((x,y)); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); rects=[]
for c,(x,y) in zip(info,pos): h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; rects.append([x,y,w,h])
Image.fromarray(at).save('mprops.webp',lossless=True,method=6); json.dump(rects,open('mprops.json','w'),separators=(',',':'))
print('props',len(rects),at.shape,[r[3] for r in rects])
# ---- 버섯형 악마 8종: 작은 4종(정수 2배, 2프레임) + 큰 4종(원본 크기) → 108×114 칸 ----
B=load('mob_sheet.png'); CW,CH=108,114
SMALL=[[(23,182,59,230),(80,182,118,230)],[(147,182,183,230),(201,182,236,230)],[(267,182,303,230),(321,182,358,230)],[(387,182,423,230),(439,182,475,230)]]
BIG=[(28,73,119,169),(150,70,237,169),(263,58,355,169),(383,64,472,169)]
cells=[]; nh=[]
for fr in SMALL:
    cs=[cut(B,b,14,34) for b in fr]; cs=[np.array(Image.fromarray(c).resize((c.shape[1]*2,c.shape[0]*2),Image.NEAREST)) for c in cs]; cells.append(cs)
for b in BIG: c=cut(B,b,14,34); cells.append([c,c])
at=np.zeros((CH*2,CW*len(cells),4),np.uint8)
for i,cs in enumerate(cells):
    for k,c in enumerate(cs):
        h,w=c.shape[:2]; assert h<=CH-2 and w<=CW, (i,h,w)
        ox=i*CW+(CW-w)//2; oy=k*CH+CH-2-h; at[oy:oy+h,ox:ox+w]=c
    nh.append(max(c.shape[0] for c in cs))
Image.fromarray(at).save('mmob.webp',lossless=True,method=6); print('mob nh',nh,[[c.shape[:2] for c in cs] for cs in cells])
# ---- 보스맵 그대로 ----
Image.open('bmap_sheet.png').convert('RGB').save('mmap.webp',lossless=True,method=6)
