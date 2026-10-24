"""v8.80 타락한 어인왕(20층 전용) · 업적
 확률(20층 100%) · 패턴 순환 · 산소 게이지/간헐천 · 물거울 반사 · 사슬(반경 밖 = 체력 절반) · 파도 고리(안전 원) · 2페이즈 빙판·해일 서핑 · 처치·도감 · 업적 달성/보상 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        await pg.wait_for_function('__G.IMG.kng&&__G.IMG.smap',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};const cnt=t=>{const c={};for(let i=0;i<4000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1}return Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/40)]))};
          o.p18=cnt(17);o.p19=cnt(18);o.p20=cnt(19);
          G.SAVE.diff.max=19;G.SAVE.diff.sel=19;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;o.bossK=P.bossK;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);"""+STEP+"""const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.sea=!!(G.arena&&G.arena.sea);o.mirrors=G.KGW.mirrors.length;o.gy0=G.KGW.geysers.length;
          const seen={tether:0,blades:0,pillars:0,ring:0,charge:0,slam:0,dash:0},sts=[];let last='',o2min=100,gyMax=0,teth=0;
          for(let i=0;i<30*90;i++){P.hp=P.max;P.o2=Math.max(P.o2,30);bo.hp=Math.min(bo.hp,bo.max*0.95);G.tick(1/30);"""+STEP+"""const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;if(seen[e.st]!==undefined)seen[e.st]++;sts.push(e.st)}
            o2min=Math.min(o2min,P.o2);gyMax=Math.max(gyMax,G.KGW.geysers.length);if(G.KGW.tether)teth=1}
          o.seen=seen;o.seq=sts.slice(0,22).join('>');o.gyMax=gyMax;o.tetherOn=teth;
          // 산소: 0이면 1초에 최대 체력 약 10%
          G.KGW.tether=null;G.KGW.ring=null;for(const k in G.kg.cd)G.kg.cd[k]=99;bo.st='chase';bo.stT=99;bo.tele=[];G.KGW.geysers=[];
          P.o2=0;P.hp=P.max;P.inv=9;const h0=P.hp;for(let i=0;i<30;i++){G.KGW.geysers=[];G.tick(1/30);}o.o2loss=+((h0-P.hp)/P.max*100).toFixed(1);
          // 간헐천: 위에 서 있으면 산소가 찬다
          P.hp=P.max;P.o2=10;const g=new G.AirGeyser(P.x,P.y);G.KGW.geysers=[g];for(let i=0;i<30;i++)G.tick(1/30);o.o2fill=Math.round(P.o2);
          // 사슬: 반경 밖으로 나가면 지금 체력의 절반
          P.hp=P.max*0.8;P.o2=100;G.KGW.tether={x:P.x,y:P.y,t:0,life:7};P.x+=G.KG.teR+30;const hb=P.hp;G.tick(1/30);o.snap=+(P.hp/hb).toFixed(2);o.tetherGone=!G.KGW.tether;
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        # 물거울 반사
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;P.inv=0;P.shield=0;const m=G.KGW.mirrors[0];m.down=0;m.hits=0;G.shards=[];G.KGW.bolts=[];
          const sh={x:m.x-30,y:m.y,vx:600,vy:0,life:1,pierce:1,hit:new Set(),dmg:P.dmg};G.shards.push(sh);const n0=G.shards.length;G.tick(1/30);
          o.bolts=G.KGW.bolts.length;o.shardGone=!G.shards.includes(sh);const bt=G.KGW.bolts[0];if(bt){o.towardMe=(bt.vx*(P.x-bt.x)+bt.vy*(P.y-30-bt.y))>0}
          // 5번 튕기면 거울이 깨진다
          for(let i=0;i<6;i++){G.shards.push({x:m.x-30,y:m.y,vx:600,vy:0,life:1,pierce:1,hit:new Set(),dmg:P.dmg});G.tick(1/30)}o.mirrorDown=!m.on;
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;for(const k in G.kg.cd)G.kg.cd[k]=99;G.kg.cd.tether=0;G.kg.ci=0;e.st='chase';e.stT=0;G.KGW.bolts=[];P.x=e.x+260;P.y=e.y+220;
          for(let i=0;i<70;i++){P.hp=P.max;G.tick(1/30);}P.o2=55;G.render()}"""); await pg.screenshot(path=B+'kng_p1.png')
        # 파도 고리: 안전 원 안이면 안 맞고, 바깥에서 가만히 있으면 맞는다
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;
          const test=(r)=>{G.KGW.tether=null;for(const k in G.kg.cd)G.kg.cd[k]=99;e.tele=[];G.kg.ringStart();e.st='ring';e.stT=0.3;P.x=e.x+r;P.y=e.y;let hits=0;
            for(let i=0;i<30*7.5;i++){const hb=P.hp;P.inv=0;P.o2=100;P.dodge=0;P.guardT=99;P.shield=0;G.KGW.bolts=[];G.shards=[];G.tick(1/30);"""+STEP+"""P.x=e.x+r;P.y=e.y;if(P.hp<hb-1)hits++;P.hp=P.max}return hits};
          o.safe=test(120);o.mid=test(500);o.after=e.st;
          // 가장 느린 이속(리자드 기준 150)으로 바깥(r=800)에서 안쪽으로 달리면 산다 — 계산
          const sp=150;let r=980,ok=true;for(let t=0;t<6;t+=1/60){r=Math.max(100,r-sp/60);for(let k=0;k<7;k++){const te=G.KG.riWarn+k*G.KG.riStep;if(Math.abs(t-te)<1/120){const ro=G.KG.riOut-k*G.KG.riBand,ri=Math.max(G.KG.riSafe,ro-G.KG.riBand);if(r<ro&&r>ri)ok=false}}}o.slowRunOk=ok;
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;for(const k in G.kg.cd)G.kg.cd[k]=99;G.kg.ringStart();e.st='ring';P.x=e.x+330;P.y=e.y+80;for(let i=0;i<30*2.4;i++){P.hp=P.max;P.inv=1;P.o2=100;G.tick(1/30);}G.render()}"""); await pg.screenshot(path=B+'kng_ring.png')
        # 2페이즈: 빙판(키를 떼도 미끄러짐) · 해일 서핑
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;G.KGW.ring=null;e.hp=e.max*0.29;for(let i=0;i<30*3.2;i++){P.hp=P.max;P.o2=100;G.tick(1/30);"""+STEP+"""}
          o.ph2=e.ph2;o.ice=G.kgIce();o.cyc=G.kg.cyc.join(',');o.mirrors=G.KGW.mirrors.length;
          for(const k in G.kg.cd)G.kg.cd[k]=99;e.st='chase';e.stT=99;e.tele=[];P.x=1800;P.y=1980;P.svx=0;P.svy=0;e.x=P.x+700;
          G.keys.add('KeyD');for(let i=0;i<30;i++){P.inv=1;G.tick(1/30);"""+STEP+"""}o.st=G.state;o.dbg=[P.stunT,P.bindT,P.charmT,+(P.svx||0).toFixed(1),Math.round(P.x),P.slowT];G.keys.delete('KeyD');const x0=P.x;for(let i=0;i<15;i++){P.inv=1;G.tick(1/30);"""+STEP+"""}o.slide=Math.round(P.x-x0);
          // 규칙 9: 멈춰 있다가 예고(1.1초) 동안 옆으로 비키면 얼마나 가나
          P.svx=0;P.svy=0;const y0=P.y;G.keys.add('KeyS');for(let i=0;i<33;i++){P.inv=1;G.tick(1/30);"""+STEP+"""}G.keys.delete('KeyS');o.side=Math.round(P.y-y0);o.need=G.KG.suW/2+12+9;o.spd=Math.round(P.spd);
          let surf=0,dash=0;G.kg.cd.surf=0;G.kg.ci=0;e.stT=0;for(let i=0;i<30*12;i++){P.hp=P.max;P.inv=0;P.o2=100;G.tick(1/30);"""+STEP+"""if(e.st==='surfW')surf++;if(e.st==='surfD')dash++;}o.surfW=surf;o.surfD=dash;
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss;for(const k in G.kg.cd)G.kg.cd[k]=99;G.kg.cd.surf=0;G.kg.ci=0;e.st='chase';e.stT=0;for(let i=0;i<300;i++){P.hp=P.max;P.inv=1;P.o2=100;G.tick(1/30);if(e.st==='surfW'&&e.anT>0.5)break}"""+STEP+"""G.render()}"""); await pg.screenshot(path=B+'kng_p2.png')
        R=await pg.evaluate("""()=>{const G=__G,e=G.boss,P=G.P;G.SAVE.ach={done:{},got:{}};G.hurtEnemy(e,e.hp+10,0,0,0,false);for(let i=0;i<60;i++){G.tick(1/30);"""+STEP+"""}
          return {boss:!!G.boss,dex:G.SAVE.dex.kills.boss12,ach:G.SAVE.ach.done,mirrors:G.KGW.mirrors.length,ice:G.kgIce(),death:!!G.KGW.death,msg:P.dropMsg,heart:G.bhKey({bk:'kng'})}}""")
        print(json.dumps(R,ensure_ascii=False))
        # 업적 화면: 예전 기록 인정 + 보상
        await pg.evaluate("""()=>{const G=__G;G.SAVE.ach={done:{},got:{}};G.SAVE.diff.max=10;G.SAVE.rush.open=false;G.SAVE.fw.snap=null;G.SAVE.shards=0;G.openAch()}""")
        await pg.screenshot(path=B+'kng_ach.png')
        R=await pg.evaluate("""()=>{const G=__G,o={};o.done=Object.keys(G.SAVE.ach.done).sort().join(',');const bt=[...document.querySelectorAll('#achList button')];o.btns=bt.map(b=>b.textContent).join('|');bt[0].click();o.shards=G.SAVE.shards;o.got=Object.keys(G.SAVE.ach.got).join(',');o.badge=document.getElementById('achBtn').classList.contains('new');return o}""")
        print(json.dumps(R,ensure_ascii=False)); print('errs',pg.errs); await b.close()
asyncio.run(main())
