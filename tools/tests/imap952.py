"""v9.52 빙결 투기장 새 그림: 광장 가장자리·통로에서 내 위치가 그림의 얼음 바닥 끝과 맞는지 스크린샷 + 오류
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/imap952.py [폴더]"""
import asyncio, sys
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/imap'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.imap', timeout=90000)
        r = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=21;G.SAVE.diff.sel=20;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);const M=G.IMAP;return {bk:G.boss&&G.boss.bk,start:[P.x,P.y],inStart:G.inPoly(P.x,P.y),inC:G.inPoly(M.cx,M.cy),c:[M.cx,M.cy],X:[M.X0,M.X1,M.Y0,M.Y1]}}""")
        print(r)
        M = r['X']; cx, cy = r['c']
        pts = {'top': (cx, M[2] + 14), 'left': (M[0] + 14, cy), 'right': (M[1] - 14, cy), 'bot': (cx - 100, M[3] - 14), 'tl': (M[0] + 250, M[2] + 250), 'br': (M[1] - 250, M[3] - 250), 'stairs': (cx, 2500), 'start': (cx, 2700)}
        for n, (x, y) in pts.items():
            await pg.evaluate("([x,y])=>{const G=__G,P=G.P;P.x=x;P.y=y;P.hp=P.max;P.inv=99;G.boss.x=G.IMAP.bx;G.boss.y=G.IMAP.by;G.boss.st='chase';G.boss.stT=99;for(const k in G.pb.cd)G.pb.cd[k]=99;G.cam&&(G.cam.x=x);for(let i=0;i<40;i++){P.x=x;P.y=y;G.tick(1/30);}}", [x, y])
            await pg.screenshot(path=f'{OUT}/imap_{n}.png')
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
