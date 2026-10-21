"""챌린지 모드 도트: 절단안의 짐승(cm) · 심연의 촉수마왕(ab) 아틀라스. 시트는 실행 폴더에 cm_sheet.png / ab_sheet.png
자르기 · 배경 제거(어두운 배경색과의 차이로 알파) · 배율만 (재색칠 없음)"""
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
# ---- 절단안의 짐승 (미니 보스) · 원본은 왼쪽을 본다 ----
C=load('cm_sheet.png')
frames('idle',C,470,590,[596,790,1000,1210,1404],[(580,440,800,478)])
frames('walk',C,628,734,[36,255,490,703,920,1146,1400],[(20,600,245,640)])
frames('atk',C,772,891,[36,228,480,720,990,1215,1418],[(20,755,240,802)])
frames('hit',C,935,1063,[36,225,410,592],[(20,915,240,960)])
frames('death',C,935,1063,[624,765,905,1060,1225,1422],[(612,915,822,960)])
# ---- 심연의 촉수마왕 ----
A=load('ab_sheet.png')
piece('body',A,858,56,1093,263,14,40)
piece('eye',A,1366,334,1424,392,16,46)
piece('eye2',A,1318,381,1380,438,16,46)
for nm,b in [('jelly',(1320,508,1382,552)),('imp',(1384,558,1424,608)),('spiky',(1245,554,1288,604)),('tent',(1288,552,1338,608)),('tent',(1342,554,1388,608)),('tent',(1383,496,1424,553))]:
    piece(nm,A,*b,14,40,ay='bot')
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
pack(['idle','walk','atk','hit','death'],'cm')
pack(['body','eye','eye2','jelly','imp','spiky','tent'],'ab')
# ---- 챌린지 맵: 그대로 (무손실 webp) ----
Image.open('chmap.png').convert('RGB').save('chmap.webp',lossless=True,method=6)
