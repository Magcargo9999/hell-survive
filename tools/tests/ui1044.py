import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1700, 700)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE;Object.assign(S.chars,{ghost:true,octo:true,gun:true,twins:true});
          const T={wolf:1,snail:1};const keys=n=>typeof n==='string'?[n]:n.flatMap(keys);
          S.dex.seen={};for(const id of ['wolf','snail']) for(const k of keys(G.ROUTE_TREE?G.ROUTE_TREE[id]:[])) S.dex.seen[k]=1;
          return Object.keys(S.dex.seen).length}""")
        print('seen keys', r)
        await pg.evaluate("()=>{__G.buildCards()}"); await pg.wait_for_timeout(600)
        print(await pg.evaluate("()=>[...document.querySelectorAll('#charCards .card')].map(c=>c.dataset.c+':'+c.className.replace('card ','')).join(' | ')"))
        await pg.click('#charCards .card[data-c=snail]'); await pg.wait_for_timeout(300)
        await pg.keyboard.press('Escape')
        print(await pg.evaluate("()=>[...document.querySelectorAll('#charCards .card')].map(c=>c.dataset.c+':'+c.className.replace('card ','')).join(' | ')"))
        await pg.screenshot(path='build/ui/frames.png'); print('errs', pg.errs); await b.close()
asyncio.run(main())
