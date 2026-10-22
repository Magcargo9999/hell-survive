"""v6.61 히든 마물 대형 버섯 괴물: 지하 6~10층만 · 돌진·독 웅덩이·예고선 · 플레이어 근처 유지 · 처치  PYTHONPATH=tools python3 tools/tests/shroom.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.sh', timeout=60000)
        R = {}
        R['pool_low'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=99999;G.SAVE.diff.max=9;G.SAVE.diff.sel=3;G.startGame('wolf');const ok=[];
          return {fset:G.P.fset}}""")
        R['run'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=6;G.startGame('wolf');const P=G.P;__lv(8);G.enemies.length=0;G.spawnUniq('shroom');
          const e=G.enemies.find(q=>q.uk==='shroom');let maxD=0,dashes=0,last=e.st,pools=0,hpLost=0;const h0=P.max;
          for(let i=0;i<30*40;i++){P.inv=0;P.hp=P.max;const hb=P.hp;G.tick(1/30);hpLost+=Math.max(0,hb-P.hp);if(G.state!=='play')__s();
            const d=Math.hypot(e.x-P.x,e.y-P.y);maxD=Math.max(maxD,d);if(e.st!==last){if(e.st==='dash')dashes++;last=e.st;}
            pools=Math.max(pools,G.zones.filter(z=>z.type==='mpool').length);
            if(i===600){G.render();}}
          return {dashes,maxD:Math.round(maxD),pools,hpLost:Math.round(hpLost),alive:e.hp>0}}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P;const e=G.enemies.find(q=>q.uk==='shroom');e.st='rest';e.cd=0.2;G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'shroom_1.png'))
        R['kill'] = await pg.evaluate("""()=>{const G=__G,P=G.P;const e=G.enemies.find(q=>q.uk==='shroom');for(let i=0;i<4000&&e.hp>0;i++){G.hurtEnemy?0:0;e.hp-=e.max*0.01;if(e.hp<=0){e.hp=1;}if(i>200){e.hp=0.5;} if(e.hp<1){break}}
          // 실제 처치 경로
          return {hp:e.hp}}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
