"""v9.70 열충격: 점화→빙결, 빙결→점화(대장장이 검 igniteX 포함) 어느 순서로도 터진다"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG', timeout=90000)
        R = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P,o={};P.up.ignite=3;P.up.freeze=3;P.syn.shock=1;G.enemies.length=0;
          const mk=(x)=>{G.spawnEnemy();const e=G.enemies[G.enemies.length-1];e.x=P.x+x;e.y=P.y;e.hp=e.max=5000;return e};
          const a=mk(300);a.ignT=3;G.freezeE(a,true);o.ignThenFreeze=a.hp<5000;
          const b=mk(900);G.freezeE(b,true);G.igniteX(b,true);o.freezeThenIgnite=b.hp<5000;
          const c=mk(1500);let n=0;for(let i=0;i<400&&c.hp>=5000;i++){c.ignT=0;c.frzT=G.gt?G.gt+3:99999;G.procElem&&G.procElem(c);n++}o.procElemPop=c.hp<5000;return o}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
