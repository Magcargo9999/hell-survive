"""v8.07 현무 리저드 스킨: 수호의 길 최종 진화에만 적용"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG && __G.IMG.sk_lizG', timeout=90000)
        await pg.evaluate("()=>{const G=__G;G.SAVE.skin.own.lizG=true;G.SAVE.skin.on={lizard:'lizG'};G.startGame('lizard');}")
        R = {}
        R['start'] = await pg.evaluate("()=>!!__G.skinOn('lizard')")
        await pg.evaluate("()=>{__lv(10)}")
        R['sel'] = await pg.evaluate("()=>({st:__G.state,form:__G.P.form,route:__G.P.route})")
        for rt in ['guard','sword']:
            await pg.evaluate("(rt)=>{const G=__G;G.startGame('lizard');__lv(10);if(G.P.route!==rt&&G.applyEvo)try{G.applyEvo(rt)}catch(e){}}", rt)
            R[rt] = await pg.evaluate("()=>({form:__G.P.form,route:__G.P.route,on:!!__G.skinOn('lizard')})")
        await pg.evaluate("()=>{const G=__G;G.startGame('lizard');__lv(20);for(let i=0;i<40;i++){G.P.inv=99;G.tick(1/30);}G.render();}")
        R['final'] = await pg.evaluate("()=>({form:__G.P.form,route:__G.P.route,on:!!__G.skinOn('lizard')})")
        await pg.screenshot(path=os.path.join(OUT,'lizg807.png'))
        print(R); await b.close()
asyncio.run(main())
