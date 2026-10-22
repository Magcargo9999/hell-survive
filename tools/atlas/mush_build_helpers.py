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
