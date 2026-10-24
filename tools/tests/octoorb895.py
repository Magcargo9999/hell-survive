import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,700)
        r=await pg.evaluate("""()=>{const G=__G;G.startGame('octo');const P=G.P||G.getP&&G.getP();return typeof G.cardDefs}""")
        print(r); 
        r=await pg.evaluate("""()=>{const G=__G;const d=G.cardDefs?G.cardDefs():[];return d.map(u=>u.id).includes('orb')}""")
        print(r,pg.errs); await b.close()
asyncio.run(main())
