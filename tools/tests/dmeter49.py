"""v6.49 딜미터기: 사슬 악마 사슬·창날 집계, 출처 없는 피해 0, 보스 딜미터기(HUD·결과창)  PYTHONPATH=tools python3 tools/tests/dmeter49.py"""
import asyncio, os
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        r = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.twins=true;G.SAVE.set.dmeter=true;G.startGame('twins');__lv(12);
          G.spawnBoss&&G.spawnBoss();const bs=G.boss;if(!bs)return {noboss:1};bs.x=G.P.x+120;bs.y=G.P.y;
          for(let i=0;i<240;i++){G.P.inv=99;G.P.hp=G.P.max;bs.x=G.P.x+110;bs.y=G.P.y;bs.hp=Math.max(bs.hp,bs.max*0.6);G.tick(1/30)}
          G.render();return {dm:Object.fromEntries(Object.entries(G.DMETER).map(([k,v])=>[G.dmName(k),Math.round(v)])),boss:Object.fromEntries(Object.entries(G.DBOSS).map(([k,v])=>[G.dmName(k),Math.round(v)]))}}""")
        print(r)
        await pg.screenshot(path=os.path.join(OUT, 'dm49_hud.png'))
        await pg.evaluate("()=>{__G.P.hp=0}")
        print('errs', pg.errs)
        await b.close()
asyncio.run(main())
