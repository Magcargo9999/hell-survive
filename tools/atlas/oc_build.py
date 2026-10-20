import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def load(f):
    im=Image.open(f); return np.array(im.convert('RGBA')).astype(float)
S={k:load(k+'.png') for k in ['adult','ele','tent','child']}
def mode_bg(c):
    q=(c.reshape(-1,3)//4).astype(int); k=q[:,0]*4096+q[:,1]*64+q[:,2]; v,n=np.unique(k,return_counts=True); m=v[np.argmax(n)]
    return c.reshape(-1,3)[k==m].mean(0)
def clean(a,minsz=10):
    m=a>0; lab,n=ndi.label(m,structure=np.ones((3,3)))
    if n: sz=ndi.sum(m,lab,range(1,n+1)); a[np.isin(lab,np.where(sz<minsz)[0]+1)]=0
    return a
def alpha_dark(c,BG,lo,hi):
    d=np.abs(c-BG).max(-1); core=d>hi; near=ndi.binary_dilation(core,iterations=2)
    return clean(np.where(d<=lo,0.0,np.where(core|near,1.0,(d-lo)/(hi-lo))))
def alpha_mag(c):
    # 마젠타 배경: G가 낮고 R·B가 높은 정도
    R,G,B=c[...,0],c[...,1],c[...,2]; mag=np.minimum(R,B)-G   # 배경이면 ~245
    a=np.clip((235-mag)/70,0,1); return clean(a)
def unblend(c,a,BG):
    A=np.clip(a,0,1)[...,None]
    with np.errstate(divide='ignore',invalid='ignore'): u=np.where(A>0.999,c,(c-BG*(1-A))/np.maximum(A,1e-3))
    return np.dstack([np.clip(u,0,255).astype(np.uint8),(np.clip(a,0,1)*255).astype(np.uint8)])
def feather(a,r=8):
    h,w=a.shape; yy=np.minimum(np.arange(h),np.arange(h)[::-1])[:,None]; xx=np.minimum(np.arange(w),np.arange(w)[::-1])[None,:]
    f=np.clip(np.minimum(yy,xx)/r,0,1); return np.where(a>0.9,a,a*f)
def cell(sheet,x0,y0,x1,y1):
    im=S[sheet]; c=im[y0:y1,x0:x1,:3]; al=im[y0:y1,x0:x1,3]
    if sheet=='ele': return np.dstack([c.astype(np.uint8),al.astype(np.uint8)])
    if sheet=='adult': a=alpha_mag(c); BG=np.array([248,3,250.]); return unblend(c,a,BG)
    BG=mode_bg(c); a=feather(alpha_dark(c,BG,12,34) if sheet=='child' else alpha_dark(c,BG,10,30),10); return unblend(c,a,BG)
def refine(sheet,y0,y1,cuts,win=20):
    im=S[sheet]
    if sheet=='ele': m=im[y0:y1,:,3]>40
    elif sheet=='adult': m=alpha_mag(im[y0:y1,:,:3])>0.3
    else: c=im[y0:y1,:,:3]; m=np.abs(c-mode_bg(c)).max(-1)>34
    col=m.sum(0); return [lo+int(np.argmin(col[lo:hi])) for c0 in cuts for lo,hi in [(max(0,c0-win),min(len(col)-1,c0+win))]]
info={}
def frames(name,sheet,y0,y1,cuts,keep=None,ref=True,anchor='bottom'):
    if ref: cuts=[cuts[0]]+refine(sheet,y0,y1,cuts[1:-1])+[cuts[-1]]
    lst=[]
    for j in range(len(cuts)-1):
        if keep is not None and j not in keep: continue
        rgba=cell(sheet,cuts[j],y0,cuts[j+1],y1); op=rgba[...,3]>128; ys,xs=np.where(op)
        bot=int(np.percentile(ys,99.3)); ax=float(np.median(xs)); lst.append((rgba,ax,bot))
    base=int(np.median([b for _,_,b in lst]))
    for rgba,ax,bot in lst:
        ys,xs=np.where(rgba[...,3]>8); x0,x1,a0,a1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        info.setdefault(name,[]).append((rgba[a0:a1,x0:x1],ax-x0,(base if anchor=='bottom' else bot)-a0))
def piece(name,sheet,x0,y0,x1,y1):
    rgba=cell(sheet,x0,y0,x1,y1); ys,xs=np.where(rgba[...,3]>8)
    cr=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]; info.setdefault(name,[]).append((cr,cr.shape[1]/2,cr.shape[0]/2))
# ---- 어린 문어 마법사 (0진화) ----
C7=[493,638,783,928,1073,1218,1363,1510]
frames('c_idle','child',34,128,C7); frames('c_walk','child',142,238,C7)
frames('c_atk','child',250,348,[493,638,783,928,1073,1190],ref=False); frames('c_hit','child',358,455,C7); frames('c_death','child',463,560,C7)
piece('c_orb','child',1310,265,1385,330)
# ---- 어른 문어 마법사 (1진화 · 최종 · 히든 몹) ----
frames('a_idle','adult',40,245,[497,690,848,1000,1162],ref=True)
frames('a_cast','adult',265,470,[538,768,1013,1260],ref=True)
frames('a_atk','adult',478,690,[5,230,430,657,896,1100,1220,1420],keep=[0,1,2,3,4,6],ref=True)
frames('a_death','adult',700,842,[5,267,541,789,1000,1320,1515],ref=True)
for b in [(240,890,312,960),(318,880,395,968)]: piece('a_orb','adult',*b)
for b in [(505,858,695,1012),(705,858,840,1012),(848,858,965,1012)]: piece('a_arc','adult',*b)
piece('a_cluster','adult',1262,268,1525,465)
# ---- 코끼리 돌진 ----
frames('e1','ele',85,325,[20,210,370,585,786,987,1189,1410,1660],anchor='bottom')
frames('e2','ele',355,612,[12,268,537,815,1095,1400,1660])
frames('e3','ele',640,890,[8,272,560,840,1190,1655])
# ---- 문어 다리 (최종 스킬 · 히든 몹 공격) ----
CX=[70,210,353,496,640,786,930,1078,1226,1375]
ROWS=[(86,180),(214,388),(408,620),(636,857),(878,1047)]
pick=[7,9,14,17,19,22,25,27,30,34,36,41,44,47]
for n in pick:
    r=(n-1)//10; c=(n-1)%10; y0,y1=ROWS[r]; x=CX[c]
    x0,x1=max(0,x-74),x+74
    frames('tent','tent',y0,y1,[x0,x1],ref=False)
SC={'a_':0.65,'e':0.6,'tent':0.7}
def scof(nm):
    for k,v in SC.items():
        if nm.startswith(k): return v
    return 1.0
for nm in list(info):
    k=scof(nm)
    if k==1.0: continue
    L=[]
    for c,ax,ay in info[nm]:
        h,w=c.shape[:2]; im=Image.fromarray(c).resize((max(1,round(w*k)),max(1,round(h*k))),Image.BOX); L.append((np.array(im),ax*k,ay*k))
    info[nm]=L
W=2000; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
Image.fromarray(at).save('oc.png'); Image.fromarray(at).save('oc.webp',lossless=True,method=6); json.dump(meta,open('oc.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
