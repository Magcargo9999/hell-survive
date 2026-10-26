"""v9.53 팔열지옥 보스맵: 층 26~29 보스방에서 마왕별 입장·스크린샷·오류
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/fmap953.py [폴더]"""
import asyncio, sys, os
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/fmap'; os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.fmap&&__G.IMG.imap', timeout=90000)
        for bk, tier in (('cvt', 25), ('snk', 27), ('bear', 25), ('rud', 28), ('lil', 28)):
            r = await pg.evaluate("""([bk,t])=>{const G=__G;G.SAVE.diff.max=29;G.SAVE.diff.sel=t;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;P.tier=t;P.bossK=bk;P.fset='fire';__lv(28);G.raiseCastle();G.enterArena();
              for(let i=0;i<90;i++)G.tick(1/30);const M=G.IMAP;return {bk:G.boss&&G.boss.bk,fire:!!G.arena.fire,img:M.img,start:[P.x,P.y],inStart:G.inPoly(P.x,P.y),inC:G.inPoly(M.cx,M.cy),boss:[G.boss.x,G.boss.y],inBoss:G.inPoly(G.boss.x,G.boss.y)}}""", [bk, tier])
            print(bk, r)
            await pg.evaluate("()=>{const G=__G,P=G.P;P.x=G.IMAP.cx-300;P.y=G.IMAP.cy+200;P.hp=P.max;P.inv=99;for(let i=0;i<120;i++)G.tick(1/30);}")
            await pg.screenshot(path=f'{OUT}/f_{bk}.png')
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
