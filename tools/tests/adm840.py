"""v8.40 썩어버린 해군 제독: 등장 확률 · 닻 견인 · 함포 · 발악 · 규칙 9(포탄 원 사이 안전 비율) · 스크린샷 · 오류"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.smap',timeout=60000)
        print('prob', await pg.evaluate("""()=>{const G=__G,R={};for(const t of [9,10,11,12,19]){const c={};for(let i=0;i<7000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1}R[t]=Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/70)]))}return JSON.stringify(R)}"""))
        await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=19;G.SAVE.shards=99999;G.SAVE.diff.sel=10;G.SAVE.chars.gun=true;G.startGame('wolf');G.P.bossK='adm';G.raiseCastle();G.enterArena();}""")
        await pg.wait_for_timeout(2000)
        print('boss', await pg.evaluate("[__G.boss&&__G.boss.bk, __G.arena&&__G.arena.sea, Math.round(__G.boss.max)]"))
        await pg.evaluate("__run(90)")  # intro
        await pg.screenshot(path=B+'adm_idle.png')
        # 근접 베기
        r=await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;P.x=e.x+120;P.y=e.y+20;e.slCd=0;e.st='chase';e.stT=0;G.tick(1/30);return e.st}""")
        await pg.wait_for_timeout(100); await pg.screenshot(path=B+'adm_slash.png'); print('slash state',r)
        # 닻 견인
        r=await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;G.SAVE.set.speed=0;P.x=e.x;P.y=e.y+420;P.inv=0;P.shield=0;P.hp=P.max;P.stunImm=0;e.tele=[];G.admAnchorStart(e);
          const out=[];for(let i=0;i<60;i++){P.hp=P.max;G.tick(1/30);if(i==26)out.push('shot');out.push([e.st,!!G.admAnc,!!G.admPull,Math.round(Math.hypot(P.x-e.x,P.y-e.y)),+P.stunT.toFixed(2)])}
          return JSON.stringify(out.filter((_,i)=>i%4==0))}""")
        print('anchor', r)
        await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;P.x=e.x+60;P.y=e.y+460;e.tele=[];e.st='chase';G.admAnchorStart(e);for(let i=0;i<30;i++){P.inv=99;P.hp=P.max;G.tick(1/30)}}""")
        await pg.screenshot(path=B+'adm_anchor.png')
        # 함포 소환 + 측면 포격 + 휘두르기
        r=await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;e.tele=[];G.admCannonCall(e);G.admBroad(e);for(let i=0;i<50;i++){P.inv=99;P.hp=P.max;G.tick(1/30)}return [G.admNC(),G.admBalls.length]}""")
        print('cannon/broad', r); await pg.screenshot(path=B+'adm_cannon.png')
        # 발악: 규칙 9 — 내 주변 250px 안에서 포탄 원 밖인 바닥 비율 (최저)
        r=await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;e.hp=e.max*0.29;let minS=1,maxN=0,maxB=0;
          for(let i=0;i<30*14;i++){P.inv=99;P.hp=P.max;if(i%20==0){P.x+=(Math.random()-0.5)*160;P.y+=(Math.random()-0.5)*120}G.tick(1/30);
            const L=G.admBalls.filter(s=>s.t>=0);maxB=Math.max(maxB,L.length);maxN=Math.max(maxN,G.admNC());
            let n=0,ok=0;for(let a=0;a<24;a++)for(let r=40;r<=250;r+=35){const x=P.x+Math.cos(a/24*6.283)*r,y=P.y+Math.sin(a/24*6.283)*r;if(!G.inPoly(x,y))continue;n++;if(!L.some(s=>{const dx=(x-s.x1)/(s.r+10),dy=(y-s.y1)*1.5/(s.r+10);return dx*dx+dy*dy<1}))ok++}
            if(n)minS=Math.min(minS,ok/n)}
          return [e.fz,maxN,maxB,+minS.toFixed(2)]}""")
        print('frenzy [fz, 최대 함포, 동시 포탄, 최저 안전 비율]', r)
        await pg.screenshot(path=B+'adm_frenzy.png')
        # 처치 → 정리 · 도감
        r=await pg.evaluate("""()=>{const G=__G,e=G.boss;G.hurtEnemy(e,1e9,0,0,0);for(let i=0;i<10;i++)G.tick(1/30);return [G.boss,G.admNC(),G.SAVE.dex.kills.boss9]}""")
        print('dead', r)
        await pg.evaluate("()=>{document.getElementById('overBox')&&0}")
        print('errs', pg.errs[:6]); await b.close()
asyncio.run(main())
