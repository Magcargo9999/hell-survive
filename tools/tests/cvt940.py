"""v9.40 영벌의 화염죄수 (지하 26층 100% · 27층 70% · 28층부터 균등 · 팔열지옥 보스방 = 용암 보스맵 v9.53 — 좌표는 마왕성 값 + (2800, 1500))
 확률 · 패턴 순환 · 불길 궤적(화상 중첩) · 형벌의 쇠사슬(피하기 · 도넛 구속) · 용광로의 저주(불타는 구슬) · 속죄의 고통(반사 상한) · 절규 해골 고리 ·
 30% 족쇄 해방(예고선 돌진 · 비키면 안전 · 보스방 안) · 처치 · 업적 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/cvt940.py   (스크린샷 build/cvt_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
STEP = "if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.cvt', timeout=90000)
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.cvBurn=0};window.__cvc=()=>{const W=__G.CVW;W.patches=[];W.skulls=[];W.embers=[];W.chain=null;W.tether=null;W.aim=null;__G.P.cvBurn=0;__G.P.cvTetImm=0}}")
        R = {}
        R['A'] = await pg.evaluate("""()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.t25=cnt(25,'cvt');o.t26=cnt(26,'cvt');o.t27=cnt(27,'cvt');o.t24=cnt(24,'cvt');o.t22=cnt(22,'cvt');
          G.SAVE.diff.max=24;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=25;P.fset='fire';P.bossK='cvt';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);"""+STEP+"""const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.ice=!!(G.arena&&G.arena.ice);o.mush=!!(G.arena&&G.arena.mush);
          const seen={},sts=[];let last='',maxP=0;
          for(let i=0;i<30*100;i++){P.hp=P.max;P.inv=1;P.cvBurn=0;bo.hp=Math.max(bo.max*0.6,Math.min(bo.hp,bo.max*0.95));G.tick(1/30);"""+STEP+"""const e=G.boss;if(!e)break;maxP=Math.max(maxP,G.CVW.patches.filter(p=>p.life>0.6).length);if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');o.maxPatch=maxP;o.patchIn=G.CVW.patches.every(p=>G.inPoly(p.x,p.y));o.bossIn=G.inPoly(bo.x,bo.y);return o}""")
        # 화상: 장판 위에 서 있으면 0.5초마다 +1 (최대 4) · 벗어나면 식는다
        R['burn'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.cv;for(const k in AI.cd)AI.cd[k]=99;G.CVW.chain=null;G.CVW.tether=null;G.CVW.skulls=[];e.tele=[];e.st='chase';e.stT=99;
          G.CVW.patches=[];const pt=new (G.CVW.patches.constructor)();e.x=3400;e.y=2200;P.x=3900;P.y=2400;
          __cvc();G.CVW.patches.push(new G.HellfirePatch(P.x,P.y,12));G.CVW.patches[0].max=13;
          G.boss.st='chase';const ai=G.cv;__cl();P.max=1000;P.hp=P.max;let st=[];for(let i=0;i<30*3;i++){P.x=3900;P.y=2400;e.x=3300;e.y=2100;G.tick(1/30);if(i%15==14)st.push(P.cvBurn)}
          o.stacks=st.join(',');o.lost=Math.round(P.max-P.hp);o.lostPct=+((P.max-P.hp)/P.max*100).toFixed(1);
          P.x=4100;P.y=2500;const s0=P.cvBurn;for(let i=0;i<30*4;i++){P.x=4100;P.y=2500;e.x=3300;e.y=2100;G.tick(1/30)}o.cooled=[s0,P.cvBurn];o.state=G.state;P.hp=P.max;return o}""")
        # 쇠사슬: 그대로 서 있으면 묶이고, 고정 뒤 옆으로 비키면 피한다
        R['chain'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.cv;__cvc();G.boss.st='chase';const ai=G.cv||AI;
          e.x=3400;e.y=2200;e.face=1;P.x=3800;P.y=2300;e.st='chase';e.stT=99;
          const go=(side)=>{G.CVW.chain=null;G.CVW.tether=null;P.cvTetImm=0;__cl();P.hp=P.max;e.x=3400;e.y=2200;P.x=3800;P.y=2300;G.cv.go('chain',99,'atk');G.CVW.chain={ph:'warn',t:0,x:e.x+40,y:e.y-30,ang:0,s:0};
            let el=0;for(let i=0;i<30*1.6;i++){e.x=3400;e.y=2200;el+=1/30;if(side&&el>G.CV.chAim)P.y=2300+Math.min(120,(el-G.CV.chAim)*150);P.x=3800;G.tick(1/30);P.inv=0}
            return !!G.CVW.tether};
          o.stand=go(false);o.dodge=go(true);
          // 묶인 뒤: 너무 가까우면 화염 오라, 너무 멀면 끌려온다, 도넛 안이면 피해 없음
          G.CVW.chain=null;G.CVW.tether={t:5.5,warnT:0};e.st='chase';e.stT=99;for(const k in G.cv.cd)G.cv.cd[k]=99;
          __cl();P.hp=P.max;let h=P.hp;for(let i=0;i<30;i++){e.x=3500;e.y=2200;P.x=e.x+80;P.y=e.y;G.tick(1/30);P.inv=0}o.nearLoss=Math.round(h-P.hp);
          P.hp=P.max;h=P.hp;for(let i=0;i<30;i++){e.x=3500;e.y=2200;P.x=e.x+280;P.y=e.y;G.tick(1/30)}o.bandLoss=Math.round(h-P.hp);
          G.CVW.tether.t=5;const d0=Math.hypot(1350-700,0);P.x=4150;P.y=2200;for(let i=0;i<30;i++){e.x=3500;e.y=2200;G.tick(1/30)}o.pull=[Math.round(d0),Math.round(Math.hypot(P.x-700,P.y-700)),+P.slowT.toFixed(2)];
          for(let i=0;i<30*6;i++){e.x=3500;e.y=2200;P.x=e.x+280;P.y=e.y;P.hp=P.max;G.tick(1/30)}o.freed=!G.CVW.tether;o.imm=+P.cvTetImm.toFixed(1);o.ex=G.CVW.tether?1:0;return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;e.x=3500;e.y=2260;P.x=3800;P.y=2320;G.CVW.tether={t:4,warnT:0};for(let i=0;i<8;i++){const q=new G.HellfirePatch(600+i*60,860+Math.sin(i)*30,9);q.max=12;q.seed=i;G.CVW.patches.push(q)}P.hp=P.max;G.tick(1/30);G.render&&G.render()}""")
        await pg.screenshot(path=B + 'cvt_chain.png')
        # 용광로의 저주: 구슬이 불타고, 자석 무시 · 닿으면 화상(경험치 없음) · 식으면 경험치
        R['furn'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;G.CVW.tether=null;G.CVW.chain=null;G.CVW.patches=[];P.cvBurn=0;e.x=3500;e.y=2200;P.x=3900;P.y=2400;
          G.orbs.length=0;G.orbs.push({x:P.x+300,y:P.y,val:5,t:0});const pk=P.pickup;P.pickup=900;G.cvFurnace(e);o.n=G.orbs.length;o.burning=G.orbs.filter(q=>q.burnT>0).length;
          o.minD=Math.round(Math.min(...G.orbs.map(q=>Math.hypot(q.x-P.x,q.y-P.y))));o.ex=G.cvExPause?1:0;
          const x0=G.orbs.map(q=>q.x+','+q.y).join('|');for(let i=0;i<30;i++){P.x=3900;P.y=2400;P.hp=P.max;G.tick(1/30)}o.moved=G.orbs.map(q=>q.x+','+q.y).join('|')!==x0;
          const q=G.orbs[1];__cl();P.hp=P.max;const h=P.hp,ex=P.exp,lv=P.lvl;P.x=q.x;P.y=q.y+10;G.tick(1/30);o.touch=[Math.round(h-P.hp),P.exp-ex,G.orbs.includes(q),P.cvBurn];
          for(let i=0;i<30*5;i++){P.x=3900;P.y=2400;P.hp=P.max;P.inv=1;G.tick(1/30)}o.cool=G.orbs.filter(q=>q.burnT>0).length;
          const n1=G.orbs.length;for(let i=0;i<30*2;i++){P.hp=P.max;G.tick(1/30);__s()}o.pickedAfter=n1-G.orbs.length;P.pickup=pk;return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;e.x=3500;e.y=2260;P.x=3800;P.y=2360;G.CVW.patches=[];G.cvFurnace(e);G.boss.st='furnace';G.boss.an='furn';for(let i=0;i<6;i++)G.tick(1/30);G.render&&G.render()}""")
        await pg.screenshot(path=B + 'cvt_furnace.png')
        # 속죄의 고통: 피해 0 · 직접 공격 반사(2%, 최대 12%) · 지속 피해는 반사 없음 · 동료는 반사 없음
        R['atone'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.cv;G.orbs.length=0;G.CVW.patches=[];P.cvBurn=0;for(const k in AI.cd)AI.cd[k]=99;
          e.x=3500;e.y=2200;P.x=3950;P.y=2400;AI.go('atone',3,'kneel');G.CVW.refl=0;G.CVW.reflT=-9;__cl();P.hp=P.max;const h0=e.hp;
          G.hurtEnemy(e,5000,0,0,0);o.dmg=Math.round(h0-e.hp);e.stT=3;G.tick(1/30);o.one=+((P.max-P.hp)/P.max*100).toFixed(1);
          for(let i=0;i<90;i++){P.inv=0;G.hurtEnemy(e,300,0,0,0);G.tick(1/30);e.stT=3}o.capPct=+((P.max-P.hp)/P.max*100).toFixed(1);
          P.hp=P.max;G.CVW.refl=0;G.CVW.reflT=-9;G.hurtEnemy(e,300,0,0,0,true);e.stT=3;G.tick(1/30);o.quiet=Math.round(P.max-P.hp);
          o.after=null;AI.go('atone',0.05,'kneel');let sk=0;for(let i=0;i<30*0.8;i++){P.hp=P.max;P.inv=1;G.tick(1/30);sk=Math.max(sk,G.CVW.skulls.length)}o.skulls=sk;o.st=e.st;
          const h1=e.hp;G.hurtEnemy(e,500,0,0,0);o.dmgAfter=Math.round(h1-e.hp);return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.cv;G.CVW.skulls=[];e.x=3500;e.y=2260;P.x=3850;P.y=2400;AI.go('atone',2.5,'kneel');G.tick(1/30);AI.go('scream',0.9,'kneel');G.boss.st='scream';G.CVW.skulls=[];
          const n=14;for(let i=0;i<n;i++){const a=i*6.283/n;G.CVW.skulls.push({x:e.x+Math.cos(a)*170,y:e.y-70+Math.sin(a)*120,vx:Math.cos(a)*230,vy:Math.sin(a)*184,life:3,f:i%5})}AI.go('atone',2.5,'kneel');G.render&&G.render()}""")
        await pg.screenshot(path=B + 'cvt_atone.png')
        # 2페이즈: 족쇄 해방 → 조준 → 돌진 → 폭발 → 숨 고르기 · 비켜 있으면 안전 · 보스방 안 · 3번마다 용광로
        R['ph2'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.cv;G.CVW.skulls=[];G.CVW.patches=[];G.CVW.tether=null;e.st='chase';e.stT=0.5;for(const k in AI.cd)AI.cd[k]=99;
          e.hp=e.max*0.29;for(let i=0;i<3;i++){P.hp=P.max;P.inv=1;G.tick(1/30)}o.st=e.st;o.ph2=e.ph2;o.invul=e.invul;
          const seen={};let last='',dashes=0,furn=0,out=0,maxP=0;
          for(let i=0;i<30*40;i++){P.hp=P.max;P.inv=1;e.hp=Math.max(e.hp,e.max*0.2);G.tick(1/30);"""+STEP+"""if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;if(e.st==='dash')dashes++;if(e.st==='furnace')furn++}if(!G.inPoly(e.x,e.y))out++;maxP=Math.max(maxP,G.CVW.patches.filter(p=>p.life>0.6).length)}
          o.seen=seen;o.dashes=dashes;o.furn=furn;o.out=out;o.maxPatch=maxP;
          // 비키기: 조준이 고정된 순간 예고선에서 수직으로 160 떨어져 있으면 몸통 · 폭발에 안 맞는다
          let hitN=0,tries=0;for(let k=0;k<4;k++){G.CVW.patches=[];G.CVW.embers=[];e.x=3400;e.y=2150;P.x=3900;P.y=2300;AI.go('aim',G.CV.daAim,'idle');__cl();P.hp=P.max;let moved=false;
            for(let i=0;i<30*3;i++){const q=G.CVW.aim;if(q&&q.t>=G.CV.daLock&&!moved){moved=true;const a=q.ang;P.x+=-Math.sin(a)*160;P.y+=Math.cos(a)*160}G.CVW.embers=[];G.tick(1/30);P.inv=0;if(e.st==='rest')break}tries++;if(P.hp<P.max)hitN++;o['t'+k]=[Math.round(P.max-P.hp),Math.round(Math.hypot(P.x-e.x,P.y-e.y)),Math.round(e.x),Math.round(e.y),Math.round(P.x),Math.round(P.y)]}
          o.sidestepHit=hitN+'/'+tries;
          // 그대로 서 있으면 맞는다
          G.CVW.embers=[];e.x=3400;e.y=2150;P.x=3800;P.y=2260;AI.go('aim',G.CV.daAim,'idle');__cl();P.hp=P.max;for(let i=0;i<30*3;i++){G.CVW.embers=[];G.tick(1/30);if(e.st==='rest')break}o.standHit=Math.round(P.max-P.hp);return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.cv;e.x=3450;e.y=2200;P.x=3900;P.y=2380;AI.go('aim',G.CV.daAim,'idle');for(let i=0;i<20;i++){P.inv=1;G.tick(1/30)}G.render&&G.render()}""")
        await pg.screenshot(path=B + 'cvt_ph2.png')
        R['X'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;delete G.SAVE.ach.done.k_cvt;const k0=G.SAVE.dex.kills.boss17|0;P.inv=1;e.invul=false;e.st='chase';G.hurtEnemy(e,e.max*5,0,0,0);
          for(let i=0;i<60;i++){P.hp=P.max;G.tick(1/30);}o.dead=!G.boss||G.boss.hp<=0;o.kills=(G.SAVE.dex.kills.boss17|0)-k0;G.achSync&&G.achSync();o.ach=!!G.SAVE.ach.done.k_cvt;
          o.clear=G.CVW.patches.length+G.CVW.skulls.length+G.CVW.embers.length+(G.CVW.tether?1:0);o.burnOrbs=G.orbs.filter(q=>q.burnT>0).length;o.death=!!G.CVW.death;return o}""")
        R['errs'] = errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
