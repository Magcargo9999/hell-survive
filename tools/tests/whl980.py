"""v9.80 심해의 시체고래 (지하 18층 100% · 19층 70% · 어인섬 보스방 SMAP)
 확률 · 순환(모든 패턴이 한 번씩 나옴) · 규칙 9(해류 줄 사이 틈 · 소용돌이 끌림 < 이속 · 잠수 원은 움직이면 못 따라잡음 · 몸통박치기/뼈는 이속 150으로 피함 · 죽음의 파도 안전 줄은 항상 1~2칸 옆이고 시간 안에 들어갈 수 있음) · 2페이즈 · 처치 · 도감 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/whl980.py   (스크린샷 build/whl_*.png)"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','smap','whl','whlfx'])", timeout=120000, polling=1000)
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1};window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};window.__only=(k)=>{const AI=__G.wh;for(const c in AI.cd)AI.cd[c]=99;AI.cd[k]=0;AI.cyc=[k];AI.ci=0};window.__go=(k)=>{const AI=__G.wh,e=__G.boss;e.tele=[];__G.WHW.cur=[];__G.WHW.vorts=[];__G.WHW.dive=null;__G.WHW.wv=null;__only(k);AI.chase(0);e.stT=0}}")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.t16=cnt(16,'whl');o.t17=cnt(17,'whl');o.t18=cnt(18,'whl');o.t19=cnt(19,'whl');o.t20=cnt(20,'whl');o.t21=cnt(21,'whl');o.t23=cnt(23,'whl');
          G.SAVE.diff.max=20;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=17;P.fset='sea';P.bossK='whl';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.arena=!!(G.arena&&G.arena.sea);
          const seen={},sts=[];let last='',out=0,pats={};
          for(let i=0;i<30*150;i++){P.hp=P.max;P.inv=1;bo.hp=Math.max(bo.max*0.5,Math.min(bo.hp,bo.max*0.95));__tk();const e=G.boss;if(!e)break;if(!G.inPoly(e.x,e.y)&&e.alpha>0)out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,40).join('>');o.bossOut=out;o.pIn=G.inPoly(P.x,P.y);return o}""")
        # 해류: 줄이 부채꼴 · 가운데 줄에 서 있으면 맞고, 옆으로 비키면 안 맞는다
        R['breath'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const run=(side)=>{__cl();P.hp=P.max;P.inv=0;e.x=1800;e.y=1500;e.face=1;P.x=2300;P.y=1500;__go('breath');let hit=false;
            for(let i=0;i<30*3;i++){P.inv=0;if(side&&i<45){P.y+=side*150/30}__tk();if(P.hp<P.max){hit=true;break}}return hit};
          o.stand=run(0);o.side=run(1);o.sideN=run(-1);
          // 가까이 (d≈200) · 멀리 (d≈700) 에서도 옆으로 비키면 피한다
          const r2=(d)=>{__cl();P.hp=P.max;e.x=1800;e.y=1500;P.x=1800+d;P.y=1500;__go('breath');let hit=false;for(let i=0;i<30*3;i++){P.inv=0;if(i<40)P.y+=150/30;__tk();if(P.hp<P.max){hit=true;break}}return hit};
          const gap=(d)=>{__cl();P.hp=P.max;e.x=1800;e.y=1500;P.x=1800+d;P.y=1500;__go('breath');let hit=false;const gy=d*Math.tan(0.34)/2;for(let i=0;i<30*3;i++){P.inv=0;if(P.y<1500+gy)P.y=Math.min(1500+gy,P.y+150/30);__tk();if(P.hp<P.max){hit=true;break}}return hit};
          o.gap450=gap(450);o.gap700=gap(700);o.d200=r2(200);return o}""")
        # 뼈 소환 · 몸통박치기: 서 있으면 맞고 이속 150으로 피한다
        R['bones'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};let bad=0;for(let k=0;k<20;k++){__cl();e.x=1500;e.y=1300;P.x=2000;P.y=1700;__go('bones');const T=e.tele.filter(t=>t.k==='circle');let ok=false;const reach=150*G.WH.boWarn;for(let a=0;a<64&&!ok;a++)for(const rr of [20,60,100]){const x=P.x+Math.cos(a/10)*rr*Math.min(1,reach/100),y=P.y+Math.sin(a/10)*rr*Math.min(1,reach/100);if(!T.some(t=>Math.hypot(x-t.x,(y-t.y)*1.5)<t.r+20)){ok=true;break}}if(!ok)bad++}o.noSafe=bad;const run=(mv)=>{__cl();P.hp=P.max;e.x=1500;e.y=1300;P.x=2000;P.y=1700;__go('bones');let hit=false;
            for(let i=0;i<30*3;i++){P.inv=0;if(mv&&i<30)P.x+=150/30;__tk();if(P.hp<P.max){hit=true;break}}return hit};o.stand=run(false);o.move=run(true);return o}""")
        R['slam'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const run=(mv)=>{__cl();P.hp=P.max;e.x=1500;e.y=1300;P.x=2000;P.y=1700;__go('slam');let hit=false,inv=0;
            for(let i=0;i<46;i++){P.inv=0;if(mv&&i<42)P.x+=150/30;__tk();if(e.invul)inv++;if(P.hp<P.max){hit=true;break}}return [hit,inv]};o.stand=run(false);o.move=run(true);
          o.landed=[Math.round(e.x),Math.round(e.y),e.alpha];return o}""")
        # 소용돌이: 끌려가는 속도 < 이속 → 중심 반대로 150px/s로 달리면 빠져나온다 · 서 있으면 중심까지 끌려가 맞는다
        R['vortex'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};__cl();P.hp=P.max;e.x=1500;e.y=1300;P.x=2000;P.y=1700;__go('vortex');for(let i=0;i<30*2;i++){P.inv=1;__tk()}const V=G.WHW.vorts;o.n=V.length;
          const v=V[0];if(!v)return o;for(let i=0;i<40;i++){P.inv=1;__tk()}const grow=v.t>=G.WH.voGrow;o.grown=grow;
          const sg=v.x<(G.whRoom().x0+G.whRoom().x1)/2?1:-1;P.x=v.x+160*sg;P.y=v.y;P.hp=P.max;let md=1e9;for(let i=0;i<30*2.5;i++){P.inv=0;const dx=P.x-v.x,dy=(P.y-v.y)*1.5,d=Math.hypot(dx,dy)||1;if(!G.inPoly(P.x+dx/d*5,P.y))break;P.x+=dx/d*150/30;P.y+=dy/d*150/30/1.5;__tk();md=Math.min(md,Math.hypot(P.x-v.x,(P.y-v.y)*1.5))}
          o.escaped=Math.round(Math.hypot(P.x-v.x,(P.y-v.y)*1.5));o.hurtRun=Math.round(P.max-P.hp);
          P.x=v.x+160*sg;P.y=v.y;P.hp=P.max;v.t=G.WH.voGrow+0.1;v.life=60;for(let i=0;i<30*6;i++){P.inv=0;__tk()}o.standD=Math.round(Math.hypot(P.x-v.x,(P.y-v.y)*1.5));o.standHurt=Math.round(P.max-P.hp);return o}""")
        # 잠수 습격: 계속 움직이면 안 맞는다(원이 느림) · 서 있으면 맞는다
        R['dive'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const run=(mv)=>{__cl();P.hp=P.max;e.x=1500;e.y=1300;P.x=2000;P.y=1700;__go('dive');let hit=false,ph=[];
            for(let i=0;i<30*7;i++){P.inv=0;if(mv){const a=i/30*0.6;P.x+=Math.cos(a)*150/30;P.y+=Math.sin(a)*150/30}__tk();const D=G.WHW.dive;if(D&&!ph.includes(D.ph))ph.push(D.ph);if(P.hp<P.max){hit=true;break}if(e.st==='chase'&&i>60)break}return [hit,ph.join('>'),Math.round(e.x),Math.round(e.y)]};
          o.stand=run(false);o.move=run(true);return o}""")
        # 죽음의 파도: 안전 줄은 항상 내 줄에서 1~2칸 옆 · 서 있으면 맞고, 150px/s로 걸어서 들어가면 안 맞는다
        R['wave'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const Rm=G.whRoom();o.room=[Math.round(Rm.x0),Math.round(Rm.x1),Math.round(Rm.y0),Math.round(Rm.y1),Math.round(Rm.band)];
          const offs=[],need=[];let hitsStand=0,hitsWalk=0,N=0;
          for(let trial=0;trial<24;trial++){for(const mode of ['stand','walk']){__cl();P.hp=P.max;e.x=Rm.x0+300;e.y=Rm.y0+200;P.x=Rm.x0+300+Math.random()*1600;P.y=Rm.y0+Rm.band*(0.2+Math.random()*9.6);G.whClear&&0;__go('wave');
              let pl=G.whLane(P.y,Rm),got=false,safe=-1,hit=false,walked=0;
              for(let i=0;i<30*14;i++){P.inv=0;const V=G.WHW.wv;if(V&&V.cur){const W=V.cur;if(safe<0){safe=W.safe;pl=G.whLane(P.y,Rm);if(mode==='walk'){offs.push(Math.abs(safe-pl));}}
                  if(mode==='walk'&&!W.go){const ty=Rm.y0+(safe+0.5)*Rm.band,dy=ty-P.y;if(Math.abs(dy)>3){const st=Math.min(Math.abs(dy),150/30);P.y+=Math.sign(dy)*st;walked+=st}}}
                else if(V&&!V.cur&&safe>=0){safe=-1}
                __tk();if(P.hp<P.max){hit=true;break}if(!G.WHW.wv&&i>60)break}
              if(mode==='stand'){hitsStand+=hit?1:0}else{hitsWalk+=hit?1:0;N++;need.push(Math.round(walked))}}}
          o.offs=[...new Set(offs)].sort();o.hitsStand=hitsStand;o.hitsWalk=hitsWalk;o.N=N;o.maxWalk=Math.max(...need);o.warn=G.WH.waWarn;o.walkBudget=Math.round(G.WH.waWarn*150);return o}""")
        # 1페이즈 → 2페이즈(체력 35%) · 2페이즈 파도 3번 · 처치
        R['ph2'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};__cl();G.WHW.cur=[];e.tele=[];e.hp=e.max*0.34;for(let i=0;i<4;i++){P.hp=P.max;P.inv=9;__tk()}o.ph2=e.ph2;o.st=e.st;for(let i=0;i<30*3;i++){P.hp=P.max;P.inv=9;__tk()}o.after=e.st;o.invul=e.invul;
          __go('wave');let n=0,last=null,dirs=[];for(let i=0;i<30*40;i++){P.hp=P.max;P.inv=9;__tk();const V=G.WHW.wv;if(V&&V.cur&&V.cur!==last){last=V.cur;n++;dirs.push(V.cur.dir)}if(!G.WHW.wv&&i>90)break}o.waves=n;o.dirs=dirs.join(',');return o}""")
        await pg.evaluate("""()=>{const G=__G;G.startGame('archer');const P=G.P;__lv(28);P.tier=17;P.fset='sea';P.bossK='whl';G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)__tk();__cl();P.inv=9}""")
        await pg.evaluate("__G.boss&&(__G.boss.hp=__G.boss.max)")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;__cl();P.hp=P.max;P.inv=9;e.x=1800;e.y=1500;P.x=1800;P.y=1700;e.hp=e.max;__go('wave');for(let i=0;i<30*5.2;i++){P.inv=9;__tk()}}""")
        await pg.screenshot(path=B + 'whl_wave.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;P.inv=9;e.x=1700;e.y=1500;P.x=2200;P.y=1600;__go('breath');for(let i=0;i<30*1.35;i++){P.inv=9;__tk()}}""")
        await pg.screenshot(path=B + 'whl_breath.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;P.inv=9;e.x=1700;e.y=1500;P.x=2100;P.y=1650;__go('vortex');for(let i=0;i<30*3.2;i++){P.inv=9;__tk()}}""")
        await pg.screenshot(path=B + 'whl_vortex.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;P.inv=9;e.x=1700;e.y=1500;P.x=2100;P.y=1650;__go('dive');for(let i=0;i<30*3.4;i++){P.inv=9;__tk()}}""")
        await pg.screenshot(path=B + 'whl_dive.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;P.inv=9;e.x=1700;e.y=1500;P.x=2100;P.y=1650;__go('bones');for(let i=0;i<30*1.1;i++){P.inv=9;__tk()}}""")
        await pg.screenshot(path=B + 'whl_bones.png')
        R['kill'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};e.tele=[];e.hp=1;G.hurtEnemy(e,99999,0,0,0);for(let i=0;i<60;i++){P.hp=P.max;P.inv=9;__tk()}o.boss=!!G.boss;o.death=!!G.WHW.death;o.dex=G.SAVE.dex.kills.boss20;o.ach=(G.SAVE.ach&&G.SAVE.ach.done&&G.SAVE.ach.done.k_whl)||null;return o}""")
        await pg.wait_for_timeout(300); await pg.screenshot(path=B + 'whl_death.png')
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('ERRS', errs[:5])
        await b.close()
asyncio.run(main())
