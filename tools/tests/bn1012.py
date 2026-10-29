"""v10.12 보스전 안내 글씨: 크기 1배 · H키로 끄기/켜기"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{const G=__G;G.SAVE.diff.max=5;G.startGame('wolf');G.enterArena&&G.enterArena()}")
        for i in range(60):
            await pg.evaluate("()=>{__G.P.inv=99;__G.tick(1/30)}")
            if await pg.evaluate("()=>!!__G.boss"): break
            await pg.wait_for_timeout(30)
        r = {}
        r['on'] = await pg.evaluate("()=>{const G=__G;return [!!G.boss, G.state]}")
        await pg.evaluate("()=>{__G.setBanner?0:0}")
        await pg.keyboard.press('KeyH'); r['off'] = await pg.evaluate("()=>localStorage.getItem('hsBnHide')")
        await pg.keyboard.press('KeyH'); r['back'] = await pg.evaluate("()=>localStorage.getItem('hsBnHide')")
        print(r, pg.errs[:3]); print('OK' if r['off'] == '1' and r['back'] == '0' else 'FAIL'); await b.close()
asyncio.run(main())
