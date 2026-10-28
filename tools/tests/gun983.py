import asyncio, sys
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        await pg.evaluate("()=>{__G.startGame('gun')}")
        await pg.wait_for_function("__G.state==='play'", timeout=60000)
        r = await pg.evaluate("""()=>{const G=__G,P=G.P; __lv(21);
          const ids=G.cardDefs().map(u=>u.id);
          P.up.gRico=3; let R=0,N=3000; for(let i=0;i<N;i++){ if(G.gunRoll1()==='R')R++; }
          const syn=G.SYNERGIES.map(s=>s.id);
          const s={gun:'R',dmg:100,d0:100,pierce:4,hit:new Set(),x:0,y:0,vx:900,vy:0,life:1};
          G.gunHit(s,{x:50,y:0,r:10,hp:5,max:5}); G.gunHit(s,{x:90,y:0,r:10,hp:5,max:5});
          return {rico:ids.includes('gRico'),mag:ids.includes('gMag'),synMag:syn.includes('gEmberMag'),rate:R/N,dmg:s.dmg,n:G.gunMagN()}}""")
        print(r, errs)
        await b.close()
asyncio.run(main())
