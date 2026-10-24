import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,620)
        await pg.evaluate("()=>{const G=__G;G.SAVE.chars.gun=true;G.SAVE.set.speed=0;G.startGame('gun');G.enemies.length=0;__lv(20);__run(30)}")
        r=await pg.evaluate("""()=>{const G=__G,P=G.P,o=[];G.enemies.length=0;P.skT=0;
          for(let k=0;k<3;k++){P.mag=['N','R','F','N','B','N'];P.magI=0;P.reloadT=0;G.shards.length=0;G.cast();
            for(let i=0;i<9;i++)G.tick(1/30);o.push(G.shards.filter(s=>s.src==='sk:roll').length+'/'+(G.rollQ?G.rollQ.n:'end'));for(let i=0;i<6;i++)G.tick(1/30);}
          return o}""")
        print(r,pg.errs); await b.close()
asyncio.run(main())
