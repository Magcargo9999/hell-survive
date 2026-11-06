import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        await pg.wait_for_timeout(1500)
        for bk in sys.argv[1:]:
            await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.clr=29;G.SAVE.diff.max=5;G.SAVE.diff.sel=0;G.SAVE.shards=1e6;G.startRush('wolf')}""")
            await pg.evaluate("""()=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(0);continue}if(__s())continue;if(G.state==='play'&&G.rush.init){G.tick(1/30);continue}break}}""")
            await pg.evaluate("""async([bk])=>{const G=__G,r=G.rush;r.ord=[bk,bk,bk,bk];r.i=2;r.ph='prep';r.wait=0;
              for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&r.ph==='fight')break;if(i%20===0)await new Promise(q=>setTimeout(q,30))}
              G.P.skillTipT=0;G.boss.invul=true;for(let i=0;i<90;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30)}}""", [bk])
            await pg.evaluate('()=>{__G.P.skillTipT=10}'); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'build/o2shot_{bk}.png')
        await b.close()
asyncio.run(main())
