import asyncio, sys
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 2150, 1160)
        await pg.evaluate("()=>{const S=__G.SAVE;Object.assign(S.chars,{ghost:true,octo:true,gun:true});S.diff.max=18;S.diff.clr=17;}")
        await pg.evaluate("()=>{__G.buildCards&&__G.buildCards()}")
        await pg.wait_for_timeout(800)
        r = await pg.evaluate("""()=>{const q=s=>document.querySelector(s);const c=q('#charCards .card');const cs=getComputedStyle(c,'::before');
          return {card:[c.offsetWidth,c.offsetHeight], src:cs.borderImageSource.slice(0,30), n:document.querySelectorAll('#charCards .card').length,
            over:[...document.querySelectorAll('#charCards .card')].map(b=>b.scrollHeight-b.clientHeight), start:[q('#startBtn').offsetWidth,q('#startBtn').offsetHeight]}}""")
        print(r); await pg.screenshot(path='build/ui/main.png')
        pg2 = await newpage(b, 1280, 720); await pg2.wait_for_timeout(500); await pg2.screenshot(path='build/ui/main_s.png', full_page=False)
        print('errs', pg.errs, pg2.errs); await b.close()
asyncio.run(main())
