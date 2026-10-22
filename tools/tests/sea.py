"""v7.10 지하 11~15층 어인섬 세트: 필드 바닥·소품·버섯형 악마 · 버섯 보스맵(마왕 4종) · 챌린지/1~5층은 그대로
PYTHONPATH=tools python3 tools/tests/mush.py   (스크린샷 build/shots/sea_*.png)"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.smap && __G.sspecies.length', timeout=60000)
        R = {}
        R['field'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=99999;G.SAVE.diff.max=14;G.SAVE.diff.sel=12;G.startGame('wolf');const P=G.P;
          for(let i=0;i<60*30;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();}
          const sp=new Set(G.enemies.filter(e=>e.kind==='mob').map(e=>e.spec.name));return {tier:P.tier,fset:P.fset,mobs:[...sp],n:G.enemies.length,ms:G.sspecies.length}}""")
        await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, 'sea_field.png'))
        for bk in ['monkey', 'eye', 'skel', 'angel']:
            R[bk] = await pg.evaluate("""(bk)=>{const G=__G;G.SAVE.diff.sel=11;G.startGame('wolf');const P=G.P;P.bossK=bk;__lv(10);G.raiseCastle();G.enterArena();
              for(let i=0;i<60;i++){G.tick(1/30);} const b=G.boss; let out=0;
              for(let i=0;i<900;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s(); if(G.arena&&!G.MMAP)out++;}
              return {sea:!!(G.arena&&G.arena.sea),bk:G.boss&&G.boss.bk,bx:G.boss&&Math.round(G.boss.x),by:G.boss&&Math.round(G.boss.y),px:Math.round(P.x),py:Math.round(P.y),state:G.state}}""", bk)
            await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, f'sea_boss_{bk}.png'))
        R['mini'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=10;G.startGame('wolf');const P=G.P;__lv(15);for(let i=0;i<60;i++){P.inv=99;G.tick(1/30);if(G.state!=='play')__s();}
          const m=G.enemies.find(e=>e.kind==='mini');return {fset:P.fset,bk:m&&m.bk}}""")
        R['low'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=3;G.startGame('wolf');const P=G.P;for(let i=0;i<300;i++){P.inv=99;G.tick(1/30);}
          return {tier:P.tier,fset:P.fset,mob:G.enemies.find(e=>e.kind==='mob')?.spec.name}}""")
        R['chal'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=7;G.SAVE.ch.open=true;G.setChMode(true);G.startGame('wolf');const P=G.P;for(let i=0;i<300;i++){P.inv=99;G.tick(1/30);}
          const r={fset:P.fset,mob:G.enemies.find(e=>e.kind==='mob')?.spec.name};G.setChMode(false);return r}""")
        print(json.dumps(R, ensure_ascii=False, indent=0)); print('errs', pg.errs)
        await b.close()
asyncio.run(main())
