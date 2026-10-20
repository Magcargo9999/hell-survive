import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
S={'s1':load('s1.png'),'s2':load('s2.png')}
for k,boxes in {'s1':[(0,910,152,1012),(596,910,742,1012)],'s2':[(0,910,150,1012),(586,905,722,1012),(0,760,150,860)]}.items():   # 피격·사망 이름표(글자) 지우기
    for x0,y0,x1,y1 in boxes: S[k][y0:y1,x0:x1]=np.array([10,12,13.])
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

cut('s1','l1idle',428,522,[170,355,556,770,978,1200,1415])
cut('s1','l1walk',546,642,[145,322,458,602,750,895,1055,1240,1415])
cut('s1','l1atk',662,764,[170,370,592,820,1040,1235,1415])
cut('s1','l1hit',910,1054,[118,272,418,572])
cut('s1','l1death',910,1054,[718,858,1002,1138,1268,1432])
cut('s2','l2idle',426,520,[148,350,556,762,976,1205,1420])
cut('s2','l2walk',534,634,[143,310,458,603,763,923,1098,1262,1428])
cut('s2','l2atk',646,750,[147,320,520,790,1020,1232,1428])
cut('s2','l2def',762,900,[112,292,452,622,802,968,1148,1432])
cut('s2','l2hit',912,1054,[96,252,398,575])
cut('s2','l2death',912,1054,[648,802,952,1102,1262,1432])
W=1600; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
Image.fromarray(at).save('lg.png'); Image.fromarray(at).save('lg.webp',lossless=True,method=6); json.dump(meta,open('lg.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
