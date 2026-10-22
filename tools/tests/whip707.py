"""v7.07 사슬 휘두르기 넉백 = 사슬 길이 비례  PYTHONPATH=tools python3 tools/tests/whip707.py"""
import asyncio, json
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        R = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.twins=true;G.startGame('twins');window.__rt=0;window.__fin=0;const P=G.P;__lv(20);P.hp=P.max;G.enemies.length=0;
          const es=[100,200,300].map(d=>{const e=G.spawnEnemy(0,100);e.hp=e.max=1e6;e.noChase=1;e.sp=0;e.x=P.x+P.face*d;e.y=P.y;e.x0=e.x;e.kres=1;return e});
          const sk=G.P.skill||null;G.P.skT=0;G.cast();
          for(let i=0;i<60;i++){P.inv=9;P.hp=P.max;G.tick(1/30)}
          return {form:P.form,dist:es.map(e=>Math.round(Math.hypot(e.x-P.x,e.y-P.y))),lossPct:es.map(e=>+((1-e.hp/e.max)*100).toFixed(2))}}""")
        print(json.dumps(R)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
