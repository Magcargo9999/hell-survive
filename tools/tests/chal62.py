"""v6.62 챌린지: 원거리 재생 +0.5 · 경험치통 · 잡몹 공격 · 미니보스 체력 · 버섯 마물 · 버섯 괴물 2회  PYTHONPATH=tools python3 tools/tests/chal62.py"""
import asyncio, json
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.sh', timeout=60000)
        R = await pg.evaluate("""()=>{const G=__G;G.SAVE.ch.open=true;G.SAVE.chars.gun=true;const o={};
          for(const c of ['wolf','snail','gun']){G.setChMode(true);G.startGame(c);o[c]={regen:+G.P.regen.toFixed(2),need:G.P.need};G.setChMode(false);}
          G.startGame('wolf');o.normalNeed=G.P.need;
          G.setChMode(true);G.startGame('wolf');const P=G.P;G.setT(900);for(let i=0;i<120;i++)G.spawnEnemy();
          o.mobs=[...new Set(G.enemies.filter(e=>e.kind==='mob').map(e=>e.spec.name))];o.dmgT=+G.chDmgT().toFixed(2);
          G.enemies.length=0;G.spawnUniq('shroom');G.enemies.length=0;P.uniqSeen.shroom=false;G.spawnUniq('shroom');o.seen2=P.uniqSeen.shroom;o.shN=P.shN;
          for(let i=0;i<600;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();}
          G.chEvent(10);o.ev=G.enemies.map(e=>e.kind+':'+Math.round(e.max)).slice(0,3);G.setChMode(false);return o}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
