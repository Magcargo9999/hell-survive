"""v10.39 10지옥 판데모니움 맵 (지하 46~50층, 잠김): floorSet · 필드 바닥·소품·위험 지대 · 보스맵 IMAP_PAN(타일 조합 그림 ×2) · 마왕 패턴이 이 맵에서 도는지
사용: PYTHONPATH=tools python3 tools/tests/pan1039.py   (스크린샷 build/pan_*.png)"""
import asyncio, sys, os, json
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
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function("__G.imgReady(['arena','pfloor','pprops','pmap','tmob','ttn','hnt'])", timeout=150000, polling=1000)
        R = {}
        R['set'] = await ev(pg, """()=>{const G=__G;return {f:[39,40,44,45,49].map(t=>G.floorSet(t)),open:G.OPEN_TIER,top:G.TOP_TIER,props:G.PPROP_RECTS.length}}""")
        await ev(pg, """()=>{const G=__G;G.SAVE.diff.max=39;G.SAVE.diff.sel=36;G.SAVE.shards=1e7;G.startGame('wolf')}""")
        for i in range(40):
            if await ev(pg, "()=>__G.state") == 'play': break
            await asyncio.sleep(0.5)
        R['field'] = await ev(pg, """()=>{const G=__G,P=G.P;__lv(25);P.inv=99;P.fset='pan';G.GROUND.clear();P.x=600;P.y=400;
          let lava=0,tiles={};for(let ty=-40;ty<40;ty++)for(let tx=-40;tx<40;tx++){if(G.isLava(tx,ty))lava++;}
          for(let i=0;i<30*3;i++){P.inv=99;P.hp=P.max;G.tick(1/30);while(__s());}return {fset:P.fset,lava,mobs:G.enemies.filter(e=>!e.boss).length}}""")
        await pg.screenshot(path=B + 'pan_field.png')
        await ev(pg, """()=>{const G=__G,P=G.P;P.x=2600;P.y=-1800;G.GROUND.clear();for(let i=0;i<10;i++){P.inv=99;G.tick(1/30);while(__s());}}""")
        await pg.screenshot(path=B + 'pan_field2.png')
        await ev(pg, """()=>{const G=__G,P=G.P;P.fset='tar';G.GROUND.clear();P.x=-2600;P.y=1800;for(let i=0;i<10;i++){P.inv=99;G.tick(1/30);while(__s());}}""")
        await pg.screenshot(path=B + 'pan_tarprops.png')   # 8지옥 소품이 버섯 그림이 아니라 타르타로스 소품인지
        await ev(pg, """()=>{const G=__G,P=G.P;P.fset='pan';G.GROUND.clear();}""")
        R['arena'] = await ev(pg, """()=>{const G=__G,P=G.P;P.bossK='ttn';G.raiseCastle();G.enterArena();return 1}""")
        await asyncio.sleep(2.5)
        R['map'] = await ev(pg, """()=>{const G=__G,P=G.P,M=G.IMAP;for(let i=0;i<20;i++){P.inv=99;G.tick(1/30);while(__s());}const e=G.boss;
          return {pan:!!(G.arena&&G.arena.pan),img:M.img,s:M.s,center:G.inPoly(M.cx,M.cy),start:G.inPoly(M.start[0],M.start[1]),boss:e&&G.inPoly(e.x,e.y),bk:e&&e.bk,
            out:[G.inPoly(M.X0-40,M.cy),G.inPoly(M.cx,M.Y0-60),G.inPoly(M.X1+40,M.cy)]}}""")
        shots = [('pan_boss_c', 'M.cx', 'M.cy'), ('pan_boss_top', 'M.cx', 'M.Y0+120'), ('pan_boss_bot', 'M.cx', 'M.Y1+260'), ('pan_boss_left', 'M.X0+220', 'M.Y1-240')]
        for name, x, y in shots:
            await ev(pg, f"""()=>{{const G=__G,P=G.P,M=G.IMAP,e=G.boss;P.x={x};P.y={y};if(e){{e.x=M.cx+300;e.y=M.cy-200;e.invul=true}}for(let i=0;i<8;i++){{P.inv=99;P.hp=P.max;G.tick(1/30);while(__s());}}}}""")
            await pg.screenshot(path=B + name + '.png')
        R['fight'] = await ev(pg, """()=>{const G=__G,P=G.P,M=G.IMAP,e=G.boss;e.invul=false;let out=0,sts={};for(let i=0;i<30*40;i++){P.inv=99;P.hp=P.max;const a=i/30;P.x=M.cx+Math.cos(a*0.6)*600;P.y=M.cy+Math.sin(a*0.6)*500;G.tick(1/30);while(__s());if(!G.boss)break;if(!G.inPoly(G.boss.x,G.boss.y))out++;sts[G.boss.st]=1}
          return {out,sts:Object.keys(sts).join(',')}}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
