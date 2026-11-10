"""v10.41 타르타로스 푸른 보스맵 — 티탄은 보라 tmap, 그 외 마왕(암전의 사냥꾼)은 푸른 tmap2 · 지오메트리(광장 안 · 출구) · 스크린샷
사용: PYTHONPATH=tools GAME_URL=... python3 tools/tests/tar2_1041.py   (스크린샷 build/tar2_*.png)"""
import asyncio, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','tmap','tmap2','hnt','ttn','tfloor','tprops','tmob'])", timeout=120000, polling=1000)
        await ev(pg, "()=>{const G=__G;G.SAVE.diff.max=39;G.SAVE.diff.sel=39;G.SAVE.shards=1e7;G.startGame('archer')}")
        for i in range(40):
            if await ev(pg, "()=>__G.state") == 'play': break
            await asyncio.sleep(0.5)
        for bk in ('hnt', 'ttn'):
            await ev(pg, f"()=>{{const G=__G,P=G.P;__lv(30);P.inv=1;P.max=1e7;P.hp=P.max;P.bossK='{bk}';G.raiseCastle();G.enterArena();return 1}}")
            await asyncio.sleep(2.5)
            r = await ev(pg, """()=>{const G=__G,P=G.P,o={};for(let i=0;i<10;i++)G.tick(1/30);o.img=G.IMAP.img;o.wh=[G.IMAP.w,G.IMAP.h];o.inPoly=G.inPoly(G.IMAP.cx,G.IMAP.cy);o.start=G.inPoly(G.IMAP.start[0],G.IMAP.start[1])||G.IMAP.start[1]>G.IMAP.Y1;o.boss=G.boss&&G.boss.bk;o.pl=[Math.round(P.x),Math.round(P.y)];return o}""")
            print(bk, r)
            await pg.screenshot(path=B + f'tar2_{bk}.png')
            await ev(pg, "()=>{const G=__G;G.reset&&G.reset()}")
        print('errs', errs[:3])
        await b.close()
asyncio.run(main())
