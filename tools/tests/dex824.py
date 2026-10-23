import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1100,'height':760}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/hell-survive/build/hell_survive.html'); await pg.wait_for_function('window.__G&&__G.ready',timeout=90000)
        await pg.evaluate("()=>{const G=__G;G.SAVE.heart={inv:[],eq:[],n:0,got:{}};G.heartGain('rare','tox');G.heartGain('legend','eye');G.heartGain('epic','angel')}")
        await pg.evaluate("document.getElementById('dexBtn').click()")
        for t in ['char','mon','heart']:
            await pg.evaluate(f"document.querySelector('.dextabs button[data-dt={t}]').click()"); await pg.wait_for_timeout(300)
            print(t, await pg.evaluate("document.getElementById('dexSum').textContent"), await pg.evaluate("[...document.getElementById('dexList').children].filter(e=>e.style.display!=='none').length"))
            await pg.screenshot(path=f'/home/claude/hell-survive/build/dex824_{t}.png')
        print(errs); await b.close()
asyncio.run(main())
