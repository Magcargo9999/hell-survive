"""v8.85 어인왕전 도중 죽고 새 판 시작 → 산소 간헐천 등이 남지 않는다 · 보스전이 아니면 그리지 않는다"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.kng&&__G.IMG.smap',timeout=90000)
        r=await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.max=19;G.SAVE.diff.sel=19;G.SAVE.shards=1e7;G.startGame('archer');__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<60;i++)G.tick(1/30);o.inBoss=[G.KGW.geysers.length,G.KGW.mirrors.length];
          G.P.hp=0;G.P.inv=0;G.P.shield=0;G.startGame('archer');for(let i=0;i<60;i++)G.tick(1/30);
          o.fresh=[G.KGW.geysers.length,G.KGW.mirrors.length,G.KGW.bolts.length,!!G.KGW.tether,!!G.KGW.ring,G.boss?G.boss.bk:null];return o}""")
        print(json.dumps(r)); print('errs',pg.errs[:5]); await b.close()
asyncio.run(main())
