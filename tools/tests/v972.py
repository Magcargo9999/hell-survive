"""v9.72 — 불구렁이 똬리 몸통 무피해(머리만) · 26~29층 보스방 열기(휴식존 4곳) · 호랑이 불의 십자가 계속 회전 · 수플렉스 안전지대 규칙 9 · 호랑이 카메라 복귀 · 도감 스킬 보기 · 총령 hq 확대 없음
사용: PYTHONPATH=tools python3 tools/tests/v972.py   (스크린샷 build/v972_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:220]
SETUP = "window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};"
async def arena(b, tier, bk, char='archer'):
    pg = await h301.newpage(b, 1280, 720); pg.errs2 = []
    pg.on('pageerror', lambda e: pg.errs2.append(str(e))); pg.on('console', lambda m: pg.errs2.append(m.text) if m.type == 'error' else None)
    await pg.wait_for_function("__G.IMG&&__G.IMG.boss", timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','fmap'])", timeout=120000, polling=1000)
    await pg.evaluate("()=>{" + SETUP + "}")
    await pg.evaluate("""([tier,bk,ch])=>{const G=__G;G.SAVE.diff.max=34;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame(ch);const P=G.P;__lv(28);P.tier=tier;P.fset='fire';P.bossK=bk;G.raiseCastle();G.enterArena();
      for(let i=0;i<40;i++)__tk()}""", [tier, bk, char])
    return pg
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); R = {}
        # 1) 불구렁이 똬리: 몸통은 피해 0, 머리(보스 본체)만 피해
        pg = await arena(b, 27, 'snk')
        R['coil'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn,o={};G.SNW.ring=null;G.SNW.hd=null;e.tele=[];AI.chase(0.5);e.hp=e.max*0.29;
          for(let i=0;i<30*5.5;i++){P.hp=P.max;P.inv=1;P.heat=0;__tk()}const C=G.SNW.coil;o.coil=!!C&&C.closed;o.ph2=e.ph2;o.st=e.st;
          if(!C)return o;const px=G.enemies.filter(q=>q.kind==='snb');o.proxies=px.length;o.proxLive=px.filter(q=>q.x>-9000).length;
          // 몸통(마디)에 직접 피해 → 마왕 체력 변화 없음
          const n=G.SNW.nodes[3];const h0=e.hp;if(px[3])G.hurtEnemy(px[3],1000,0,0,0);o.bodyDmg=Math.round(h0-e.hp);
          // 머리(보스 본체)에는 들어간다
          const h1=e.hp;e.invul=false;G.hurtEnemy(e,1000,0,0,0);o.headDmg=Math.round(h1-e.hp);
          // 몸통을 지나가는 투사체는 안 사라진다(마디가 맞지 않으므로 대상에서 빠짐) — 대리 히트박스가 화면 밖으로 빠졌는지
          o.reach=Math.round(Math.hypot(e.x-P.x,e.y-P.y));return o}""")
        R['coilBanner'] = await ev(pg, "()=>(__G.banner&&__G.banner.txt||'').slice(0,80)")
        # 2) 26~29층 보스방 열기
        R['heat'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};o.on=G.heatOn();o.arena=G.heatArena();o.z=G.arenaRests().map(z=>[Math.round(z.x),Math.round(z.y),G.inPoly(z.x,z.y)]);
          P.heat=0;for(let i=0;i<30*10;i++){P.hp=P.max;P.inv=1;__tk()}o.heat10=Math.round(P.heat);
          const z=G.arenaRests()[0];P.x=z.x;P.y=z.y;for(let i=0;i<30*2;i++){P.hp=P.max;P.inv=1;__tk()}o.inRest=P.inRest;o.heatAfter=Math.round(P.heat);
          P.heat=100;P.hp=P.max;P.inv=1;const h0=P.hp;P.x=G.IMAP.cx;P.y=G.IMAP.cy;let t=0;for(let i=0;i<30*1.1;i++){__tk();t++}o.burn=+(((h0-P.hp)/P.max)*100).toFixed(2);
          o.nearestSeen=!!G.arenaRestNearest(P.x,P.y);return o}""")
        await ev(pg, "()=>{const G=__G,P=G.P;P.heat=60;P.x=G.IMAP.cx;P.y=G.IMAP.cy+120;for(let i=0;i<10;i++){P.inv=1;__tk()}}")
        await pg.screenshot(path=B + 'v972_heat_arena.png')
        R['errs1'] = pg.errs2[:4]; await pg.close()
        # 30층(호랑이) 보스방은 열기 없음
        pg = await arena(b, 29, 'tig')
        R['tigNoHeat'] = await ev(pg, "()=>({on:__G.heatOn(),arena:__G.heatArena(),heat:__G.P.heat})")
        # 3) 호랑이 십자가: 불 뿜는 동안에도 회전
        R['cross'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,C=G.TGW.cr,o={};C.off=0;C.gone=false;C.van=0;C.ph='spin';C.t=0;e.tele=[];if(G.tg)G.tg.chase(99);
          let aSpin=C.a,aBr0=null,aBr1=null,lens0=null,lens1=null,brSteps=0;
          for(let i=0;i<30*9;i++){P.hp=P.max;P.inv=1;P.heat=0;P.x=G.IMAP.cx+900;P.y=G.IMAP.cy+400;G.TGW.crHitT=99;__tk();
            if(C.ph==='breath'&&C.t>=G.TG.crBrWarn){if(aBr0===null){aBr0=C.a;lens0=C.len.map(Math.round)}aBr1=C.a;lens1=C.len.map(Math.round);brSteps++}}
          o.spinStart=+aSpin.toFixed(2);o.breathRotDeg=aBr0===null?null:+((aBr1-aBr0)*57.3).toFixed(1);o.breathSteps=brSteps;o.lens0=lens0;o.lens1=lens1;o.arms=G.tgArms().length;return o}""")
        # 4) 수플렉스 안전지대: 가장 느린 이속 150으로도 닿는다 + 작아짐
        R['sx'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,C=G.TGW.cr,o={};C.off=0;C.gone=false;let far=0,cross=0,n=0,maxEdge=0;
          for(let k=0;k<400;k++){C.a=Math.random()*6.28;P.x=G.IMAP.X0+200+Math.random()*(G.IMAP.X1-G.IMAP.X0-400);P.y=G.IMAP.Y0+150+Math.random()*(G.IMAP.Y1-G.IMAP.Y0-300);if(!G.inPoly(P.x,P.y)||G.tgCrossAt(P.x,P.y,30))continue;e.x=P.x+600;e.y=P.y;
            const S=G.tgSafeSpot(e);n++;const edge=Math.hypot(S.x-P.x,S.y-P.y)-(S.r+18);maxEdge=Math.max(maxEdge,edge);if(edge>150*G.TG.sxWarn-30)far++;if(G.tgCrossAt(S.x,S.y,S.r))cross++}
          o.n=n;o.far=far;o.cross=cross;o.maxEdge=Math.round(maxEdge);o.reach150=Math.round(150*G.TG.sxWarn);o.sxR=G.TG.sxR;o.warn=G.TG.sxWarn;return o}""")
        # 5) 카메라: 2페이즈에서 호랑이 쪽으로 기울고, 리듬 돌진이 아니면 15%, 돌진 때 70%로 → 끝나면 돌아옴
        R['cam'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};e.hp=e.max*0.39;P.x=G.IMAP.cx;P.y=G.IMAP.cy+200;for(let i=0;i<30*4;i++){P.hp=P.max;P.inv=1;__tk()}
          o.ph2=e.ph2;o.cam=G.tgCam();o.w1=+(G.TGW.camW||0).toFixed(2);
          G.TGW.rw={segs:[],i:0};for(let i=0;i<30*3;i++){P.hp=P.max;P.inv=1;G.TGW.rw={segs:[],i:0};G.tick(1/30);if(G.state!=='play')__s()}o.wBusy=+(G.TGW.camW||0).toFixed(2);
          G.TGW.rw=null;e.st='chase';for(let i=0;i<30*4;i++){P.hp=P.max;P.inv=1;G.tick(1/30);if(G.state!=='play')__s()}o.wAfter=+(G.TGW.camW||0).toFixed(2);return o}""")
        R['errs2'] = pg.errs2[:4]; await pg.close()
        # 6) 도감: 해금한 캐릭터는 진화 루트에서 스킬을 볼 수 있다
        pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function("__G.IMG&&__G.IMG.boss", timeout=90000)
        R['dex'] = await ev(pg, """()=>{const G=__G,o={};G.SAVE.chars.wolf=true;G.openRoutePic('wolf');const cards=document.querySelectorAll('#routeTree .rc.sk');o.cards=cards.length;
          o.skills=[...document.querySelectorAll('#routeTree .rc i')].map(x=>x.textContent);
          const c=[...cards].find(x=>x.querySelector('i'));c.click();o.panel=document.getElementById('routeSkill').textContent.slice(0,90);
          const none=[...cards].find(x=>!x.querySelector('i'));none.click();o.panelNone=document.getElementById('routeSkill').textContent.slice(0,60);
          G.SAVE.chars.octo=false;G.openRoutePic('octo');o.lockedShown=document.getElementById('routeSkill').style.display;
          G.SAVE.chars.octo=true;G.openRoutePic('snail');o.snail=[...document.querySelectorAll('#routeTree .rc i')].map(x=>x.textContent);
          G.SAVE.chars.ghost=true;G.openRoutePic('ghost');o.ghost=[...document.querySelectorAll('#routeTree .rc i')].map(x=>x.textContent);return o}""")
        await pg.screenshot(path=B + 'v972_route.png')
        R['dexErr'] = errs[:3]; await pg.close()
        # 7) 연보라 총령: 1진화 확대 캔버스 없음
        pg = await h301.newpage(b, 1280, 720)
        R['ghost'] = await ev(pg, """()=>{const G=__G;G.SAVE.chars.ghost=true;G.startGame('ghost');window.__rt=0;__lv(12);const D=G.FD?null:null;const img=G.IMG.gg;const H=G.hqLow?G.hqLow(img,0.78):null;
          return {form:G.P.form,route:G.P.route,sameImg:H===img,hq2:G.hq(img)!==img}}""")
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
