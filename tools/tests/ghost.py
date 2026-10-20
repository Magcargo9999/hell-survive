import asyncio,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs('build/audit/gg',exist_ok=True)
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await newpage(b,1000,620)
        await pg.evaluate("()=>{__G.SAVE.chars.ghost=true;__G.startGame('ghost')}")
        await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(12);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<20;i++){P.inv=9;G.tick(1/30)};for(let i=0;i<8;i++)G.spawnEnemy(Math.random()*6.28,260);for(let i=0;i<14;i++){P.inv=9;G.tick(1/30)};P.skT=0;G.cast();for(let i=0;i<9;i++){P.inv=9;G.tick(1/30)}}")
        r1=await pg.evaluate("()=>({f:__G.P.form,sk:__G.P.skill,lv:__G.P.lvl})")
        await pg.screenshot(path='build/audit/gg/t1.png')
        await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(22);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<40;i++){P.inv=9;G.tick(1/30)};for(let i=0;i<10;i++)G.spawnEnemy(Math.random()*6.28,300);for(let i=0;i<20;i++){P.inv=9;G.tick(1/30)}}")
        r2=await pg.evaluate("()=>{const G=__G,P=G.P; const n0=(P.pals||[]).length; P.inv=0; const h0=P.hp; G.enemies.forEach(e=>{e.x=P.x+5;e.y=P.y});G.tick(1/30); return {f:P.form,sk:P.skill,pals:n0,after:(P.pals||[]).length,hp:[h0,P.hp]}}")
        for i in range(6): await pg.evaluate("()=>{__G.tick(1/30)}")
        await pg.screenshot(path='build/audit/gg/t2.png'); print(r1,r2,pg.errs[:3]); await b.close()
asyncio.run(main())
