import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
S={'s1':load('s1.png'),'s2':load('s2.png')}
def alpha_of(c,BG,lo=10,hi=34):
    d=np.abs(c-BG).max(-1); core=d>hi; near=ndi.binary_dilation(core,iterations=2)
    a=np.where(d<=lo,0.0,np.where(core|near,1.0,(d-lo)/(hi-lo)))
    m=a>0; lab,n=ndi.label(m,structure=np.ones((3,3)))
    if n: sz=ndi.sum(m,lab,range(1,n+1)); a[np.isin(lab,np.where(sz<8)[0]+1)]=0
    return a
def feather(a,r=10):
    h,w=a.shape; yy=np.minimum(np.arange(h),np.arange(h)[::-1])[:,None]; xx=np.minimum(np.arange(w),np.arange(w)[::-1])[None,:]
    f=np.clip(np.minimum(yy,xx)/r,0,1); return a*np.where(a>=0.98,np.maximum(f,0.0)*0+1,f) if False else np.where(a>0.9,a,a*f)
def unblend(c,a,BG):
    A=np.clip(a,0,1)[...,None]
    with np.errstate(divide='ignore',invalid='ignore'): u=np.where(A>0.999,c,(c-BG*(1-A))/np.maximum(A,1e-3))
    return np.dstack([np.clip(u,0,255).astype(np.uint8),(np.clip(a,0,1)*255).astype(np.uint8)])
def mode_bg(c):
    q=(c.reshape(-1,3)//4).astype(int); k=q[:,0]*4096+q[:,1]*64+q[:,2]; v,n=np.unique(k,return_counts=True); m=v[np.argmax(n)]
    sel=k==m; return c.reshape(-1,3)[sel].mean(0)
def bgof(im,y0,y1,x0,x1): return mode_bg(im[y0+4:y1-4,x0:x1])
def refine(im,y0,y1,cuts,BG,win=22):
    d=np.abs(im[y0:y1]-BG).max(-1)>34; col=d.sum(0); out=[]
    for c in cuts:
        lo,hi=max(0,c-win),min(im.shape[1]-1,c+win); out.append(lo+int(np.argmin(col[lo:hi])))
    return out
info={}
def cut(sheet,name,y0,y1,cuts,keep=None,refineit=True):
    im=S[sheet]; BG=bgof(im,y0,y1,cuts[0],cuts[-1])
    if refineit: cuts=[cuts[0]]+refine(im,y0,y1,cuts[1:-1],BG)+[cuts[-1]]
    band=im[y0+3:y1-3]; lst=[]
    for j in range(len(cuts)-1):
        if keep is not None and j not in keep: continue
        x0,x1=cuts[j],cuts[j+1]; c=band[:,x0:x1]; bg=mode_bg(c); a=alpha_of(c,bg,13,38)
        rgba=unblend(c,a,bg); op=a>0.5; ys,xs=np.where(op)
        br=op&(c.max(-1)>150)
        bot=int(np.percentile(ys,99.3)); ax=float(np.median(np.where(br)[1])) if br.sum()>30 else float(np.median(xs))
        lst.append((rgba,ax,bot))
    base=int(np.median([b for _,_,b in lst]))
    for rgba,ax,bot in lst:
        ys,xs=np.where(rgba[...,3]>8); x0,x1,yy0,yy1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        info.setdefault(name,[]).append((rgba[yy0:yy1,x0:x1],ax-x0,base-yy0))
def piece(sheet,name,x0,y0,x1,y1):
    im=S[sheet]; c=im[y0:y1,x0:x1]; BG=mode_bg(c)
    a=feather(alpha_of(c,BG,13,38),14); rgba=unblend(c,a,BG); ys,xs=np.where(rgba[...,3]>8)
    cr=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]; info.setdefault(name,[]).append((cr,cr.shape[1]/2,cr.shape[0]/2))
# ---- 1진화: 연보라 총령 ----
cut('s1','g1idle',348,467,[200,390,582,766,962,1171,1380])
cut('s1','g1walk',477,591,[200,393,598,805,1017,1222,1410])
cut('s1','g1atk',601,715,[188,323,478,629,777,921,1265,1418],keep=[0,1,2,3,4,6],refineit=False)
cut('s1','g1hit',725,830,[205,396,602,790])
cut('s1','g1death',839,940,[205,386,568,736,896,1050])
cut('s1','g1skill',951,1067,[195,397,609,782,1018,1232,1410],keep=[0,1,2,5])
# ---- 최종: 연보라 총령 (소녀) ----
cut('s2','g2idle',538,612,[160,321,481,642,803,966,1130,1300])
cut('s2','g2walk',626,700,[160,319,484,645,805,970,1135,1300])
cut('s2','g2atk',712,790,[160,322,484,645,805,966,1126,1292],keep=[0,1,2,4,5])
cut('s2','g2skill',800,880,[160,328,487,640,768,925,1062,1222],keep=[0,2,3,5])
cut('s2','g2hit',888,962,[160,316,470,620,756,910],keep=[0,1,3,4])
cut('s2','g2death',974,1054,[160,330,497,688,890,1110,1300])
# ---- 이펙트 ----
piece('s2','pal',634,358,756,483); piece('s2','pal',758,358,882,483); piece('s2','pal',894,358,1012,483)
piece('s2','shield',1090,358,1244,483); piece('s2','boom',1288,356,1426,483)
for b in [(1080,165,1117,212),(1138,158,1183,217),(1196,150,1262,224),(1264,148,1350,228)]: piece('s1','orb',*b)
piece('s1','chg',1132,250,1222,325); piece('s1','chg',1224,236,1420,334)
def drop_pal(rgba):   # 등 뒤에 붙어 다니는 작은 유령 지우기: 위쪽 절반에서 후드(밝고 채도 낮은 천)보다 왼쪽에 있는 것을 비운다
    c=rgba[...,:3].astype(int); a=rgba[...,3]; h,w=a.shape
    hood=(a>200)&((c.max(-1)-c.min(-1))<55)&(c.max(-1)>165)
    hood=ndi.binary_opening(hood,iterations=1)
    lab,n=ndi.label(hood)
    if not n: return rgba
    sz=ndi.sum(hood,lab,range(1,n+1)); big=lab==(int(np.argmax(sz))+1)   # 가장 큰 천 덩어리 = 후드
    ys,xs=np.where(big); top=ys.min(); Hh=int(h*0.58)
    out=rgba.copy(); prev=None
    for y in range(0,Hh):
        row=np.where(big[y])[0]
        L=(row.min() if len(row) else (prev if prev is not None else int(np.percentile(xs,10))))
        if y<top: L=int(xs[ys<top+6].min()) if (ys<top+6).any() else L
        prev=L
        out[y,:max(0,L-2),3]=0
    return out
for nm in ['g2idle','g2walk','g2atk','g2skill','g2hit']:
    info[nm]=[(drop_pal(c),ax,ay) for c,ax,ay in info[nm]]
W=1600; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
Image.fromarray(at).save('gg.png'); Image.fromarray(at).save('gg.webp',lossless=True,method=6); json.dump(meta,open('gg.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
