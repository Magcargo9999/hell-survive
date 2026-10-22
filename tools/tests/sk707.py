"""v7.07 스켈레톤 마왕 결계: 첨탑 도트 · 20초 미파괴 시 체력 15% 회복 · 해골 전사 2마리  PYTHONPATH=tools python3 tools/tests/sk707.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.mimic', timeout=60000)
        await pg.wait_for_timeout(1500)
        R = {}
        R['setup'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=5;G.SAVE.shards=999;G.SAVE.diff.sel=3;G.startGame('ghost');const P=G.P;P.bossK='skel';__lv(25);P.hp=P.max=99999;G.enemies.length=0;G.raiseCastle();G.enterArena();
          for(let i=0;i<30*6;i++){P.inv=9;G.tick(1/30);if(G.state!=='play')__s();}
          const b=G.boss;b.hp=b.max*0.6;for(let i=0;i<30*5;i++){P.inv=9;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();}
          return {bk:b.bk,shield:b.shield,tow:b.tow,adds:G.enemies.filter(e=>e.adds).length,skm:G.enemies.filter(e=>e.kind==='skm').length,hp:+(b.hp/b.max).toFixed(2)}}""")
        await pg.screenshot(path=os.path.join(OUT, 'sk707_1.png'))
        R['heal'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;const h0=b.hp/b.max;let t=0,healed=false;
          for(let i=0;i<30*26&&!healed;i++){P.inv=9;P.hp=P.max;for(const e of G.enemies)if(e.adds)e.hp=e.max;const h=b.hp;G.tick(1/30);t+=1/30;if(b.hp>h+b.max*0.1)healed=true;if(G.state!=='play')__s();}
          return {healed,t:+t.toFixed(1),h0:+h0.toFixed(2),h1:+(b.hp/b.max).toFixed(2)}}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P;const t=G.enemies.find(e=>e.kind==='skh');if(t){P.x=t.x;P.y=t.y+150;}G.boss&&(G.boss.shield=true);for(let i=0;i<5;i++)G.tick(1/30);G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'sk707_2.png'))
        R['break0']=0
        R['break'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(const e of G.enemies)if(e.kind==='skh')e.hp=0;
          for(let i=0;i<10;i++){P.inv=9;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();}
          return {shield:b.shield,adds:G.enemies.filter(e=>e.adds&&e.hp>0).length}}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
