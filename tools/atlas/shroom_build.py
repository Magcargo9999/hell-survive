"""v6.61 히든 마물 '대형 버섯 괴물'(지하 6~10층): 사용자 시트(shroom_sheet.png)에서 대기 7 · 이동 8 · 피격 6 · 사망 5 · 독 웅덩이 1장
자르기 · 시트에 들어 있는 투명도 그대로(옅은 안개 알파<48은 0) · 배율만 (재색칠 없음). 출력 sh.webp / sh.json"""
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
info={}
def cut(S,x0,y0,x1,y1,lo,hi,mask=None):
    c=S[y0:y1,x0:x1]; BG=mode_bg(c); a=alpha(c,BG,lo,hi)
    if mask:
        for (mx0,my0,mx1,my1) in mask: a[max(0,my0-y0):max(0,my1-y0),max(0,mx0-x0):max(0,mx1-x0)]=0
    return unblend(c,a,BG)
def refine(S,y0,y1,cuts,win=24,T=30):
    c=S[y0:y1]; m=np.abs(c-mode_bg(c)).max(-1)>T; col=m.sum(0)
    return [cuts[0]]+[lo+int(np.argmin(col[lo:hi])) for c0 in cuts[1:-1] for lo,hi in [(c0-win,c0+win)]]+[cuts[-1]]
def frames(name,S,y0,y1,cuts,mask=None,lo=14,hi=34):
    cuts=refine(S,y0,y1,cuts); lst=[]
    for j in range(len(cuts)-1):
        rgba=cut(S,cuts[j],y0,cuts[j+1],y1,lo,hi,mask); op=rgba[...,3]>128; ys,xs=np.where(op)
        bot=int(np.percentile(ys,99.5)); low=op[int(bot*0.62):bot+1]; lx=np.where(low)[1]
        lst.append((rgba,float(np.median(lx)),bot))
    base=int(np.median([b for _,_,b in lst]))
    for rgba,ax,bot in lst:
        ys,xs=np.where(rgba[...,3]>8); x0,x1,a0,a1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        info.setdefault(name,[]).append((rgba[a0:a1,x0:x1],ax-x0,base-a0))
def piece(name,S,x0,y0,x1,y1,lo=14,hi=40,ay='mid'):
    rgba=cut(S,x0,y0,x1,y1,lo,hi); ys,xs=np.where(rgba[...,3]>8)
    cr=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]; info.setdefault(name,[]).append((cr,cr.shape[1]/2,cr.shape[0] if ay=='bot' else cr.shape[0]/2))
S=load('shroom_sheet.png'); SA=np.array(Image.open('shroom_sheet.png').convert('RGBA'))
def cut(_S,x0,y0,x1,y1,lo=0,hi=0):
    c=SA[y0:y1,x0:x1].copy(); a=c[...,3].astype(float); a[a<48]=0; c[...,3]=clean(a,8).astype(np.uint8); return c
def F(name,y0,y1,boxes,lo=22,hi=52):
    lst=[]
    for (x0,x1) in boxes:
        rgba=cut(S,x0,y0,x1,y1,lo,hi); op=rgba[...,3]>128; ys,xs=np.where(op)
        bot=int(np.percentile(ys,99.5)); lst.append((rgba,float(np.median(xs[ys>bot*0.75])),bot))
    base=int(np.median([b for _,_,b in lst]))
    for rgba,ax,bot in lst:
        ys,xs=np.where(rgba[...,3]>8); x0,x1,a0,a1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        info.setdefault(name,[]).append((rgba[a0:a1,x0:x1],ax-x0,base-a0))
F('idle',50,161,[(505,628),(645,751),(764,874),(882,986),(1003,1106),(1120,1222),(1237,1345)])
F('walk',200,318,[(503,624),(638,748),(765,877),(889,999),(1006,1114),(1124,1241),(1247,1362),(1372,1507)])
F('hit',514,617,[(501,628),(655,779),(797,902),(929,1043),(1078,1193)])
F('death',662,774,[(515,642),(662,782),(794,950),(955,1100),(1104,1240)])
piece('pool',S,636,836,740,956,22,52,ay='mid')
def pack(names,fn):
    W=1600; x=y=sh=0; pos={}
    for nm in names:
        for i,(c,ax,ay) in enumerate(info[nm]):
            h,w=c.shape[:2]
            if x+w>W: x=0; y+=sh+2; sh=0
            pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
    at=np.zeros((y+sh,W,4),np.uint8); meta={}
    for (nm,i),(x,y) in pos.items():
        c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,round(float(ax),1),int(ay)])
    im=Image.fromarray(at); im.save(fn+'.png'); im.save(fn+'.webp',lossless=True,method=6); json.dump(meta,open(fn+'.json','w'),separators=(',',':'))
    print(fn,at.shape,{k:(len(v),[f[2:4] for f in v]) for k,v in meta.items()})
pack(['idle','walk','hit','death','pool'],'sh')
