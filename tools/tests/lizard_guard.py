import asyncio,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs('build/audit/lg',exist_ok=True),sys

from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await newpage(b,1000,620); logs=[]
        pg.on('console',lambda m: logs.append(m.text[:300]))
        await pg.evaluate("()=>{__G.SAVE.chars.lizard=true;__G.startGame('lizard');window.__rt=1;}")
        r=await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(12);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<10;i++)G.spawnEnemy(Math.random()*6.28,200);for(let i=0;i<30;i++){P.hp=P.max;G.tick(1/30)};return {route:P.route,form:P.form,skill:P.skill,max:P.max,regen:P.regen}}")
        print(r); await pg.screenshot(path='build/audit/lg/t1.png',clip={'x':300,'y':160,'width':400,'height':300})
        r=await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(22);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<14;i++)G.spawnEnemy(Math.random()*6.28,120);for(let i=0;i<10;i++){P.inv=0;G.tick(1/30)};P.skT=0;G.cast();const h0=P.hp;let k0=P.kills;for(let i=0;i<45;i++){P.inv=Math.min(P.inv,0.12);G.enemies.forEach(e=>{if(e.hp>0){e.x+= (P.x-e.x)*0.3;e.y+=(P.y-e.y)*0.3}});G.tick(1/30)};return {fin:P.fin,form:P.form,skill:P.skill,shell:P.shellT,hpdiff:h0-P.hp,kills:P.kills-k0}}")
        print(r); await pg.screenshot(path='build/audit/lg/t2.png',clip={'x':300,'y':160,'width':400,'height':300})
        print(pg.errs[:3],logs[:3]); await b.close()
asyncio.run(main())
