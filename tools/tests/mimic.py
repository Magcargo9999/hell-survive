"""v7.02 미믹 습격(잭팟 머신 나쁜 보상): 룰렛 50:50 유지 · 미믹 2마리 돌진·처치 시 영혼 조각 1000씩  PYTHONPATH=tools python3 tools/tests/mimic.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        R = {}
        R['odds'] = await pg.evaluate("""()=>{const G=__G;let good=0,N=40000,ids={};for(let i=0;i<N;i++){const r=G.slotRoll();ids[r.id]=(ids[r.id]||0)+1;if(r.good)good++;}
          return {goodPct:+(good/N*100).toFixed(1),ids}}""")
        R['run'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=0;G.startGame('wolf');const P=G.P;__lv(6);G.enemies.length=0;G.spawnMimic(2);
          const ms=G.enemies.filter(e=>e.kind==='mimic');let hits=0,hpLost=0,lunges=0,last=ms[0].st,minD=1e9;
          for(let i=0;i<30*20;i++){const hb=P.hp;P.inv=0;G.tick(1/30);if(P.hp<hb){hits++;hpLost+=hb-P.hp;} if(G.state!=='play')__s();
            if(ms[0].st!==last){if(ms[0].st==='lunge')lunges++;last=ms[0].st;} minD=Math.min(minD,Math.hypot(ms[0].x-P.x,ms[0].y-P.y));
            P.hp=P.max; if(i===150)G.render();}
          return {n:ms.length,hp:Math.round(ms[0].max),hits,lunges,minD:Math.round(minD),alive:ms.filter(e=>e.hp>0).length}}""")
        await pg.evaluate("""()=>{const G=__G;for(const e of G.enemies){if(e.kind==='mimic'){e.st='wind';e.sT=0.2;}}G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'mimic_1.png'))
        R['kill'] = await pg.evaluate("""()=>{const G=__G,P=G.P;const ms=G.enemies.filter(e=>e.kind==='mimic');const s0=G.calcShards();
          for(const e of ms){G.hurtEnemy(e,e.max*2,1,0,0);}
          for(let i=0;i<10;i++)G.tick(1/30);G.render();
          return {gain:G.calcShards()-s0,mimicShards:P.mimicShards,left:G.enemies.filter(e=>e.kind==='mimic').length,udeath:G.udeath.length,banner:G.banner&&G.banner.txt}}""")
        await pg.screenshot(path=os.path.join(OUT, 'mimic_2.png'))
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
