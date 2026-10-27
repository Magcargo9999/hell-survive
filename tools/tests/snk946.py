"""v9.46 불구렁이 (지하 28층 100% · 29층 70% · 30층 균등 · 팔열지옥 보스방 = 마왕성)
 확률 · 순환 · 다관절 몸(마디 대리 히트박스 → 마왕에게 50%) · 파열하는 대지(균열 → 참호 벽 · 돌출 반경 = 피할 수 있는 크기) ·
 탐욕의 용광로(흡입 · 구슬 삼킴 → 화구 수) · 불길의 환영 포위(못 나감 · 투사체 반사 상한 · 머리 5번 = 파훼) · 30% 종말의 똬리(가둠 · 최소 크기 · 20초 뒤 풀림) · 처치 · 업적 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/snk946.py   (스크린샷 build/snk_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
STEP = "if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:200]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','fmap'])", timeout=120000, polling=1000)   # v9.72 보스방 그림(LAZY)이 와야 enterArena가 바로 열린다
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1};window.__tk=()=>{const G=__G;if(G.P)G.P.heat=0;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};window.__free=()=>{const AI=__G.sn;for(const k in AI.cd)AI.cd[k]=99}}")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.t27=cnt(27,'snk');o.t28=cnt(28,'snk');o.t29=cnt(29,'snk');o.t26=cnt(26,'snk');o.t25=cnt(25,'snk');
          G.SAVE.diff.max=24;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=27;P.fset='fire';P.bossK='snk';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);const H=G.snHall();o.hall=[Math.round(H.cx),Math.round(H.cy),Math.round(H.rx),Math.round(H.ry),H.cells.length];
          const seen={},sts=[];let last='',maxC=0,out=0,px=0;
          for(let i=0;i<30*120;i++){P.hp=P.max;P.inv=1;bo.hp=Math.max(bo.max*0.6,Math.min(bo.hp,bo.max*0.95));__tk();const e=G.boss;if(!e)break;maxC=Math.max(maxC,G.SNW.cracks.length);px=Math.max(px,G.enemies.filter(q=>q.kind==='snb').length);if(!e.under&&!G.inPoly(e.x,e.y))out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,30).join('>');o.maxCracks=maxC;o.bossOut=out;o.proxies=px;o.pIn=G.inPoly(P.x,P.y);return o}""")
        # 다관절: 마디를 때리면 마왕에게 50% (한 프레임에 한 번) · 마디에 닿으면 피해
        R['body'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.sn;__free();G.SNW.cracks=[];G.SNW.ring=null;G.SNW.suck=null;e.tele=[];AI.chase(99);e.x=900;e.y=800;e.face=1;P.x=1300;P.y=1000;
          for(let i=0;i<30;i++){e.x=900+i;__tk();P.inv=1}const px=G.enemies.filter(q=>q.kind==='snb'&&!q.invul);o.n=px.length;const q=px[px.length-1];
          o.tailD=Math.round(Math.hypot(q.x-e.x,q.y-e.y));const h0=e.hp;G.hurtEnemy(q,1000,0,0,0);o.fwd=Math.round(h0-e.hp);const h1=e.hp;G.hurtEnemy(px[0],1000,0,0,0);o.sameFrame=Math.round(h1-e.hp);
          __tk();const h2=e.hp;G.hurtEnemy(px[2],1000,0,0,0);o.nextFrame=Math.round(h2-e.hp);
          AI.go('stun',99,'hit');__tk();const n=G.SNW.nodes[5];__cl();P.hp=P.max;AI.bump=0;P.x=n.x;P.y=n.y;__tk();o.touch=Math.round(P.max-P.hp);return o}""")
        # 파열하는 대지: 균열 → 굳으면 참호(벽) · 참호를 넘지 못함 · 돌출 반경은 피할 수 있는 만큼 · 서 있으면 맞음
        R['burrow'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.sn;__free();e.tele=[];G.SNW.balls=[];G.orbs.length=0;e.x=820;e.y=820;P.x=1100;P.y=900;__cl();P.hp=P.max;
          AI.dig('tunnel');let warnSeen=0,hard=0,R0=0;const sts=[];let last='';
          for(let i=0;i<30*12;i++){P.inv=1;P.hp=P.max;__tk();if(e.st!==last){last=e.st;sts.push(e.st)}warnSeen=Math.max(warnSeen,G.SNW.cracks.filter(c=>!c.hard).length);hard=Math.max(hard,G.SNW.cracks.filter(c=>c.hard).length);
            if(e.st==='lurk'&&AI.fired&&!R0){R0=AI.emR;o.esc=Math.round(G.snEscapeR(AI.emX,AI.emY,G.SN.emWarn-G.SN.emAim))}if(e.st==='emerge'&&o.orbs===undefined){o.orbs=G.orbs.length}if(e.st==='chase')break}
          o.seq=sts.join('>');o.warn=warnSeen;o.hard=hard;o.emR=Math.round(R0);
          // 참호 벽 통과 시도: 굳은 참호 하나를 가로질러 걸어 본다
          const c=G.SNW.cracks.find(c=>c.hard);if(c){const mx=(c.ax+c.bx)/2,my=(c.ay+c.by)/2,vx=c.bx-c.ax,vy=c.by-c.ay,l=Math.hypot(vx,vy),nx=-vy/l,ny=vx/l;
            P.x=mx+nx*60;P.y=my+ny*60;const side0=Math.sign((P.x-mx)*nx+(P.y-my)*ny);G.keys.clear();const kx=-nx,ky=-ny;if(kx>0.3)G.keys.add('KeyD');if(kx<-0.3)G.keys.add('KeyA');if(ky>0.3)G.keys.add('KeyS');if(ky<-0.3)G.keys.add('KeyW');
            let md=1e9;for(let i=0;i<45;i++){P.inv=1;P.hp=P.max;__tk();for(const q of G.SNW.cracks)if(q.hard&&q.life>0.3)md=Math.min(md,G.segDist?G.segDist(P.x,P.y,q.ax,q.ay,q.bx,q.by):1e9)}o.minWallD=Math.round(md);G.keys.clear();o.crossed=Math.sign((P.x-mx)*nx+(P.y-my)*ny)!==side0;o.wallD=Math.round(G.SNW.cracks.filter(c=>c.hard).reduce((m,c)=>Math.min(m,Math.hypot(P.x-(c.ax+c.bx)/2,P.y-(c.ay+c.by)/2)),1e9))}
          // 서 있으면 맞고, 고정되자마자 피할 수 있는 곳으로 가면 안 맞는다
          const run=(dodge)=>{G.SNW.cracks=[];e.tele=[];e.x=820;e.y=820;P.x=1100;P.y=900;AI.dig('tunnel');__cl();P.hp=P.max;let got=false;
            for(let i=0;i<30*12;i++){if(e.st==='lurk'&&AI.fired&&dodge&&!got){got=true;const a=Math.atan2(P.y-AI.emY,P.x-AI.emX)||0;let best=null;for(let k=0;k<16;k++){const b=a+k*0.39,tx=AI.emX+Math.cos(b)*(AI.emR+40),ty=AI.emY+Math.sin(b)*(AI.emR+40)*0.62;if(G.inPoly(tx,ty)){best=[tx,ty];break}}if(best){P.x=best[0];P.y=best[1]}}
              if(e.st!=='lurk')P.inv=1;__tk();if(e.st==='lurk')P.inv=0;if(e.st==='emerge'||e.st==='chase')break}return Math.round(P.max-P.hp)};
          o.stand=run(false);o.dodge=run(true);return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn;__free();e.tele=[];e.x=820;e.y=820;P.x=1100;P.y=900;AI.dig('tunnel');for(let i=0;i<30*3.2;i++){P.inv=1;P.hp=P.max;__tk();if(e.st==='lurk')break}for(let i=0;i<18;i++){P.inv=1;__tk()}G.render&&G.render()}""")
        await pg.screenshot(path=B + 'snk_burrow.png')
        # 탐욕의 용광로: 부채꼴 안이면 끌려감 · 걸으면 빠져나감 · 내 자석 밖 구슬은 삼킴 → 화구 수
        R['devour'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.sn;__free();G.SNW.cracks=[];e.tele=[];G.SNW.balls=[];AI.chase(99);e.x=760;e.y=820;e.face=1;P.x=1150;P.y=820;
          G.orbs.length=0;for(let i=0;i<9;i++)G.orbs.push({x:500+i*40,y:1000,val:3,t:0});G.orbs.push({x:P.x+20,y:P.y,val:3,t:0});const pk=P.pickup;P.pickup=60;
          AI.cd.devour=0;AI.ci=AI.cyc.indexOf('devour');AI.next();o.st=e.st;let d0=0;
          for(let i=0;i<30*0.9;i++){P.inv=1;P.hp=P.max;__tk()}d0=Math.hypot(P.x-e.x,P.y-e.y);
          for(let i=0;i<30*1.0;i++){P.inv=1;P.hp=P.max;__tk()}o.pulled=Math.round(d0-Math.hypot(P.x-e.x,P.y-e.y));
          G.keys.clear();G.keys.add('KeyS');const y0=P.y;for(let i=0;i<30*1.2;i++){P.inv=1;P.hp=P.max;__tk()}G.keys.clear();o.walkOut=Math.round(P.y-y0);
          for(let i=0;i<30*3;i++){P.inv=1;P.hp=P.max;__tk();if(e.st==='spit')break}o.ate=G.SNW.ate;o.spitN=AI.spitN;o.balls=G.SNW.balls.length;P.pickup=pk;
          // 화구 사이 틈: 첫 파도 구체 간 최소 간격(거리 260에서)
          const B2=G.SNW.balls.map(b=>Math.atan2(b.vy/0.8,b.vx)).sort((a,b)=>a-b);let mg=9;for(let i=1;i<B2.length;i++)mg=Math.min(mg,B2[i]-B2[i-1]);o.gapAt260=Math.round(mg*260-2*G.SN.fbR);return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn;__free();G.SNW.balls=[];AI.chase(99);e.x=760;e.y=820;e.face=1;P.x=1150;P.y=860;G.orbs.length=0;for(let i=0;i<8;i++)G.orbs.push({x:1000+i*30,y:1000,val:3,t:0});AI.cd.devour=0;AI.ci=AI.cyc.indexOf('devour');AI.next();for(let i=0;i<30*1.4;i++){P.inv=1;P.hp=P.max;__tk()}G.render&&G.render()}""")
        await pg.screenshot(path=B + 'snk_devour.png')
        # 불길의 환영 포위: 못 나감 · 투사체 반사(상한 15%) · 머리 5번 → 휘청
        R['ring'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.sn;__free();G.SNW.balls=[];G.SNW.cracks=[];e.tele=[];AI.chase(99);e.x=760;e.y=820;P.x=1000;P.y=860;
          AI.dig('ring');for(let i=0;i<30*2.2;i++){P.inv=1;P.hp=P.max;__tk()}const R=G.SNW.ring;o.ph=R&&R.ph;o.st=e.st;
          G.keys.clear();G.keys.add('KeyD');for(let i=0;i<30*3;i++){P.inv=1;P.hp=P.max;__tk()}G.keys.clear();o.inside=!G.SNW.ring?'gone':Math.round(Math.hypot(P.x-R.x,(P.y-R.y)/0.62))<=Math.round(R.r);o.r=Math.round(R.r);
          // 반사: 바깥으로 나가는 투사체를 여러 개
          __cl();P.hp=P.max;G.SNW.rfSum=0;for(let k=0;k<30;k++){G.shards.push({x:P.x,y:P.y-26,vx:900,vy:0,life:2,pierce:1,hit:new Set(),dmg:P.dmg});for(let i=0;i<6;i++){__tk();P.inv=0}}
          for(let i=0;i<60;i++){__tk();P.inv=0}o.reflPct=+((P.max-P.hp)/P.max*100).toFixed(1);o.rfSumPct=+(G.SNW.rfSum/P.max*100).toFixed(1);G.SNW.ring=null;G.SNW.hd=null;e.tele=[];AI.chase(99);__tk();AI.dig('ring');
          // 머리 5번
          let broke=false;for(let i=0;i<30*8&&!broke;i++){P.hp=P.max;P.inv=1;__tk();if(e.st==='enHead'){P.x=e.x+80;P.y=e.y;G.hurtEnemy(e,10,0,0,0)}if(e.st==='stun')broke=true}o.broke=broke;o.ringGone=!G.SNW.ring;return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn;__free();AI.chase(99);e.x=760;e.y=820;P.x=1000;P.y=860;AI.dig('ring');for(let i=0;i<30*3.4;i++){P.inv=1;P.hp=P.max;__tk();if(e.st==='enHead')break}G.render&&G.render()}""")
        await pg.screenshot(path=B + 'snk_ring.png')
        # 30% 종말의 똬리
        R['coil'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.sn;G.SNW.ring=null;G.SNW.hd=null;e.tele=[];AI.chase(0.5);e.hp=e.max*0.29;
          for(let i=0;i<3;i++){P.hp=P.max;P.inv=1;__tk()}o.st=e.st;o.ph2=e.ph2;
          for(let i=0;i<30*4.2;i++){P.hp=P.max;P.inv=1;__tk()}const C=G.SNW.coil;o.coil=!!C&&C.closed;o.st2=e.st;o.nodes=G.SNW.nodes.length;
          G.keys.clear();G.keys.add('KeyD');G.keys.add('KeyS');for(let i=0;i<30*2;i++){P.hp=P.max;P.inv=1;__tk()}G.keys.clear();
          o.pIn=G.inPoly(P.x,P.y);o.q=+(Math.hypot((P.x-C.cx)/(C.rx*C.k),(P.y-C.cy)/(C.ry*C.k))).toFixed(2);
          const px=G.enemies.filter(q=>q.kind==='snb'&&!q.invul);o.px=px.length;__tk();const h0=e.hp;G.hurtEnemy(px[3],1000,0,0,0);o.fwd=Math.round(h0-e.hp);
          let mink=1,hits=0,tries=0;for(let i=0;i<30*18;i++){P.hp=P.max;P.inv=1;e.hp=Math.max(e.hp,e.max*0.2);__tk();if(G.SNW.coil)mink=Math.min(mink,G.SNW.coil.k);}
          o.minK=+mink.toFixed(2);const C2={rx:G.snHall().rx,ry:G.snHall().ry,k:G.SN.coMin};o.minRx=Math.round(C2.rx*C2.k-G.SN.coR);o.minRy=Math.round(C2.ry*C2.k-G.SN.coR*0.7);
          // 기둥: 예고가 뜬 뒤 그 자리를 벗어나면 안 맞는다
          for(let i=0;i<30*4;i++){P.hp=P.max;P.inv=1;e.hp=Math.max(e.hp,e.max*0.2);__tk()}o.released=!G.SNW.coil;o.st3=e.st;return o}""")
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.sn;AI.cd.coil=0;AI.chase(0.1);for(let i=0;i<30*3;i++){P.hp=P.max;P.inv=1;e.hp=Math.max(e.hp,e.max*0.2);__tk()}G.render&&G.render()}""")
        await pg.screenshot(path=B + 'snk_coil.png')
        R['X'] = await ev(pg, """()=>{const G=__G,P=G.P,o={},e=G.boss;delete G.SAVE.ach.done.k_snk;const k0=G.SAVE.dex.kills.boss18|0;P.inv=1;e.invul=false;e.under=false;G.hurtEnemy(e,e.max*5,0,0,0);
          for(let i=0;i<60;i++){P.hp=P.max;__tk();}o.dead=!G.boss||G.boss.hp<=0;o.kills=(G.SAVE.dex.kills.boss18|0)-k0;G.achSync&&G.achSync();o.ach=!!G.SAVE.ach.done.k_snk;
          o.left=G.enemies.filter(q=>q.kind==='snb').length+G.SNW.cracks.length+(G.SNW.coil?1:0)+(G.SNW.ring?1:0);o.death=!!G.SNW.death;return o}""")
        await pg.evaluate("()=>{__G.render&&__G.render()}"); await pg.screenshot(path=B + 'snk_death.png')
        R['errs'] = errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
