"""v10.46 각성한 원숭이 마왕 — 패턴별 화면 (build/amk/s_*.png)"""
import asyncio, sys
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
        print(await pg.evaluate(START, 'wolf'))
        await pg.evaluate("()=>{for(let i=0;i<90;i++){__G.P.hp=__G.P.max;__G.P.inv=1;__G.tick(1/30)}__G.AMW.tip={sh:1,wh:1,pi:1,ph:1}}")
        K = await pg.evaluate("()=>__G.amkK()")
        for name, pat, ph, ox, oy, sec in [('idle1', 'idle', 1, 300, 80, 0.3), ('claw', 'claw', 1, 180, 40, 0.9 * K), ('claw2', 'claw', 1, 180, 40, 0.97 * K), ('shatter_w', 'shatter', 1, 330, 120, 0.5 * K), ('shatter_f', 'shatter', 1, 330, 120, 0.85 * K + 0.22), ('shatter_c', 'shatter', 1, 330, 120, 0.85 * K + 1.2),
                                           ('whirl_w', 'whirl', 1, 320, 60, 0.6 * K), ('whirl_1', 'whirl', 1, 320, 60, 1.0 * K + 0.12), ('whirl_2', 'whirl', 1, 320, 60, 1.5 * K + 0.1), ('whirl_3', 'whirl', 1, 320, 60, 2.0 * K + 0.1),
                                           ('pillar', 'pillar', 1, 300, 60, 0.35 + 1.25 * K), ('leap', 'leap', 1, 420, 0, 0.8 * K), ('land', 'leap', 1, 420, 0, 1.0 * K + 0.1), ('rage', 'rage', 1, 300, 80, 1.6), ('idle2', 'idle', 2, 300, 80, 0.4), ('claw_p2', 'claw', 2, 250, 0, 0.9 * K),
                                           ('ph_fade', 'phantom', 2, 300, 80, 0.4), ('ph_aim', 'phantom', 2, 300, 80, 0.55 + 0.8 * K), ('ph_dash', 'phantom', 2, 300, 80, 0.56 + 1.1 * K + 0.14 * K), ('ph_boomw', 'phantom', 2, 300, 80, 0.56 + 1.38 * K + 0.6 * K), ('ph_boom', 'phantom', 2, 300, 80, 0.56 + 2.38 * K + 0.15)]:
            st = await pg.evaluate(SET, [pat, ph, ox, oy, sec]); await pg.wait_for_timeout(120); await pg.screenshot(path=f'../../build/amk/s_{name}.png')
        await pg.evaluate("()=>{const G=__G,e=G.boss;e.ph=2;e.hide=false;e.invul=false;G.amk.chase(99);G.hurtEnemy(e,e.hp+10,0,0,0);for(let i=0;i<50;i++)G.tick(1/60)}")
        await pg.wait_for_timeout(150); await pg.screenshot(path='../../build/amk/s_death.png'); print(await pg.evaluate("()=>[__G.state, document.getElementById('overTitle').textContent, __G.SAVE.dex.kills.boss28]"))
        await pg.evaluate("()=>{for(let i=0;i<400;i++)__G.tick(1/30)}"); await pg.wait_for_timeout(300); await pg.screenshot(path='../../build/amk/s_win.png')
        print(await pg.evaluate("()=>[__G.state, document.getElementById('overTitle').textContent, document.getElementById('overStats').textContent.slice(-60), __G.P.earned]"), 'errs', pg.errs)
        await b.close()
asyncio.run(main())
