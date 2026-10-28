"""v9.02 팔한지옥의 백곰 마왕 (지하 21층 100% · 22층 70%)
 확률 · 빙결 투기장 · 패턴 순환 · 얼음 장벽(이동·투사체 차단) · 눈보라(바람·동상·바람 그늘·빙결) · 균열(점-선분 거리, 0.5초 안에 비켜나기) ·
 2페이즈 핀볼 반사 돌진(광장 안에 머무름) · 규칙 9 · 처치·도감 · 스크린샷 + 같은 버전의 다른 수정(총잡이 · 듀라한 · 사슬 · 키메라)"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.ifloor',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};const cnt=t=>{const c={};for(let i=0;i<4000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1}return Math.round((c.bear||0)/40)};
          o.p21=cnt(20);o.p22=cnt(21);o.p23=cnt(22);
          G.SAVE.diff.max=21;G.SAVE.diff.sel=20;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;o.tier=P.tier;o.bossK=P.bossK;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);"""+STEP+"""const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.ice=!!(G.arena&&G.arena.ice);o.inPoly=[Math.round(P.x),Math.round(P.y)];
          const seen={},sts=[];let last='';
          for(let i=0;i<30*80;i++){P.hp=P.max;P.inv=1;bo.hp=Math.max(bo.max*0.6,Math.min(bo.hp,bo.max*0.95));G.tick(1/30);"""+STEP+"""const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');return o}""")
        print('A',json.dumps(R,ensure_ascii=False))
        # 장벽: 가두기 · 이동 차단 · 투사체 소멸
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;const AI=G.pb;for(const k in AI.cd)AI.cd[k]=99;G.PBW.bz=null;G.PBW.fis=[];G.PBW.spears=[];e.tele=[];
          P.x=G.IMAP.cx;P.y=G.IMAP.cy;e.x=P.x+700;e.y=P.y-300;e.st='chase';e.stT=99;AI.wq=AI.wallSpots();AI.wallRise();o.walls=G.PBW.walls.length;
          for(let i=0;i<10;i++)G.tick(1/30);
          const esc=(k)=>{P.x=G.IMAP.cx;P.y=G.IMAP.cy;for(const w of G.PBW.walls)w.t=0.5;G.keys.add(k);for(let i=0;i<60;i++){P.hp=P.max;P.inv=1;G.tick(1/30);}G.keys.delete(k);return Math.round(Math.hypot(P.x-G.IMAP.cx,P.y-G.IMAP.cy))};
          {const w0=G.PBW.walls[0];const sh={x:P.x+60,y:P.y-22,vx:900,vy:0,life:1,pierce:1,hit:new Set(),dmg:10};G.shards.push(sh);let gone=-1;for(let i=0;i<20;i++){G.tick(1/30);if(!G.shards.includes(sh)){gone=i;break}}o.shotGone=gone;o.shotX=Math.round(sh.x-P.x);}
          o.escD=esc('KeyD');o.escW=esc('KeyW');o.escS=esc('KeyS');o.escA=esc('KeyA');
          // 대각선 (가장 틈이 있을 법한 곳)
          P.x=G.IMAP.cx;P.y=G.IMAP.cy;for(const w of G.PBW.walls)w.t=0.5;G.keys.add('KeyD');G.keys.add('KeyS');for(let i=0;i<60;i++){P.inv=1;G.tick(1/30);}G.keys.delete('KeyD');G.keys.delete('KeyS');o.escDS=Math.round(Math.hypot(P.x-G.IMAP.cx,P.y-G.IMAP.cy));for(const k2 of [['KeyA','KeyW'],['KeyA','KeyS'],['KeyD','KeyW']]){P.x=G.IMAP.cx;P.y=G.IMAP.cy;for(const w of G.PBW.walls)w.t=0.5;k2.forEach(k=>G.keys.add(k));for(let i=0;i<60;i++){P.inv=1;G.tick(1/30);}k2.forEach(k=>G.keys.delete(k));o['esc'+k2.join('')]=Math.round(Math.hypot(P.x-G.IMAP.cx,P.y-G.IMAP.cy))}
          o.wallsLeft=G.PBW.walls.length;AI.wq=AI.wallSpots();AI.wallRise();for(let i=0;i<8;i++)G.tick(1/30);
          P.x=G.IMAP.cx;P.y=G.IMAP.cy;G.render();return o}""")
        print('W',json.dumps(R,ensure_ascii=False))
        await pg.screenshot(path=B+'bear_wall.png')
        # 눈보라: 바람에 밀림 · 동상 · 바람 그늘 · 빙결(이동 불가 1.5초)
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.pb;G.PBW.walls=[];e.tele=[];G.PBW.fis=[];
          P.x=G.IMAP.cx;P.y=G.IMAP.cy;e.x=P.x-900;e.y=P.y-200;G.PBW.frost=0;G.PBW.frzImm=0;G.PBW.bz={t:0,ux:1,uy:0,shade:false};
          let x0=P.x;for(let i=0;i<30;i++){P.hp=P.max;P.inv=1;G.tick(1/30);}o.push1s=Math.round(P.x-x0);o.frost1s=Math.round(G.PBW.frost);
          // 바람을 거슬러 걸으면 앞으로 간다 (가장 느린 이속 150 기준)
          const s0=P.spd;P.spd=150;x0=P.x;G.keys.add('KeyA');for(let i=0;i<30;i++){P.inv=1;G.tick(1/30);}G.keys.delete('KeyA');o.against=Math.round(P.x-x0);P.spd=s0;
          // 바람 그늘: 바람이 불어오는 쪽(왼쪽)에 장벽
          G.PBW.frost=0;G.PBW.bz.t=0;G.PBW.walls=[new G.IceWall(P.x-110,P.y,80,160,9,false)];G.PBW.walls[0].t=1;x0=P.x;for(let i=0;i<30;i++){P.inv=1;G.tick(1/30);}o.shadePush=Math.round(P.x-x0);o.shadeFrost=Math.round(G.PBW.frost);o.shade=G.PBW.bz&&G.PBW.bz.shade;
          G.PBW.walls=[];G.PBW.bz.t=0;G.PBW.frost=95;for(let i=0;i<12;i++){P.inv=1;G.tick(1/30);}o.frz=+(P.frzT||0).toFixed(2);
          x0=P.x;const y0=P.y;G.keys.add('KeyS');for(let i=0;i<20;i++){P.inv=1;G.tick(1/30);}o.frozenMoveY=Math.round(P.y-y0);o.stillFrz=P.frzT>0;for(let i=0;i<40;i++){P.inv=1;G.tick(1/30);}G.keys.delete('KeyS');o.afterMoveY=Math.round(P.y-y0);o.imm=+G.PBW.frzImm.toFixed(1);
          G.PBW.frost=40;G.PBW.bz={t:1,ux:0.7071,uy:0.7071,shade:false};P.frzT=0;G.render();return o}""")
        print('Z',json.dumps(R,ensure_ascii=False))
        await pg.screenshot(path=B+'bear_blizzard.png')
        # 균열: 점-선분 거리 판정 · 0.5초 안에 옆으로 비키면 안 맞음
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.pb;G.PBW.bz=null;G.PBW.frost=0;G.PBW.walls=[];for(const k in AI.cd)AI.cd[k]=99;e.st='chase';e.stT=99;
          o.sd=[G.segDist(0,10,-5,0,5,0),G.segDist(10,0,0,0,5,0),G.segDist(3,4,0,0,0,0)];
          const run=(mv)=>{P.x=G.IMAP.cx;P.y=G.IMAP.cy+100;e.x=P.x-600;e.y=P.y;e.face=1;G.PBW.fis=[];G.PBW.fsHit=false;
            const f=new G.Fissure(e.x+70,e.y+10,Math.atan2(P.y-(e.y+10),P.x-(e.x+70)),0);G.PBW.fis=[f];const s0=P.spd;P.spd=150;if(mv)G.keys.add('KeyS');let hit=0;
            for(let i=0;i<24;i++){const hb=P.hp;P.inv=0;P.dodge=0;P.shield=0;P.guardT=99;G.tick(1/30);if(P.hp<hb-0.5)hit++;P.hp=P.max}G.keys.delete('KeyS');P.spd=s0;return hit};
          o.stand=run(false);o.dodge=run(true);
          AI.fissures();o.nLines=G.PBW.fis.length;let mn=9;const A=G.PBW.fis.map(f=>f.ang);for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){let d=Math.abs(A[i]-A[j])%6.283;d=Math.min(d,6.283-d);mn=Math.min(mn,d)}o.minGap=+mn.toFixed(2);
          G.tick(1/30);G.tick(1/30);G.tick(1/30);G.tick(1/30);G.render();return o}""")
        print('F',json.dumps(R,ensure_ascii=False))
        await pg.screenshot(path=B+'bear_fissure.png')
        # 2페이즈: 핀볼 반사 돌진
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.pb;G.PBW.fis=[];e.tele=[];e.hp=e.max*0.29;for(let i=0;i<30*3;i++){P.hp=P.max;P.inv=1;G.tick(1/30);"""+STEP+"""}
          o.ph2=e.ph2;o.cyc=AI.cyc.join(',');for(const k in AI.cd)AI.cd[k]=99;G.PBW.bz=null;P.x=G.IMAP.cx+500;P.y=G.IMAP.cy+300;e.x=G.IMAP.cx-300;e.y=G.IMAP.cy-200;
          AI.wq=AI.wallSpots();AI.wallRise();o.bumpers=G.PBW.walls.length;AI.pinAim();let maxN=0,out=0,dash=0,diz=0;
          for(let i=0;i<30*6;i++){P.hp=P.max;P.inv=1;G.tick(1/30);"""+STEP+"""if(AI.pb)maxN=Math.max(maxN,AI.pb.n);if(e.st==='pbDash')dash++;if(!G.IMAP||e.x<G.IMAP.X0||e.x>G.IMAP.X1||e.y<G.IMAP.Y0||e.y>G.IMAP.Y1)out++;
            if(i===40){G.render();window.__shot=1}}
          o.bounces=maxN;o.dashF=dash;o.dizzyF=diz;o.outF=out;o.exPause=G.pbExPause(e);return o}""")
        print('P',json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.pb;for(const k in AI.cd)AI.cd[k]=99;P.x=G.IMAP.cx+300;P.y=G.IMAP.cy+250;e.x=G.IMAP.cx-200;e.y=G.IMAP.cy-100;AI.pinAim();for(let i=0;i<18;i++){P.hp=P.max;P.inv=1;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=B+'bear_pinball.png')
        # 처치 · 도감
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;e.invul=false;e.st='chase';e.hp=1;G.hurtEnemy(e,99999,0,0,0);for(let i=0;i<30*2;i++){P.inv=1;G.tick(1/30);"""+STEP+"""}
          o.dead=!G.boss;o.kills=G.SAVE.dex.kills.boss14||0;o.walls=G.PBW.walls.length;return o}""")
        print('K',json.dumps(R,ensure_ascii=False))
        # 같은 버전의 다른 수정
        R=await pg.evaluate("""()=>{const G=__G,o={};
          G.startGame('gun');let P=G.P;__lv(21);o.roll=G.ROLL.n;G.gunLoad();o.mag=P.mag.length;P.up.gEmber=3;P.syn.gEmberMag=true;let none=0;for(let i=0;i<300;i++){G.gunLoad();if(!P.mag.includes('F'))none++}o.noEmber=none;
          G.startGame('ghost');P=G.P;window.__rt=1;__lv(21);window.__rt=1;o.route=P.route;o.form=P.form;G.castLostHead();const h=G.lhead;o.headLife=h&&h.life;o.hasHurt=!!(h&&h.hurt);o.dm=G.KN.lh.dm;
          G.startGame('chimera');P=G.P;window.__rt=0;__lv(21);o.chim=[P.route,P.form,+P.dmg.toFixed(1)];
          return o}""")
        print('X',json.dumps(R,ensure_ascii=False))
        print('errs',pg.errs[:5])
        await b.close()
asyncio.run(main())
