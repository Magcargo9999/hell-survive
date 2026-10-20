import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
im=np.array(Image.open('s.png').convert('RGB')).astype(float)
BG=np.array([16,14,19])
def alpha_of(c):
    d=np.abs(c-BG).max(-1); core=d>26; near=ndi.binary_dilation(core,iterations=2)
    a=np.where(d<=8,0.0,np.where(core|near,1.0,(d-8)/18.0))
    m=a>0; lab,n=ndi.label(m,structure=np.ones((3,3)))
    if n: sz=ndi.sum(m,lab,range(1,n+1)); a[np.isin(lab,np.where(sz<6)[0]+1)]=0
    return a
def unblend(c,a):
    A=np.clip(a,0,1)[...,None]
    with np.errstate(divide='ignore',invalid='ignore'): u=np.where(A>0.999,c,(c-BG*(1-A))/np.maximum(A,1e-3))
    return np.dstack([np.clip(u,0,255).astype(np.uint8),(np.clip(a,0,1)*255).astype(np.uint8)])
B={'idle':(368,494),'walk':(514,644),'atk':(663,792),'hit':(809,922),'death':(939,1062)}
C={'idle':[205,390,575,760,960,1155,1340],'walk':[205,400,600,795,990,1188,1380],'atk':[205,336,470,618,758,1260,1400],
   'hit':[215,420,615,800],'death':[205,378,558,732,890,1040]}
info={}
for k,(y0,y1) in B.items():
    band=im[y0:y1]; A=alpha_of(band); cuts=C[k]; lst=[]
    for j in range(len(cuts)-1):
        if k=='atk' and j==4: continue   # 5~7번(구슬이 떨어져 나가는 칸)은 쓰지 않고 마지막 칸만
        x0,x1=cuts[j],cuts[j+1]; a=A[:,x0:x1]; c=band[:,x0:x1]
        rgba=unblend(c,a); op=a>0.5; br=op&(c.max(-1)>120); ys,xs=np.where(op)
        bot=int(np.percentile(ys,99.5)); ax=float(np.median(np.where(br)[1])) if br.sum()>30 else float(np.median(xs))
        lst.append((rgba,ax,bot))
    base=int(np.median([b for _,_,b in lst]))
    for rgba,ax,bot in lst:
        ys,xs=np.where(rgba[...,3]>8); x0,x1,y0_,y1_=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        info.setdefault(k,[]).append((rgba[y0_:y1_,x0:x1],ax-x0,base-y0_))
# 구슬 (작은 것 · 꼬리 달린 것)
for nm,(x0,y0,x1,y1) in {'orb':(1125,188,1190,252),'orbT':(1150,278,1225,332)}.items():
    c=im[y0:y1,x0:x1]; a=alpha_of(c); rgba=unblend(c,a); ys,xs=np.where(rgba[...,3]>8)
    cr=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]; info[nm]=[(cr,cr.shape[1]/2,cr.shape[0]/2)]
W=1500; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
Image.fromarray(at).save('gh.png'); Image.fromarray(at).save('gh.webp',lossless=True,method=6); json.dump(meta,open('gh.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
