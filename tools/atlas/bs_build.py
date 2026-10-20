from seg import *
def ext(sh,y0,y1,x0,x1,thr=16):
    im=S[sh]; c=im[y0:y1,x0:x1]; bg=np.array([14,10,7.])
    d=np.abs(c-bg).max(-1); mn=c.mean(-1)
    gry=(np.abs(c[...,0]-c[...,2])<9)&(mn>17)&(mn<66)&(np.abs(c[...,0]-c[...,1])<9)
    hard=(d>thr)&~gry
    m=ndi.binary_closing(hard,np.ones((3,3))); m=ndi.binary_fill_holes(m)
    lab,n=ndi.label(m,np.ones((3,3)))
    for i in range(1,n+1):
        ys,xs=np.where(lab==i); h=np.ptp(ys)+1; w=np.ptp(xs)+1
        if len(ys)<14 or (h>40 and w<5) or (w>=10 and h<=6) or len(ys)<0.25*h*w and h<10: m[lab==i]=False
    soft=np.clip((d-6)/(thr-6),0,1)
    a=np.where(m,1.0,np.where(ndi.binary_dilation(m,iterations=1),soft,0))
    a=np.where(gry&~m,0,a)
    A=a[...,None]
    with np.errstate(divide='ignore',invalid='ignore'): u=np.where(A>0.999,c,(c-bg*(1-A))/np.maximum(A,1e-3))
    rgba=np.dstack([np.clip(u,0,255).astype(np.uint8),(a*255).astype(np.uint8)])
    ys,xs=np.where(a>0.03)
    return rgba[ys.min():ys.max()+1,xs.min():xs.max()+1], (y0+ys.min(), y0+ys.max(), x0+xs.min())
info={}
def frames(name,sh,y0,y1,boxes,anchor=True):
    L=[]
    for x0,x1 in boxes:
        r,(top,bot,left)=ext(sh,y0,y1,x0,x1); L.append((r,top,bot,left))
    base=int(np.median([b for _,_,b,_ in L]))
    for r,top,bot,left in L:
        op=r[...,3]>128; cols=np.where(op[-max(4,int(r.shape[0]*0.25)):].any(0))[0]   # 발(아래쪽) 기준 몸 중심
        ax=float(cols.mean()) if len(cols) else r.shape[1]/2
        info.setdefault(name,[]).append((r,round(ax,1),base-top))
def piece(name,sh,x0,y0,x1,y1):
    r,_=ext(sh,y0,y1,x0,x1); info.setdefault(name,[]).append((r,r.shape[1]/2,r.shape[0]/2))
# --- 1진화 ---
frames('b1idle','s1',495,580,[(37,118),(121,222),(226,328),(333,438),(440,534),(537,634)])
frames('b1walk','s1',495,580,[(670,750),(762,845),(858,937),(946,1026),(1028,1104),(1108,1184),(1188,1266),(1266,1342),(1348,1424)])
frames('b1atk','s1',635,722,[(40,140),(186,286),(333,436),(476,578),(612,710),(734,832)])
frames('b1skill','s1',778,885,[(26,150),(160,300),(310,424),(450,560),(582,710),(1302,1400)])
frames('b1hit','s1',955,1051,[(29,113),(121,199),(210,284),(290,370)])
frames('b1death','s1',940,1051,[(400,486),(496,585),(586,667),(667,750),(750,822),(822,893)])
# --- 최종 ---
frames('b2idle','s2',482,579,[(31,131),(136,240),(240,345),(348,450),(452,555),(557,650)])
frames('b2walk','s2',482,579,[(670,762),(764,860),(864,956),(957,1051),(1051,1143),(1145,1235),(1235,1328),(1329,1430)])
frames('b2atk','s2',615,712,[(30,136),(172,296),(328,444),(474,586),(606,712),(728,836)])
frames('b2skill','s2',752,847,[(30,147),(168,296),(312,433),(442,560),(578,690),(1302,1421)])
frames('b2hit','s2',940,1022,[(30,112),(112,195),(195,276),(276,352)])
frames('b2death','s2',925,1022,[(372,456),(456,541),(541,616),(616,690),(690,758),(758,806)])
# --- 투사체 · 폭발 ---
piece('bomb1','s1',1070,980,1130,1046)
piece('bomb2','s2',955,975,1000,1022)
piece('megab','s2',1008,955,1192,1030)
for i,(x0,x1) in enumerate([(1150,1206),(1206,1260),(1260,1318),(1318,1372),(1372,1422)]): piece('boom','s1',x0,985,x1,1048)
W=1800; x=y=sh=0; pos={}
for nm in info:
    for i,(c,ax,ay) in enumerate(info[nm]):
        h,w=c.shape[:2]
        if x+w>W: x=0; y+=sh+2; sh=0
        pos[(nm,i)]=(x,y); x+=w+2; sh=max(sh,h)
at=np.zeros((y+sh,W,4),np.uint8); meta={}
for (nm,i),(x,y) in pos.items():
    c,ax,ay=info[nm][i]; h,w=c.shape[:2]; at[y:y+h,x:x+w]=c; meta.setdefault(nm,[]).append([x,y,w,h,ax,int(ay)])
Image.fromarray(at).save('bs.png'); Image.fromarray(at).save('bs.webp',lossless=True,method=6); json.dump(meta,open('bs.json','w'))
print(at.shape,{k:(len(v),[f[3] for f in v]) for k,v in meta.items()})
# review sheet on magenta-ish mid bg
bgc=np.zeros_like(at[...,:3]); bgc[:]= (70,110,70); a=at[...,3:]/255; rv=(at[...,:3]*a+bgc*(1-a)).astype(np.uint8); Image.fromarray(rv).save('review.png')
