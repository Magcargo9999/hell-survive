"""v10.20: 똥바람은 rush.paused()여도 계속 분다"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
import h301
PICK = """(want)=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;
  if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(want===5?1:0);continue}
  if(__s())continue; if(G.state==='play'&&G.rush&&G.rush.init){G.tick(1/30);continue} break}
  return [G.state,G.P.lvl,G.rush.totalCardsPicked]}"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.diff.clr=29;S.diff.max=5;S.dex.kills={boss:1,boss2:1,boss3:1,boss4:1};S.heart.inv=[];S.heart.eq=[];G.startRush('wolf')}""")
        await pg.evaluate(PICK, 2)
        r = await pg.evaluate("""async()=>{const G=__G;
          for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&G.rush.ph==='fight')break;if(i%20===0)await new Promise(r=>setTimeout(r,30))}
          const R=G.rush;R.modifiers=['o2','cross','wind'];R.paused=()=>true;R.skipMod=()=>false;R.wind=null;
          for(let i=0;i<5;i++)G.tick(1/30);const x0=G.P.x,y0=G.P.y;for(let i=0;i<30;i++){G.P.inv=99;G.tick(1/30)}
          return {ph:R.ph,boss:!!G.boss,st:G.state,has:R.has('wind'),off:R.wind&&R.wind.off,moved:Math.hypot(G.P.x-x0,G.P.y-y0)}}""")
        print(r, pg.errs[:3]); print('OK' if r['off'] is False and r['moved']>20 else 'FAIL'); await b.close()
asyncio.run(main())
