"""∞ 챌린지: 산소 게이지가 필드·마왕전 모두에서 그려지는지"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.clr=29;G.SAVE.diff.max=5;const c=G.ctx,f=c.fillText.bind(c);window.__n=0;c.fillText=function(t,...a){if(typeof t==='string'&&t.indexOf('🫧')>=0)window.__n++;return f(t,...a)}}""")
        await pg.evaluate("()=>{const S=__G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38}")
        await pg.evaluate("()=>__G.startChallenge('wolf')")
        for _ in range(160):
            if await pg.evaluate("()=>__G.state==='play'&&!!__G.chal"): break
            await pg.wait_for_timeout(250)
        r = await pg.evaluate("""async()=>{const G=__G,P=G.P;P.inv=999;P.need=1e12;P.lvl=20;G.chal.next=99;const o={};
          const run=async(n)=>{window.__n=0;for(let i=0;i<n;i++){P.inv=999;P.hp=P.max;G.tick(1/30);await new Promise(q=>setTimeout(q,16))}return window.__n};
          o.field=await run(90);o.o2f=Math.round(P.o2);
          G.chal.usedB=[];G.chBossCall();G.chal.siren=0.01;for(let i=0;i<200&&!(G.boss&&G.boss.hp>0);i++){P.inv=999;G.tick(1/30);await new Promise(q=>setTimeout(q,10))}
          o.boss=G.boss&&G.boss.bk;o.bossDrawn=await run(90);o.o2b=Math.round(P.o2);return o}""")
        print(r); print('errs', pg.errs[:5]); await b.close()
asyncio.run(main())
