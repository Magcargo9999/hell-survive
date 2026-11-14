"""v10.51 각성한 원숭이 마왕 — 무한 난타 화면 + 걷기(패턴 사이 걷는 거리) 측정"""
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
from amk1046 import START
SET = """(arg)=>{const [pat,ph,ox,oy,sec]=arg;const G=__G,P=G.P,e=G.boss,A=G.amk,W=G.AMW,M=G.IMAP;const cx=(M.X0+M.X1)/2,cy=(M.Y0+M.Y1)/2;
 e.tele=[];A.q=[];W.waves=[];W.clones=[];e.hide=false;e.jh=0;A.lp=null;e.ph=ph;e.x=cx;e.y=cy;e.invul=false;P.x=cx+ox;P.y=cy+oy;P.max=1e6;P.hp=1e6;
 A.chase(99);for(const k in A.cd)A.cd[k]=99;A.k=G.amkK();if(pat==='idle'){}else if(pat==='claw')A.clawStart();else if(pat==='rage'){e.ph=1;A.rageStart()}else A[pat+'Start']();
 for(let i=0;i<sec*60;i++){P.inv=1;G.tick(1/60)} return e.st}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.evaluate(START, 'wolf')
        await pg.evaluate("()=>{for(let i=0;i<90;i++){__G.P.hp=__G.P.max;__G.P.inv=1;__G.tick(1/30)}__G.AMW.tip={sh:1,wh:1,pi:1,ph:1,ba:1}}")
        K = await pg.evaluate("()=>__G.amkK()")
        for name, sec in [('ba_wind', 0.5 * K), ('ba_1', 0.9 * K + 0.4 * K), ('ba_5', 0.9 * K + 2.8 * K)]:
            st = await pg.evaluate(SET, ['barrage', 1, 200, 40, sec]); await pg.wait_for_timeout(150); await pg.screenshot(path=f'build/amk/s_{name}.png'); print(name, st)
        # 걷기: 플레이어가 맵을 크게 돌 때 20초 동안 마왕이 걸은 거리 · 걷고 있던 시간 비율
        print(await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,A=G.amk,M=G.IMAP;const cx=(M.X0+M.X1)/2,cy=(M.Y0+M.Y1)/2;e.tele=[];A.q=[];e.ph=1;e.hp=e.max*0.9;e.x=cx;e.y=cy;A.chase(1);
          let dist=0,mv=0,n=0,px=e.x,py=e.y;for(let i=0;i<1200;i++){const a=i/1200*6.283*2;P.x=cx+Math.cos(a)*420;P.y=cy+Math.sin(a)*320;P.inv=1;P.hp=P.max;G.tick(1/60);dist+=Math.hypot(e.x-px,e.y-py);px=e.x;py=e.y;if(e.moving)mv++;n++;}
          return {dist:Math.round(dist),walkPct:Math.round(mv/n*100)}}"""), 'errs', pg.errs)
        await b.close()
asyncio.run(main())
