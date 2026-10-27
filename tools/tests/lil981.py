"""릴세르카 최신 수정(v9.64 왈츠 쿨 26 · v9.66 거울 체력 15% · 깨지면 0.2초 경직)이 실제 판에서 적용되는지"""
import asyncio, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        await pg.wait_for_function("__G.imgReady(['arena','imap','lil','lfx'])", timeout=120000, polling=1000)
        await pg.evaluate("()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer')}")
        await pg.wait_for_function("__G.state==='play'", timeout=60000)
        r = await pg.evaluate("""()=>{const G=__G,o={};const P=G.P;o.tier=P.tier;o.bossK=P.bossK;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<60;i++){G.tick(1/30);if(G.state!=='play')__s()}const e=G.boss;o.bk=e&&e.bk;const AI=G.ls;o.st=G.state;o.fset=P.fset;if(!AI)return o;o.LS={wCd:G.LS.wCd,mrHp:G.LS.mrHp,mrStun:G.LS.mrStun};
          for(const k in AI.cd)AI.cd[k]=99;AI.cd.mirror=0;AI.cyc=['mirror'];AI.ci=0;e.st='glide';e.stT=0;
          for(let i=0;i<120;i++){P.hp=P.max;P.inv=1;G.tick(1/30);if(G.state!=='play')__s()}
          o.mirs=G.LSW.mir.map(m=>[Math.round(m.hp),Math.round(m.max||0)]);o.bossMax=Math.round(e.max);
          const m=G.LSW.mir[0];if(m){const h0=m.hp;m.hp=1;G.hurtEnemy&&0;}
          return o}""")
        print(r, 'ERRS', errs[:3]); await b.close()
asyncio.run(main())
