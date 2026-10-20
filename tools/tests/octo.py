import asyncio,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs('build/audit/oc',exist_ok=True),sys

from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await newpage(b,1000,620); logs=[]
        pg.on('console',lambda m: logs.append(m.text[:300]))
        # 1) 히든 몹
        r=await pg.evaluate("()=>{const G=__G;G.SAVE.chars.octo=false;G.SAVE.diff.max=3;G.SAVE.diff.sel=2;G.SAVE.shards=500;G.startGame('wolf');const P=G.P;window.__lv(14);G.enemies.length=0;G.setT(300);G.spawnUniq('octo');const e=G.enemies.find(q=>q.uk==='octo');e.x=P.x+300;e.y=P.y;for(let i=0;i<150;i++){P.hp=P.max;G.tick(1/30)} return {tier:P.tier, st:e.st, tele:e.tele.length, hp:Math.round(e.hp)}}")
        print('mob',r)
        await pg.screenshot(path='build/audit/oc/m1.png')
        for i in range(3):
            await pg.evaluate("()=>{const G=__G,P=G.P;for(let i=0;i<25;i++){P.hp=P.max;G.tick(1/30)}}")
            await pg.screenshot(path='build/audit/oc/m%d.png'%(i+2))
        r=await pg.evaluate("()=>{const G=__G,P=G.P;const e=G.enemies.find(q=>q.uk==='octo'); G.hurtEnemy(e,1e7,1,0,0); for(let i=0;i<60;i++)G.tick(1/30); return {unlock:G.SAVE.chars.octo, banner:document.title}}")
        print('kill',r)
        # 2) 플레이어
        r=await pg.evaluate("()=>{const G=__G;G.SAVE.diff.sel=0;G.startGame('octo');const P=G.P;window.__lv(6);return {orbs:P.orbsN,ups:Object.keys(P.up).length,form:P.form}}")
        print('octo6',r)
        await pg.evaluate("()=>{const G=__G,P=G.P;P.skillTipT=0;G.enemies.length=0;for(let i=0;i<8;i++)G.spawnEnemy(Math.random()*6.28,250);for(let i=0;i<20;i++){P.inv=9;G.tick(1/30)}}")
        await pg.screenshot(path='build/audit/oc/p0.png')
        r=await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(12);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<12;i++)G.spawnEnemy(Math.random()*6.28,260);for(let i=0;i<10;i++){P.inv=9;G.tick(1/30)};P.skT=0;G.cast();for(let i=0;i<36;i++){P.inv=9;G.tick(1/30)}return {orbs:P.orbsN,form:P.form,sk:P.skill}}")
        print('octo12',r); await pg.screenshot(path='build/audit/oc/p1.png')
        for i in range(12): await pg.evaluate("()=>{const G=__G,P=G.P;P.inv=9;G.tick(1/30)}")
        await pg.screenshot(path='build/audit/oc/p1b.png')
        r=await pg.evaluate("()=>{const G=__G,P=G.P;window.__lv(22);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<14;i++)G.spawnEnemy(Math.random()*6.28,260);for(let i=0;i<10;i++){P.inv=9;G.tick(1/30)};P.skT=0;G.cast();for(let i=0;i<30;i++){P.inv=9;G.tick(1/30)}return {orbs:P.orbsN,form:P.form,sk:P.skill}}")
        print('octo22',r); await pg.screenshot(path='build/audit/oc/p2.png')
        print(pg.errs[:3], logs[:3]); await b.close()
asyncio.run(main())
