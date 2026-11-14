"""v10.52 각성한 원숭이 마왕 — 2페이즈 광폭 질주: 속도 배율 · 지속 시간(×K) · 화면"""
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
from amk1046 import START
JS = """(S)=>{const G=__G,P=G.P,e=G.boss,A=G.amk,M=G.IMAP;const cx=(M.X0+M.X1)/2,cy=(M.Y0+M.Y1)/2;
 e.tele=[];A.q=[];e.ph=2;e.hp=e.max*0.45;e.x=cx;e.y=cy;e.hide=false;P.spd=S;A.k=G.amkK();for(const k in A.cd)A.cd[k]=99;A.frenzyStart();
 let t=0,on=0,d0=0,d1=0,px=e.x,py=e.y;for(let i=0;i<60*14;i++){P.x=cx+Math.cos(i/60)*500;P.y=cy+Math.sin(i/60)*380;P.inv=1;P.hp=P.max;G.tick(1/60);const dd=Math.hypot(e.x-px,e.y-py);px=e.x;py=e.y;if(e.st==='chase'){if(e.fzT>0){on++;d1+=dd}else d0+=dd}}
 return {K:+A.k.toFixed(2),fzSec:+(on/60).toFixed(1),spdFz:Math.round(d1/Math.max(1,on/60))}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720); await pg.evaluate(START, 'wolf')
        await pg.evaluate("()=>{for(let i=0;i<90;i++){__G.P.hp=__G.P.max;__G.P.inv=1;__G.tick(1/30)}__G.AMW.tip={fz:1}}")
        for S in (140, 280, 360): print(S, await pg.evaluate(JS, S))
        await pg.evaluate(JS, 280); await pg.evaluate("()=>{const G=__G,A=G.amk,P=G.P,e=G.boss;for(const k in A.cd)A.cd[k]=99;A.frenzyStart();for(let i=0;i<90;i++){P.x+=4;P.inv=1;G.tick(1/60)}}")
        await pg.wait_for_timeout(200); await pg.screenshot(path='build/amk/s_frenzy.png'); print('errs', pg.errs); await b.close()
asyncio.run(main())
