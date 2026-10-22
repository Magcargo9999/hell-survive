"""v7.06 수호의 길 조건(Lv.10 전 누적 피해 400) · 경험치 +7.5%  PYTHONPATH=tools python3 tools/tests/liz706.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        R = {}
        R['taken'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.lizard=true;G.startGame('lizard');const P=G.P;P.hp=P.max=10000;
          const a=P.taken10;for(let i=0;i<10;i++){P.inv=0;G.hurt(30)}return {added:Math.round(P.taken10-a)}}""")
        for name, pre in (('low', 0), ('high', 450)):
            R[name] = await pg.evaluate("""(pre)=>{const G=__G;G.SAVE.chars.lizard=true;G.startGame('lizard');const P=G.P;P.taken10=pre;let g=0;
              while(g++<3000){const t=document.getElementById('levelTitle').textContent;
                if(G.state==='levelup'){ if(t.indexOf('갈림길')>=0)break; G.pick(0);continue}
                if(G.state==='evolve'){G.tick(1/30);continue}
                P.hp=P.max;P.inv=9;G.addExp(P.need);G.tick(1/30)}
              return {lvl:P.lvl,locked:G.choices.map(c=>!!c.locked),cond:(G.choices[1].cond||{}).txt}}""", pre)
        await pg.wait_for_timeout(400)
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
