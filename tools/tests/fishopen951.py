"""v9.51 마계 물고기 해금: 지하 20층 마왕 처치(또는 예전 20층 클리어 기록)로 열림 · 상점에서는 안 팔림"""
import asyncio
from h301 import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE,o={};o.cond=G.CHARS.fish.cond;o.price=G.CHARS.fish.price;
          S.chars.fish=false;S.rush.open=false;S.fw.snap=null;G.buildCards();o.locked=!S.chars.fish;
          S.rush.open=true;G.buildCards();o.oldRecord=!!S.chars.fish;
          S.chars.fish=false;S.rush.open=false;S.fw.snap=null;S.diff.max=19;S.diff.sel=19;S.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();for(let i=0;i<30;i++)G.tick(1/30);P.tier=19;try{G.bossDefeated(G.boss)}catch(e){o.err=String(e)}
          o.afterKill=!!S.chars.fish;return o}""")
        print(r, 'OK' if r['locked'] and r['oldRecord'] and r['afterKill'] and r['price']==0 else 'FAIL')
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
