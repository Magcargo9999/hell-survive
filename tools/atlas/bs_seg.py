import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as ndi
def load(f): return np.array(Image.open(f).convert('RGB')).astype(float)
S={'s1':load('s1.png'),'s2':load('s2.png')}
def gray_rows(im,y0,y1,x0,x1):
    out=[]
    for y in range(y0,y1):
        r=im[y,x0:x1]; g=(np.abs(r[:,0]-r[:,2])<8)&(r.mean(1)>17)&(r.mean(1)<60); out.append(g.mean())
    return np.array(out)
def mask_of(c,bg,thr=16):
    d=np.abs(c-bg).max(-1); mn=c.mean(-1); m=(d>thr)
    gry=(np.abs(c[...,0]-c[...,2])<9)&(mn>17)&(mn<66)&(np.abs(c[...,0]-c[...,1])<9)
    m&=~gry
    m=ndi.binary_closing(m,np.ones((3,3)),iterations=1)
    m=ndi.binary_fill_holes(m)
    lab,n=ndi.label(m,np.ones((3,3)))
    if n:
        sz=ndi.sum(m,lab,range(1,n+1)); m[np.isin(lab,np.where(sz<12)[0]+1)]=False
    return m
def groups(m,gap=5,minw=12):
    col=m.any(0); gs=[]; i=0; W=len(col)
    while i<W:
        if col[i]:
            j=i
            while j<W and (col[j:j+gap].any()): j+=1
            if j-i>=minw: gs.append((i,j))
            i=j
        else: i+=1
    return gs
def band_mask(im,y0,y1,x0,x1,thr=16):
    c=im[y0:y1,x0:x1]; bg=mode_bg(c); d=np.abs(c-bg).max(-1); m=d>thr
    cov=m.mean(1); strip=cov>0.42; m[strip]=False
    m2=ndi.binary_closing(m,np.ones((3,3))); m2=ndi.binary_fill_holes(m2)
    lab,n=ndi.label(m2,np.ones((3,3)))
    if n:
        sz=ndi.sum(m2,lab,range(1,n+1)); m2[np.isin(lab,np.where(sz<14)[0]+1)]=False
    return c,bg,m2,strip
def mode_bg(c):
    q=(c.reshape(-1,3)//4).astype(int); k=q[:,0]*4096+q[:,1]*64+q[:,2]; v,n=np.unique(k,return_counts=True); mm=v[np.argmax(n)]
    return c.reshape(-1,3)[k==mm].mean(0)
