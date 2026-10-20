import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
S={'s1':load('s1.png')}
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

cut('s1','idle',345,465,[126,275,435,615,796,978,1147,1294,1436])
cut('s1','walk',476,588,[126,279,444,596,740,880,1034,1185,1336])
cut('s1','atk',598,710,[126,297,480,688,1027,1228],keep=[0,1,2,4])
cut('s1','hit',716,818,[126,298,468,641,804])
cut('s1','death',830,932,[126,301,483,697,890])
W=1600; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
Image.fromarray(at).save('os.png'); Image.fromarray(at).save('os.webp',lossless=True,method=6); json.dump(meta,open('os.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
