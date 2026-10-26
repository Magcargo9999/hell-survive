"""v9.64 릴세르카 스포트라이트·릴세르카 원이 광장 밖으로 안 나가는지 (가장자리 여러 위치)"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.ifloor',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);const e=G.boss,AI=G.ls,M=G.IMAP;let bad=0,n=0,outS=0,outB=0;
          for(let a=0;a<12;a++){for(const r of [0.5,0.8,0.95]){
            P.x=M.cx+Math.cos(a/12*6.283)*(M.X1-M.X0)*0.5*r;P.y=M.cy+Math.sin(a/12*6.283)*(M.Y1-M.Y0)*0.5*r;if(!G.inPoly(P.x,P.y))continue;
            e.x=M.cx;e.y=M.cy;G.LSW.spot=null;AI.waltzStart();n++;
            for(let i=0;i<30*8;i++){P.x=G.LSW.spot?G.LSW.spot.x:P.x;P.hp=P.max;P.inv=1;P.stunT=0;G.tick(1/30);const S=G.LSW.spot;if(!S)break;if(!G.inPoly(S.x,S.y))outS++;if(!G.inPoly(e.x,e.y))outB++}}}
          return {n,outS,outB}}""")
        print(json.dumps(R),'errs',errs); await b.close()
asyncio.run(main())
