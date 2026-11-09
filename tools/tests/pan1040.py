"""v10.40 10지옥 판데모니움 필드 기믹: 흑백 반전(30초 · 페이즈마다 타오르는 칸만 피해) · 무너지는 바닥(1초 서 있으면 금 → 1.5초 뒤 심연 · 피해 · 못 들어감)
사용: PYTHONPATH=tools python3 tools/tests/pan1040.py   (스크린샷 build/pan40_*.png)"""
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
        await pg.wait_for_function("__G.imgReady(['pfloor','pprops','tmob'])", timeout=150000, polling=1000)
        await ev(pg, """()=>{const G=__G;G.SAVE.diff.max=39;G.SAVE.diff.sel=36;G.SAVE.shards=1e7;G.startGame('wolf')}""")
        for i in range(40):
            if await ev(pg, "()=>__G.state") == 'play': break
            await asyncio.sleep(0.5)
        S = """const G=__G,P=G.P,W=G.PANW,A=G.PAN;const tk=n=>{for(let i=0;i<n;i++){G.tick(1/30);while(__s());}};
          const fix=()=>{P.max=1e5;P.inv=0;P.shield=0;P.taken=1;G.enemies.length=0};
          const find=f=>{for(let r=3;r<60;r++)for(let ty=-r;ty<=r;ty++)for(let tx=-r;tx<=r;tx++)if(f(tx,ty))return [tx,ty];return null};"""
        R = {}
        R['setup'] = await ev(pg, "()=>{" + S + """__lv(25);P.fset='pan';G.GROUND.clear();G.panClear();tk(2);return {ph:W.ph,on:W.on,lava:!!find((x,y)=>G.isLava(x,y)),vent:!!find((x,y)=>G.isPanVent(x,y)),overlap:!!find((x,y)=>G.isLava(x,y)&&G.isPanVent(x,y))}}""")
        R['phase'] = await ev(pg, "()=>{" + S + """const T=G.TILE;const L=find((x,y)=>G.isLava(x,y)),V=find((x,y)=>G.isPanVent(x,y));const o={};
          const dmg=(c)=>{fix();P.hp=P.max;W.cells.clear();let h=P.hp;for(let i=0;i<30;i++){P.x=c[0]*T+T/2;P.y=c[1]*T+T/2;W.sk='';W.st=0;tk(1);P.inv=0}return Math.round(h-P.hp)};
          W.ph='w';W.t=0;o.wLava=dmg(L);W.t=0;o.wVent=dmg(V);W.ph='b';W.t=0;o.bLava=dmg(L);W.t=0;o.bVent=dmg(V);
          W.ph='w';W.t=A.cyc-0.05;tk(3);o.flip=W.ph;return o}""")
        await ev(pg, "()=>{" + S + """const T=G.TILE;const V=find((x,y)=>G.isPanVent(x,y));W.ph='w';W.t=A.cyc-2;P.x=V[0]*T+T*3;P.y=V[1]*T;P.inv=99;tk(3)}""")
        await pg.screenshot(path=B + 'pan40_warn.png')
        R['collapse'] = await ev(pg, "()=>{" + S + """const T=G.TILE;const C=find((x,y)=>!G.isLava(x,y)&&!G.isPanVent(x,y)&&!G.isLava(x+1,y)&&!G.isPanVent(x+1,y));const o={};
          fix();P.hp=P.max;W.cells.clear();W.ph='w';W.t=0;P.x=C[0]*T+T/2;P.y=C[1]*T+T/2;const h=P.hp;
          tk(Math.round(30*0.9));o.crackAt09=W.cells.size;tk(6);o.crack=[...W.cells.values()].map(c=>c.s).join();
          tk(Math.round(30*1.6));o.pit=[...W.cells.values()].map(c=>c.s).join();o.pitDm=Math.round(h-P.hp);
          const tx=Math.floor(P.x/T),ty=Math.floor(P.y/T);o.pushedOut=!(tx===C[0]&&ty===C[1]);
          // 들어가려 해도 못 들어감
          let inside=0;for(let i=0;i<20;i++){P.x=C[0]*T+T/2+ (i%2?20:-20);P.y=C[1]*T+T/2;tk(1);if(Math.floor(P.x/T)===C[0]&&Math.floor(P.y/T)===C[1])inside++}o.inside=inside;
          tk(30*5);o.after=W.cells.size;
          // 걸어 다니면 안 갈라진다
          W.cells.clear();for(let i=0;i<30*6;i++){P.x+=150/30;tk(1)}o.walkCells=W.cells.size;return o}""")
        await ev(pg, "()=>{" + S + """const T=G.TILE;W.cells.clear();W.ph='b';W.t=5;P.inv=99;for(let k=0;k<4;k++){W.cells.set((Math.floor(P.x/T)+2+k)+','+Math.floor(P.y/T),{tx:Math.floor(P.x/T)+2+k,ty:Math.floor(P.y/T),s:k<2?'crack':'pit',t:k<2?1:1})}tk(2)}""")
        await pg.screenshot(path=B + 'pan40_dark.png')
        await ev(pg, "()=>{" + S + """P.inv=99;P.bossK='ttn';G.raiseCastle();G.enterArena();}""")
        await asyncio.sleep(2.5)
        R['arena'] = await ev(pg, "()=>{" + S + """P.inv=99;tk(40);return {arena:!!G.arena,on:W.on,cells:W.cells.size}}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
