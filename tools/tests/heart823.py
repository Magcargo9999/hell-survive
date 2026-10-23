import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1100,'height':760}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/hell-survive/build/hell_survive.html'); await pg.wait_for_function('window.__G&&__G.ready',timeout=90000)
        print(await pg.evaluate("""()=>{const G=__G;G.SAVE.heart={inv:[],eq:[],n:0,got:{}};G.HEART.drop=1;const a=G.rollHeartDrop('tox');for(const g of ['rare','epic','unique','legend'])G.heartGain(g,'tox');G.SAVE.heart.got={};G.SAVE.heart.eq=[];G.SAVE.heart.n=0;return {a}}"""))
        await pg.evaluate("document.getElementById('heartBtn').click()"); await pg.wait_for_timeout(500)
        await pg.screenshot(path='/home/claude/hell-survive/build/heart823.png'); print(errs); await b.close()
asyncio.run(main())
