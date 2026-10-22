"""v7.04 사슬 악마: 공속→회전 속도 · 창날 최대 체력 비례 피해  PYTHONPATH=tools python3 tools/tests/twin704.py"""
import asyncio, json
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        R = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.twins=true;const out={};
          for(const a of [1,1.5]){G.startGame('twins');const P=G.P;__lv(6);P.aspd=a;G.enemies.length=0;
            for(let i=0;i<40;i++){P.inv=0;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();}
            out['spd'+a]=Math.round(P.tw.spd);}
          G.startGame('twins');const P=G.P;__lv(6);G.enemies.length=0;const e=G.spawnEnemy(0,60);e.hp=e.max=100000;e.x=P.x+60;e.y=P.y;
          let d=0;for(let i=0;i<90;i++){P.inv=0;P.hp=P.max;e.x=P.tw.x;e.y=P.tw.y;G.tick(1/30);if(G.state!=='play')__s();}
          out.dealt=Math.round(e.max-e.hp);out.dm=Object.keys(G.DMETER).filter(k=>k.startsWith('tw')).map(k=>k+':'+Math.round(G.DMETER[k]));return out}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
