"""v9.51 백곰 마왕 도트 — 대기·이동·강공격·포효·돌진·갑주·사망 스크린샷 + 콘솔 오류
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/bear951.py [폴더]"""
import asyncio, sys
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.bear', timeout=90000)
        r = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=21;G.SAVE.diff.sel=20;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<60;i++)G.tick(1/30);const e=G.boss;return {bk:e&&e.bk,img:!!G.IMG.bear}}""")
        print(r)
        async def shot(name, js):
            await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss;P.hp=P.max;P.inv=99;P.x=G.IMAP.cx;P.y=G.IMAP.cy-200;e.x=P.x+20;e.y=P.y+330;e.hp=e.max;e.st='chase';e.stT=99;for(const k in G.pb.cd)G.pb.cd[k]=99;"+js+"G.render()}")
            await pg.screenshot(path=f'{OUT}/bear_{name}.png')
        await shot('idle0', "e.an='idle';")
        await shot('idle', "e.an='idle';")
        await shot('walk', "e.an='walk';e.st='chase';e.stT=5;")
        await shot('cast', "e.an='cast';e.anT=0.3;e.st='wall';e.stT=5;")
        await shot('roar', "e.an='roar';e.anT=0;e.st='intro';e.stT=5;")
        await shot('ball', "e.an='ball';e.st='pbDash';e.stT=5;")
        await shot('ph2', "e.ph2=true;e.an='idle';e.st='chase';e.stT=5;")
        await shot('trans', "e.ph2=true;e.an='roar';e.anT=1.5;e.st='roar';e.stT=5;")
        await pg.evaluate("()=>{const G=__G,e=G.boss;G.P.x=G.IMAP.cx;G.P.y=G.IMAP.cy-200;e.x=G.P.x+20;e.y=G.P.y+330;G.PBW.death={x:e.x,y:e.y,t:1.6,face:-1};G.render()}")
        await pg.screenshot(path=f'{OUT}/bear_death.png')
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
