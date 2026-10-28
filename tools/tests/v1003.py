"""v10.03: 임프 처치 조각이 결과창에 표시 · 호랑이 카메라 안 딸려감 · 리듬 돌진 항상 직선(나를 겨눔)"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','fmap'])", timeout=120000, polling=1000)
        await pg.evaluate("()=>{window.__tk=()=>{const G=__G;if(G.P)G.P.heat=0;G.tick(1/30)};const G=__G;G.SAVE.diff.max=29;G.SAVE.diff.sel=29;G.SAVE.shards=1e7;G.startGame('archer')}")
        await pg.wait_for_function("__G.state==='play'&&__G.P", timeout=60000)
        R = {}
        R['tg'] = await ev(pg, """()=>{const G=__G,P=G.P;__lv(30);P.max=1e7;P.hp=P.max;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)__tk();const e=G.boss,AI=G.tg;
          for(const k in AI.cd)AI.cd[k]=99;e.hp=e.max*0.39;for(let i=0;i<120;i++){P.inv=1;P.hp=P.max;__tk()}
          const o={ph2:e.ph2,cam:G.tgCam()};const ty={};for(let i=0;i<20;i++){AI.rwStart();ty[G.TGW.rw.ty]=1;G.TGW.rw=null;AI.chase(1)}o.types=Object.keys(ty);return o}""")
        print(R); print('ERR', errs[:5]); await b.close()
asyncio.run(main())
