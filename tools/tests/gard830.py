"""v8.30 지하 16~20층 악마 식물원: 필드·보스맵 스크린샷 + 오류 확인"""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('file:///home/claude/hell-survive/build/hell_survive.html'); await pg.wait_for_function('window.__G&&__G.ready',timeout=90000)
        await pg.wait_for_function('__G.IMG&&__G.IMG.gfloor&&__G.IMG.gprops&&__G.IMG.gmap',timeout=60000)
        for t in (10,14):
            await pg.evaluate(f"()=>{{const G=__G;G.SAVE.diff.max=19;G.SAVE.shards=99999;G.SAVE.diff.sel={t};G.startGame('wolf');}}")
            await pg.wait_for_timeout(1200)
            print(t, await pg.evaluate("[__G.P.tier,__G.P.fset,__G.P.bossK]"))
        await pg.screenshot(path='/home/claude/hell-survive/build/gard_field.png')
        await pg.evaluate("()=>{const G=__G;G.P.x+=900;G.P.y+=400}"); await pg.wait_for_timeout(600); await pg.screenshot(path='/home/claude/hell-survive/build/gard_field2.png')
        await pg.evaluate("()=>{const G=__G;G.raiseCastle();G.enterArena();}"); await pg.wait_for_timeout(2500)
        print('arena', await pg.evaluate("[!!__G.arena&&__G.arena.gard, !!__G.boss, __G.boss&&__G.boss.bk]"))
        await pg.screenshot(path='/home/claude/hell-survive/build/gard_boss.png')
        print('inPoly', await pg.evaluate("(()=>{const G=__G,b=G.boss,P=G.P;return [G.inPoly?G.inPoly(b.x,b.y):'?', G.inPoly?G.inPoly(P.x,P.y):'?']})()"))
        print(errs[:5]); await b.close()
asyncio.run(main())
