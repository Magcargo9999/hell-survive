"""v6.45 챌린지 맵 점검: PYTHONPATH=tools python3 tools/tests/chmap.py
① 맵 그림 가로·세로(띠 이음 합)가 CHM.w/h와 같은가 ② 걸을 수 있는 다각형 안 어디에 서도 화면이 허공(그림 밖)이 아닌가 ③ 리자드 Lv.5 안내에 해골 궁수 조건이 없는가"""
import asyncio, sys, os
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.evaluate("()=>{const G=__G;G.SAVE.set.speed=0;G.SAVE.ch.open=true;G.setChMode(true);G.startGame('gun');G.enemies.length=0}")
        r = await pg.evaluate("""()=>{const G=__G,C=G.CHM,q=C.poly;
          const sw=C.cols.reduce((a,[x,y])=>a+y-x,0)*C.s,sh=C.rows.reduce((a,[x,y])=>a+y-x,0)*C.s;
          const out={sizeOk:sw===C.w&&sh===C.h,sw,sh,w:C.w,h:C.h,bad:[]};
          const pts=[];for(let i=0;i<q.length;i++){const a=q[i],b=q[(i+1)%q.length];pts.push(a,[(a[0]+b[0])/2,(a[1]+b[1])/2])}
          const cv=document.querySelector('canvas'),cx=cv.getContext('2d');
          pts.forEach((a,i)=>{const dx=C.cx-a[0],dy=C.cy-a[1],l=Math.hypot(dx,dy),x=a[0]+dx/l*14,y=a[1]+dy/l*14;
            for(let k=0;k<150;k++){G.P.x=x;G.P.y=y;G.P.inv=99;G.tick(1/30);let g=0;while(G.state!=='play'&&g++<5)__s()}G.render();
            // 플레이어 발밑 화면 좌표 주변이 '허공색'(거의 검보라 단색)이 아닌지: 주변 40x40 평균 밝기와 분산
            const cam={x:Math.min(Math.max(x,G.W/2),C.w-G.W/2),y:Math.min(Math.max(y-20,G.H/2),C.h-G.H/2)};
            const sx=Math.round(G.W/2+(x-cam.x)),sy=Math.round(G.H/2+(y-cam.y));
            const d=cx.getImageData(Math.max(0,sx-60),Math.max(0,sy-30),120,40).data;let mx=0;for(let j=0;j<d.length;j+=4)mx=Math.max(mx,d[j]+d[j+1]+d[j+2]);
            if(mx<60)out.bad.push(i)});
          return out}""")
        print(r)
        ok = r['sizeOk'] and not r['bad']
        # 리자드 Lv.5 안내
        t = await pg.evaluate("""()=>{const G=__G;G.setChMode(false);G.startGame('lizard');__lv(5);const b=G.banner;return b?b.txt:null}""")
        print('lizard Lv5 banner:', t)
        ok = ok and (t is None or '해골' not in t)
        print('ERRS', pg.errs[:3]); print('PASS' if ok else 'FAIL')
        await b.close()
asyncio.run(main())
