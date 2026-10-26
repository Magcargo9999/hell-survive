"""v9.63 지옥의 화염 호랑이 (지하 30층 전용 최종 마왕)
 확률 · 30층 개방 · 순환 · 불의 십자가(회전 중 바깥 안전 · 불 뿜기 때 팔 사이·출구 통로 안전) · 가드(피해 0 · 횟수 → 반격 반경 상한) ·
 연속 돌진 · 수플렉스(안전지대 = 빗나감 / 밖 = 잡힘 → 현재 체력 80% · 잡몹 즉사) · 완벽 회피 3연속 → 기절 · 40% 2페이즈(십자가 소멸 · 카메라 고정 · 리듬 돌진 안전 공간) ·
 처치 · 업적 · 스크린샷
사용: GAME_URL=http://localhost:8765/build/hell_survive.html PYTHONPATH=tools python3 tools/tests/tig963.py   (스크린샷 build/tig_*.png)"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        await pg.evaluate("""()=>{window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};
          window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1};
          window.__free=()=>{const AI=__G.tg;for(const k in AI.cd)AI.cd[k]=99}}""")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};let c=0;for(let i=0;i<2000;i++)if(G.pickBossK(29)==='tig')c++;o.t30=c/20;c=0;for(let i=0;i<2000;i++)if(G.pickBossK(28)==='tig')c++;o.t29=c/20;
          o.open=G.OPEN_TIER;G.SAVE.diff.max=29;G.SAVE.diff.sel=29;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(30);o.tier=P.tier;G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const e=G.boss;o.bk=e&&e.bk;o.fire=!!(G.arena&&G.arena.fire);o.arms=G.tgArms().length;
          const seen={},sts=[];let last='';for(let i=0;i<30*90;i++){P.hp=P.max;P.inv=1;e.hp=Math.max(e.max*0.6,e.hp);__tk();if(e.st!==last){last=e.st;sts.push(e.st);seen[e.st]=(seen[e.st]||0)+1}}
          o.seen=seen;o.seq=sts.slice(0,26).join('>');o.pIn=G.inPoly(P.x,P.y);return o}""")
        # 불의 십자가: 회전 중 반경 610 밖은 늘 안전 · 불 뿜기 때 팔 사이(45°) · 아래 출구 통로는 안전 · 팔 위는 맞음
        R['cross'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,C=G.TGW.cr,cx=G.IMAP.cx,cy=G.IMAP.cy;__free();P.max=1e5;P.hp=P.max;C.off=0;C.hold=false;C.ph='spin';C.t=0;C.van=0;
          let outHit=0,inHit=0,brGap=0,brArm=0,corr=0;
          for(let i=0;i<30*14;i++){e.x=cx-900;e.y=cy;G.tg.go('stun',99,'stun');P.inv=1;P.hp=P.max;__tk();
            for(let k=0;k<16;k++){const a=k*0.3927;if(G.tgCrossAt(cx+Math.cos(a)*640,cy+Math.sin(a)*640,22))outHit++}
            if(C.ph==='breath'&&C.t>=G.TG.crBrWarn){for(let k=0;k<4;k++){const a=C.a+Math.PI/4+k*Math.PI/2;if(G.tgCrossAt(cx+Math.cos(a)*400,cy+Math.sin(a)*400,22))brGap++;const b=C.a+k*Math.PI/2;if(G.tgCrossAt(cx+Math.cos(b)*(C.len[k]-30),cy+Math.sin(b)*(C.len[k]-30),0))brArm++}
              if(G.tgCrossAt(cx,G.IMAP.Y1+60,22))corr++}
            if(G.tgCrossAt(cx+Math.cos(C.a)*300,cy+Math.sin(C.a)*300,0))inHit++}
          o.outHit=outHit;o.breathGapHit=brGap;o.breathArm=brArm>0;o.corridor=corr;o.onArm=inHit>0;
          // 팔 위에 서 있으면 맞는다
          __cl();P.hp=P.max;C.ph='spin';C.t=0;C.a=0;G.TGW.crHitT=0;P.x=cx+300;P.y=cy;__tk();o.armDmg=Math.round(P.max-P.hp);return o}""")
        # 가드: 피해 0 · 맞은 횟수 → 반격 반경(상한 400) · 다음 돌진 속도 상한
        R['guard'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg;__free();G.TGW.cr.off=99;e.tele=[];e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=e.x+700;P.y=e.y;
          AI.guardStart();const h0=e.hp;for(let i=0;i<50;i++){G.hurtEnemy(e,5000,0,0,0);P.inv=1;__tk()}o.dmg=Math.round(h0-e.hp);o.hits=G.TGW.gHits;o.R=Math.round(G.tgCxR());
          G.TGW.gHits=200;o.Rcap=Math.round(G.tgCxR());G.TGW.gHits=o.hits;
          for(let i=0;i<30*2;i++){P.inv=1;__tk()}o.st=e.st;o.boost=+AI.boost.toFixed(2);G.TGW.gHits=200;AI.go('guard',0.01,'guard');__tk();o.boostCap=+AI.boost.toFixed(2);
          for(let i=0;i<30*2;i++){P.inv=1;__tk()}o.after=e.st;return o}""")
        # 연속 돌진: 3번 + 마무리 · 맞음 판정
        R['dash'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg;__free();G.TGW.cr.off=99;e.tele=[];AI.boost=1;e.x=G.IMAP.cx-500;e.y=G.IMAP.cy;P.x=G.IMAP.cx+200;P.y=G.IMAP.cy;
          __cl();P.hp=P.max;AI.dashStart();const sts=[];let last='';for(let i=0;i<30*6;i++){__tk();if(e.st!==last){last=e.st;sts.push(e.st)}if(e.st==='chase'||e.st==='stun')break}
          o.seq=sts.join('>');o.took=Math.round(P.max-P.hp);o.bIn=G.inPoly(e.x,e.y);return o}""")
        # 수플렉스: 안전지대 안 = 빗나감 · 밖 = 잡힘(현재 체력 80%) · 잡몹 즉사
        R['sx'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg,C=G.TGW.cr;__free();C.off=0;C.van=0;e.tele=[];e.x=G.IMAP.cx-700;e.y=G.IMAP.cy+200;P.x=G.IMAP.cx+500;P.y=G.IMAP.cy+250;
          const res=[];
          for(const inside of [true,false]){__cl();P.hp=P.max*0.9;P.inv=0;G.TGW.crHitT=99;for(let k=0;k<6;k++)G.spawnEnemy(k,300);const nm=G.enemies.filter(q=>q.kind==='mob'&&q.hp>0).length;
            AI.sxStart();const S=G.TGW.safe;const d=Math.hypot(S.x-P.x,S.y-P.y);const onCross=G.tgCrossAt(S.x,S.y,S.r);const h0=P.hp;let held=0,sts=[],last='';
            for(let i=0;i<30*6;i++){if(inside){P.x=S.x;P.y=S.y}else{P.x=S.x+300;P.y=S.y}G.TGW.crHitT=99;__tk();if(e.st!==last){last=e.st;sts.push(e.st)}if(e.st==='sxHold')held++;if(e.st==='chase'||e.st==='stun')break}
            res.push({inside,dist:Math.round(d),onCross,seq:sts.join('>'),held:held>0,hpPct:+(P.hp/h0).toFixed(3),mobs0:nm,mobs1:G.enemies.filter(q=>q.kind==='mob'&&q.hp>0).length,crossHeldAfter:C.hold})}
          o.res=res;return o}""")
        # 안전지대 위치 규칙 9: 수플렉스를 여러 번 — 안전지대가 늘 2.6초 안에 닿는 거리, 십자가와 안 겹침
        R['sxSafe'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,C=G.TGW.cr;let far=0,cross=0,n=0;C.off=0;
          for(let k=0;k<300;k++){C.a=Math.random()*6.28;P.x=G.IMAP.X0+200+Math.random()*(G.IMAP.X1-G.IMAP.X0-400);P.y=G.IMAP.Y0+150+Math.random()*(G.IMAP.Y1-G.IMAP.Y0-300);if(!G.inPoly(P.x,P.y)||G.tgCrossAt(P.x,P.y,30))continue;e.x=P.x+600;e.y=P.y;
            const S=G.tgSafeSpot(e);n++;if(Math.hypot(S.x-P.x,S.y-P.y)>150*G.TG.sxWarn-20)far++;if(G.tgCrossAt(S.x,S.y,S.r))cross++}
          o.n=n;o.far=far;o.cross=cross;return o}""")
        # 완벽 회피 3연속 → 기절 · 맞으면 끊김
        R['stun'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg,C=G.TGW.cr;C.off=0;C.gone=false;G.TGW.streak=0;G.TGW.hitF=false;AI.chase(5);
          G.tgPatEnd();G.tgPatEnd();o.s2=G.TGW.streak;G.TGW.hitF=true;G.tgPatEnd();o.broken=G.TGW.streak;G.tgPatEnd();G.tgPatEnd();const r=G.tgPatEnd();o.stun=r&&e.st==='stun';o.crossOff=C.off>0;o.arms=G.tgArms().length;
          const h0=e.hp;G.hurtEnemy(e,1000,0,0,0);o.dmgInStun=Math.round(h0-e.hp);for(let i=0;i<30*5;i++){P.inv=1;P.hp=P.max;__tk()}o.after=e.st;return o}""")
        # 2페이즈: 십자가 소멸 · 카메라 고정 · 이속 1.5배 · 리듬 돌진 안전 공간
        R['ph2'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg;__free();e.tele=[];AI.chase(1);e.hp=e.max*0.39;e.x=G.IMAP.cx;e.y=G.IMAP.cy-200;P.x=G.IMAP.cx;P.y=G.IMAP.cy+200;
          for(let i=0;i<30*3;i++){P.inv=1;P.hp=P.max;__tk()}o.ph2=e.ph2;o.cross=G.tgArms().length;o.cam=G.tgCam();
          const W=G.W||innerWidth,H=G.H||innerHeight;let outView=0,maxSp=0,lx=e.x,ly=e.y,types={},unsafe=0,rw=0,sts={};
          for(let i=0;i<30*40;i++){P.inv=1;P.hp=P.max;__tk();if(e.st==='prowl'){maxSp=Math.max(maxSp,Math.hypot(e.x-lx,e.y-ly)*30)}lx=e.x;ly=e.y;sts[e.st]=(sts[e.st]||0)+1;
            const R=G.TGW.rw;if(R&&R.segs.length&&!R.chk){R.chk=1;rw++;types[R.ty]=(types[R.ty]||0)+1;
              // 줄들이 덮지 않는 자리가 내 둘레 160 안에 남는가 (줄 폭 + 내 몸)
              let ok=0,all=0;for(let a=0;a<6.28;a+=0.2)for(let r=0;r<=160;r+=20){all++;const x=P.x+Math.cos(a)*r,y=P.y+Math.sin(a)*r;if(!G.inPoly(x,y))continue;if(!R.segs.some(s=>G.segDist(x,y,s.ax,s.ay,s.bx,s.by)<G.TG.rwW+28))ok++}
              if(ok===0)unsafe++}}
          o.types=types;o.rwSets=rw;o.unsafe=unsafe;o.prowlSp=Math.round(maxSp);o.pSpd=Math.round(P.spd);o.sts=sts;return o}""")
        # 카메라: 호랑이를 따라가고 나는 화면 안에 남는다
        R['cam'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.tg;__free();AI.chase(99);e.x=G.IMAP.cx-900;e.y=G.IMAP.cy;P.x=G.IMAP.cx+900;P.y=G.IMAP.cy;
          for(let i=0;i<60;i++){P.inv=1;P.hp=P.max;__tk()}const W=innerWidth;o.camToBoss=Math.round(Math.abs(G.cam.x-e.x));o.pToCam=Math.round(Math.abs(P.x-G.cam.x));o.half=W/2;o.pIn=G.inPoly(P.x,P.y);return o}""")
        # 처치 · 업적
        R['kill'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss;e.invul=false;G.tg.go('stun',9,'stun');G.hurtEnemy(e,e.hp+10,0,0,0);for(let i=0;i<60;i++){P.inv=1;P.hp=P.max;__tk()}
          o.dead=!G.boss||G.boss.hp<=0;o.kills=G.SAVE.dex.kills.boss19|0;G.achSync&&G.achSync();o.ach=!!(G.SAVE.ach&&G.SAVE.ach.done&&G.SAVE.ach.done.k_tig);o.h6=!!(G.SAVE.ach&&G.SAVE.ach.done&&G.SAVE.ach.done.h6);o.clr=G.SAVE.diff.clr;o.cr=!!G.TGW.cr;return o}""")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        # 스크린샷
        async def shot(name, js, n=0):
            await ev(pg, "()=>{const G=__G;G.SAVE.diff.max=29;G.SAVE.diff.sel=29;if(!G.boss||G.boss.hp<=0||G.boss.bk!=='tig'){G.startGame('archer');__lv(30);G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)__tk()}const P=G.P,e=G.boss,AI=G.tg,C=G.TGW.cr;for(const k in AI.cd)AI.cd[k]=99;P.hp=P.max;P.inv=99;e.tele=[];" + js + "for(let i=0;i<" + str(n) + ";i++){P.inv=99;__tk()}G.render()}")
            await pg.screenshot(path=B + 'tig_' + name + '.png')
        C0 = "e.ph2=false;if(C){C.gone=false;C.off=0;C.van=0;C.hold=false}"
        await shot('spin', C0 + "C.ph='spin';C.t=1;C.a=0.3;e.x=G.IMAP.cx+500;e.y=G.IMAP.cy-250;P.x=G.IMAP.cx+380;P.y=G.IMAP.cy+300;AI.chase(99);", 3)
        await shot('breath', C0 + "C.ph='spin';C.t=4.95;e.x=G.IMAP.cx+500;e.y=G.IMAP.cy-250;P.x=G.IMAP.cx+380;P.y=G.IMAP.cy+300;AI.chase(99);", 30)
        await shot('breathwarn', C0 + "C.ph='spin';C.t=4.95;e.x=G.IMAP.cx+500;e.y=G.IMAP.cy-250;P.x=G.IMAP.cx+380;P.y=G.IMAP.cy+300;AI.chase(99);", 8)
        await shot('guard', C0 + "C.off=99;e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=e.x+260;P.y=e.y+60;AI.guardStart();G.TGW.gHits=9;", 20)
        await shot('counter', C0 + "C.off=99;e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=e.x+420;P.y=e.y+60;AI.guardStart();G.TGW.gHits=12;", 60+25)
        await shot('dashwarn', C0 + "C.off=99;e.x=G.IMAP.cx-400;e.y=G.IMAP.cy;P.x=G.IMAP.cx+100;P.y=G.IMAP.cy+80;AI.dashStart();", 8)
        await shot('dash', C0 + "C.off=99;e.x=G.IMAP.cx-400;e.y=G.IMAP.cy;P.x=G.IMAP.cx+100;P.y=G.IMAP.cy+180;AI.dashStart();", 19)
        await shot('sxwarn', C0 + "e.x=G.IMAP.cx-300;e.y=G.IMAP.cy+250;P.x=G.IMAP.cx+300;P.y=G.IMAP.cy+300;AI.sxStart();", 20)
        await shot('sxjump', C0 + "e.x=G.IMAP.cx-300;e.y=G.IMAP.cy+250;P.x=G.IMAP.cx+300;P.y=G.IMAP.cy+300;AI.sxStart();P.inv=0;", 0)
        await ev(pg, "()=>{const G=__G,P=G.P,e=G.boss;for(let i=0;i<30*2.9;i++){P.inv=0;P.x=G.TGW.safe?G.TGW.safe.x+400:P.x;__tk()}for(let i=0;i<26;i++)__tk();G.render()}")
        await pg.screenshot(path=B + 'tig_sxhold.png')
        await shot('stun', C0 + "e.x=G.IMAP.cx-400;e.y=G.IMAP.cy+250;P.x=G.IMAP.cx;P.y=G.IMAP.cy+300;AI.stun();", 20)
        await shot('ph2cut', "e.hp=e.max*0.39;AI.chase(0.1);e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=G.IMAP.cx+200;P.y=G.IMAP.cy+200;", 12)
        await shot('rhythm', "e.ph2=true;if(C)C.gone=true;e.x=G.IMAP.cx-300;e.y=G.IMAP.cy;P.x=G.IMAP.cx+100;P.y=G.IMAP.cy+80;G.TGW.cut=0;AI.rwStart();", 12)
        await shot('rhythm2', "e.ph2=true;if(C)C.gone=true;e.x=G.IMAP.cx-300;e.y=G.IMAP.cy;P.x=G.IMAP.cx+100;P.y=G.IMAP.cy+80;G.TGW.cut=0;AI.rwStart();", 12)
        print('errs', errs[:8]); await b.close()
asyncio.run(main())
