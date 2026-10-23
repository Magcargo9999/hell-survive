import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1000,'height':700}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/hell-survive/build/hell_survive.html'); await pg.wait_for_function('window.__G&&__G.ready',timeout=90000)
        await pg.wait_for_timeout(1500); print('menu playT', await pg.evaluate("__G.SAVE.playT"))
        await pg.evaluate("__G.startGame('wolf')"); await pg.wait_for_timeout(3000)
        t=await pg.evaluate("__G.SAVE.playT"); print('after 3s run', round(t,1))
        await pg.keyboard.press('KeyP'); await pg.wait_for_timeout(1500); t2=await pg.evaluate("__G.SAVE.playT"); print('paused', round(t2-t,2))
        await pg.evaluate("document.getElementById('setBtn')&&document.getElementById('setBtn').click()"); await pg.wait_for_timeout(300)
        print(await pg.evaluate("document.getElementById('setPlay').textContent")); await pg.screenshot(path='/home/claude/hell-survive/build/playt825.png')
        await pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); print(errs); await b.close()
asyncio.run(main())
