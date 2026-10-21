"""v6.22 코끼리 돌진: 이동 방향(상하·대각)·서 있을 때 바라보는 방향·벽 멈춤 확인"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
JS = """([keys, face, ex, ey])=>{const G=__G,P=G.P;G.enemies.length=0;P.inv=99;P.skT=0;P.x=0;P.y=0;P.face=face;
 for(const k of ['KeyW','KeyA','KeyS','KeyD'])G.keys.delete(k); for(const k of keys)G.keys.add(k);
 for(let i=0;i<3;i++)G.tick(1/30);
 const e={kind:'mob',x:ex,y:ey,kx:0,ky:0,sp:0,spec:null,sc:1,r:20,hp:1e6,max:1e6,dmg:0,exp:0,elite:false,flash:0,t:0,orbCd:0,slowT:0};
 G.enemies.push(e); const x0=e.x,y0=e.y; G.cast(); let mx=0,my=0,maxd=0,eh=false,dd=null;
 for(let i=0;i<110;i++){ for(const k of ['KeyW','KeyA','KeyS','KeyD'])G.keys.delete(k); if(i<8)for(const k of keys)G.keys.add(k); P.x=0;P.y=0; e.x=ex;e.y=ey; G.tick(1/30); if(G.eleQ){ dd=[+G.eleQ.ux.toFixed(2),+G.eleQ.uy.toFixed(2)]; if(G.eleQ.hit.has(e))eh=true; } }
 return {hit:eh?1:0, dir:dd};}"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await newpage(b)
        await pg.evaluate("()=>{const G=__G;G.SAVE.chars.octo=true;G.startGame('octo');window.__lv(12);}")
        cases = [('위로(W)', ['KeyW'], 1, 0, -400, 1), ('아래로(S)', ['KeyS'], 1, 0, 400, 1), ('오른쪽 위(W+D)', ['KeyW', 'KeyD'], 1, 283, -283, 1),
                 ('왼쪽(A)', ['KeyA'], 1, -400, 0, 1), ('서 있기·왼쪽 보기', [], -1, -400, 0, 1), ('서 있기·오른쪽 보기', [], 1, 400, 0, 1),
                 ('W 누르는데 적은 오른쪽(빗나가야 함)', ['KeyW'], 1, 400, 0, 0)]
        for nm, keys, face, ex, ey, want in cases:
            await pg.evaluate("()=>{const G=__G,P=G.P;P.skT=0;G.state==='play'||0}")
            r = await pg.evaluate(JS, [keys, face, ex, ey]); ok = (r['hit'] > 0) == bool(want)
            print('PASS' if ok else 'FAIL', nm, r)
        print(pg.errs[:3]); await b.close()
asyncio.run(main())
