"""v8.13 수호령 총령 스킨: 연보라 총령 최종 진화에만 적용"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG && __G.IMG.sk_ghostG', timeout=90000)
        R = {}
        await pg.evaluate("()=>{const G=__G;G.SAVE.skin.own.ghostG=true;G.SAVE.skin.on={ghost:'ghostG'};G.SAVE.chars.ghost=true;G.startGame('ghost');}")
        R['f0'] = await pg.evaluate("()=>[__G.P.form,!!__G.skinOn('ghost')]")
        await pg.evaluate("()=>{__lv(10)}"); R['f1'] = await pg.evaluate("()=>[__G.P.form,!!__G.skinOn('ghost')]")
        await pg.evaluate("()=>{__lv(20);for(let i=0;i<40;i++){__G.P.inv=99;__G.tick(1/30);}__G.render();}")
        R['f2'] = await pg.evaluate("()=>[__G.P.form,!!__G.skinOn('ghost')]")
        await pg.evaluate("()=>{const G=__G;for(let i=0;i<8;i++)G.spawnEnemy(Math.random()*6.28,220);for(let i=0;i<50;i++){G.P.inv=99;G.tick(1/30);}G.render();}")
        await pg.screenshot(path=os.path.join(OUT, 'ghostg813.png')); print(R); await b.close()
asyncio.run(main())
