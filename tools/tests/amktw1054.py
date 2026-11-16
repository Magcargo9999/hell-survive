"""v10.54 각성한 원숭이 마왕 — 잔류 회오리: 생성 수 · 내 자리 회피 · 끌림 < 내 이속 · 화면"""
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
from amk1046 import START
JS = """([S,ph,kind])=>{const G=__G,P=G.P,e=G.boss,A=G.amk,M=G.IMAP;const cx=(M.X0+M.X1)/2,cy=(M.Y0+M.Y1)/2;
 G.AMW.tw=[];e.tele=[];A.q=[];e.ph=ph;e.hp=e.max*(ph===2?0.45:0.9);e.x=cx;e.y=cy-300;e.hide=false;P.spd=S;P.x=cx;P.y=cy;A.k=G.amkK();for(const k in A.cd)A.cd[k]=99;
 if(kind==='whirl')A.whirlStart();else A.twSpawn(G.AMK.twPh);
 let n=0,minD=1e9,pull=0,hits=0,hp0=0;for(let i=0;i<60*6;i++){P.x=cx;P.y=cy;P.inv=0;P.hp=P.max;G.tick(1/60);n=Math.max(n,G.AMW.tw.length);for(const o of G.AMW.tw)minD=Math.min(minD,Math.hypot(o.x-cx,o.y-cy))}
 // 끌림 측정: 가장 가까운 회오리 옆 100px에 세우고 1초
 const o=G.AMW.tw[0];let pr=0;if(o){for(const q of G.AMW.tw)q.hc=99;const a=Math.atan2(P.y-o.y,P.x-o.x);for(let i=0;i<60;i++){const x0=o.x+Math.cos(a)*100,y0=o.y+Math.sin(a)*100;P.x=x0;P.y=y0;P.inv=0;G.tick(1/60);pr=Math.max(pr,Math.hypot(P.x-x0,P.y-y0)*60)}}
 return {n,minD:Math.round(minD),pullMax:Math.round(pr),spd:Math.round(G.amkS()),ratio:+(pr/G.amkS()).toFixed(2)}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720); await pg.evaluate(START, 'wolf')
        await pg.evaluate("()=>{for(let i=0;i<90;i++){__G.P.hp=__G.P.max;__G.P.inv=1;__G.tick(1/30)}__G.AMW.tip={tw:1,wh:1}}")
        for S, ph, k in ((140, 1, 'whirl'), (280, 2, 'whirl'), (380, 2, 'ph')): print(S, ph, k, await pg.evaluate(JS, [S, ph, k]))
        await pg.evaluate("()=>{const G=__G,A=G.amk,P=G.P,e=G.boss;G.AMW.tw=[];for(const k in A.cd)A.cd[k]=99;A.k=1;A.twSpawn(5);for(let i=0;i<120;i++){P.inv=1;P.hp=P.max;G.tick(1/60)}}")
        await pg.wait_for_timeout(200); await pg.screenshot(path='build/amk/s_tw.png'); print('errs', pg.errs); await b.close()
asyncio.run(main())
