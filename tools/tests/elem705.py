"""v7.05 빙결·점화 카드 + 조합(빙하 충격파·달궈진 칼날)  PYTHONPATH=tools python3 tools/tests/elem705.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        R = {}
        R['run'] = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;__lv(8);G.enemies.length=0;
          P.up.freeze=3;P.up.ignite=3;
          const mk=(hp,x)=>{const e=G.spawnEnemy(0,100);e.hp=e.max=hp;e.x=P.x+x;e.y=P.y;return e};
          const a=mk(20000,70),b=mk(20000,-70);
          let fz=0,ig=0;for(let i=0;i<30*12;i++){P.inv=0;P.hp=P.max;a.x=P.x+70;a.y=P.y;b.x=P.x-70;b.y=P.y;G.tick(1/30);if(G.state!=='play')__s();
            if(a.frzT>G.gt||b.frzT>G.gt)fz++;if(a.ignT>0||b.ignT>0)ig++;}
          return {fz,ig,igDmg:Math.round(G.DMETER.ignite||0),lost:Math.round(40000-a.hp-b.hp),dm:Object.keys(G.DMETER)}}""")
        R['syn'] = await pg.evaluate("""()=>{const G=__G,P=G.P;P.up.freeze=3;P.up.nova=3;P.up.ignite=3;P.up.blade=3;
          return G.availSyn().map(s=>s.id)}""")
        R['cards'] = await pg.evaluate("""()=>{const G=__G;return G.UPGRADES.filter(u=>u.id==='freeze'||u.id==='ignite').map(u=>[1,3,5].map(n=>u.txt(n)))}""")
        R['glacier'] = await pg.evaluate("""()=>{const G=__G,P=G.P;P.syn.glacier=true;P.up.nova=3;P.up.freeze=1;G.enemies.length=0;const e=G.spawnEnemy(0,100);e.hp=e.max=9999;e.x=P.x+90;e.y=P.y;
          for(let i=0;i<30*8;i++){P.inv=0;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();if(e.frzT>G.gt)return {frozen:true,rooted:e.rootT>G.gt};}
          return {frozen:false}}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;for(let i=0;i<5;i++){const e=G.spawnEnemy(i,80+i*20);e.x=P.x+90*Math.cos(i);e.y=P.y+90*Math.sin(i);e.frzT=G.gt+9;e.ignT=9}G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'elem_1.png'))
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
