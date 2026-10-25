"""v9.20 팔한지옥의 대공작 릴세르카 (지하 25층 최종 마왕)
 확률 · 순환 · 결정화 영역(동상 → 동결 감속 · 1.5초 벗어나면 초기화) · 왈츠(정반대 스포트라이트 · 시선) · 거울(3갈래 반사 · 파괴 화이트아웃) ·
 피루엣 · 샹들리에 · 2페이즈 백한의 무도회(마찰 0 · 회전 안전지대 · 방향 전환) · 처치 · 업적 · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.ifloor',timeout=90000)
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0}}")
        R=await pg.evaluate("""()=>{const G=__G,o={};const c={};for(let i=0;i<2000;i++){const q=G.pickBossK(24);c[q]=(c[q]||0)+1}o.p25=c;o.open=G.OPEN_TIER;
          G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;o.tier=P.tier;o.bossK=P.bossK;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);"""+STEP+"""const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);
          const seen={},sts=[];let last='';
          for(let i=0;i<30*90;i++){P.hp=P.max;P.inv=1;P.stunT=0;P.chillT=0;bo.hp=Math.max(bo.max*0.5,Math.min(bo.hp,bo.max*0.95));G.tick(1/30);"""+STEP+"""const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');return o}""")
        print('A',json.dumps(R,ensure_ascii=False))
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.ls;for(const k in AI.cd)AI.cd[k]=99;G.LSW.spot=null;G.LSW.mir.forEach(m=>m.hp=0);G.LSW.bolts=[];G.LSW.chand=[];P.chillT=0;G.LSW.frost=0;
          e.st='glide';e.stT=99;e.x=G.IMAP.cx;e.y=G.IMAP.cy;let t=-1;
          for(let i=0;i<30*5;i++){P.x=e.x+120;P.y=e.y;P.hp=P.max;P.inv=1;G.tick(1/30);if(P.chillT>0&&t<0)t=i/30}o.chillAt=+t.toFixed(2);o.chill=+P.chillT.toFixed(1);
          o.aspd=+(G.aspdE?0:0);const sp0=P.x;G.keys.add('KeyD');for(let i=0;i<15;i++){P.inv=1;G.tick(1/30);}G.keys.delete('KeyD');o.moved=Math.round(P.x-sp0);
          for(let i=0;i<30*3.2;i++){P.x=e.x+600;P.y=e.y;P.inv=1;G.tick(1/30);}o.after=+P.chillT.toFixed(1);o.frostAfter=Math.round(G.LSW.frost);
          for(let i=0;i<30*1;i++){P.x=e.x+120;P.y=e.y;P.inv=1;G.tick(1/30);}o.f1=Math.round(G.LSW.frost);for(let i=0;i<30*1.0;i++){P.x=e.x+600;P.y=e.y;P.inv=1;G.tick(1/30);}o.f2=Math.round(G.LSW.frost);for(let i=0;i<30*0.7;i++){P.x=e.x+600;P.y=e.y;P.inv=1;G.tick(1/30);}o.f3=Math.round(G.LSW.frost);
          G.keys.add('KeyD');const x1=P.x;for(let i=0;i<15;i++){P.inv=1;G.tick(1/30);}G.keys.delete('KeyD');o.movedFree=Math.round(P.x-x1);return o}""")
        print('Z',json.dumps(R,ensure_ascii=False))
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.ls;P.chillT=0;G.LSW.frost=0;P.x=G.IMAP.cx+300;P.y=G.IMAP.cy+200;e.x=G.IMAP.cx;e.y=G.IMAP.cy;
          G.LSW.gazed=false;AI.waltzStart();const S=G.LSW.spot;o.far=Math.round(Math.hypot(e.x-P.x,e.y-P.y));let minSep=1e9,maxV=0,px=S.x,py=S.y,gz=0;
          for(let i=0;i<30*7.5;i++){if(!G.LSW.spot)break;P.x=G.LSW.spot.x;P.y=G.LSW.spot.y;P.hp=P.max;__cl();G.tick(1/30);const T=G.LSW.spot;if(!T)break;minSep=Math.min(minSep,Math.hypot(T.x-e.x,T.y-e.y));maxV=Math.max(maxV,Math.hypot(T.x-px,T.y-py)*30);px=T.x;py=T.y;if(G.LSW.gazed)gz++}
          o.minSep=Math.round(minSep);o.maxV=Math.round(maxV);o.gazedFollow=gz;o.inHall=true;
          // 가만히 서 있으면 시선
          G.LSW.gazed=false;P.chillT=0;AI.waltzStart();const sx=P.x,sy=P.y;let hp0=P.max,dm=0,stun=0;P.hp=P.max;
          for(let i=0;i<30*4;i++){P.x=sx;P.y=sy;__cl();G.tick(1/30);if(P.stunT>0)stun=1}o.gazeDmgPct=Math.round((hp0-P.hp)/P.max*100);o.stun=stun;o.gazed=G.LSW.gazed;
          G.LSW.spot=null;e.st='glide';e.stT=99;return o}""")
        print('W',json.dumps(R,ensure_ascii=False))
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.ls;G.LSW.bolts=[];P.x=G.IMAP.cx+400;P.y=G.IMAP.cy;e.x=G.IMAP.cx-400;e.y=G.IMAP.cy;
          AI.mirrors();const m=G.LSW.mir[0];o.n=G.LSW.mir.length;o.inEn=G.enemies.includes(m);for(let i=0;i<14;i++){P.inv=1;G.tick(1/30);}
          const h0=m.hp,sh={x:m.x+120,y:m.y-m.r,vx:-700,vy:0,life:1,pierce:1,hit:new Set(),dmg:50,arrow:true,sz:1};G.shards.push(sh);let gone=-1;for(let i=0;i<20;i++){P.inv=1;G.tick(1/30);if(!G.shards.includes(sh)){gone=i;break}}
          o.shotGone=gone;o.refl=G.LSW.bolts.filter(b=>b.k==='refl').length;o.mDmg=Math.round(h0-m.hp);
          const k0=G.SAVE.dex.kills.lmir|0;G.hurtEnemy(m,m.max*3,0,0,0);o.white=+G.LSW.white.toFixed(2);o.dex=(G.SAVE.dex.kills.lmir|0)-k0;o.busy=AI.busy();o.ex=G.lsExPause(e);
          for(let i=0;i<40;i++){P.inv=1;G.tick(1/30);}o.white2=G.LSW.white;
          // 피루엣 · 샹들리에
          G.LSW.bolts=[];AI.cd.pirouette=0;AI.ci=AI.cyc.indexOf('pirouette');e.st='glide';e.stT=0;let mx=0;for(let i=0;i<30*3;i++){P.inv=1;P.x=G.IMAP.cx+500;P.y=G.IMAP.cy+300;G.tick(1/30);mx=Math.max(mx,G.LSW.bolts.length)}o.pirBolts=mx;
          G.LSW.bolts=[];P.x=G.IMAP.cx+200;P.y=G.IMAP.cy+250;__cl();P.hp=P.max;AI.chand();o.chN=G.LSW.chand.length;const h1=P.hp;for(let i=0;i<30*1.5;i++){P.x=G.IMAP.cx+200;P.y=G.IMAP.cy+250;G.tick(1/30);}o.chHit=Math.round(h1-P.hp);return o}""")
        print('M',json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.ls;P.hp=P.max;P.chillT=0;G.LSW.bolts=[];P.x=G.IMAP.cx+200;P.y=G.IMAP.cy+250;e.x=G.IMAP.cx-250;e.y=G.IMAP.cy+100;AI.mirrors();AI.chand();G.LSW.frost=65;
          for(let i=0;i<20;i++){P.inv=1;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=B+'lil_p1.png')
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.ls;G.LSW.mir.forEach(m=>m.hp=0);G.LSW.chand=[];e.x=G.IMAP.cx;e.y=G.IMAP.cy-250;P.x=G.IMAP.cx+250;P.y=G.IMAP.cy+80;AI.waltzStart();for(let i=0;i<55;i++){P.inv=1;P.x=G.LSW.spot.x;P.y=G.LSW.spot.y;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=B+'lil_waltz.png')
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;G.LSW.spot=null;e.st='glide';e.stT=1;P.chillT=0;G.LSW.frost=0;
          e.hp=e.max*0.24;P.x=G.IMAP.cx+330;P.y=G.IMAP.cy;for(let i=0;i<4;i++){P.inv=1;G.tick(1/30);}o.st=e.st;o.ph2=e.ph2;
          for(let i=0;i<30*3;i++){P.inv=1;P.hp=P.max;G.tick(1/30);}o.st2=e.st;o.ice=G.lsIce();o.center=[Math.round(e.x-G.IMAP.cx),Math.round(e.y-G.IMAP.cy)];
          // 안전지대를 따라 돌기 (반지름 330) → 피해 없음 (샹들리에 제외)
          G.LSW.chand=[];const B=G.LSW.ball;B.ch=99;__cl();P.hp=P.max;let h=P.hp;for(let i=0;i<30*4;i++){P.x=G.IMAP.cx+Math.cos(B.ang)*330;P.y=G.IMAP.cy+Math.sin(B.ang)*330;P.svx=0;P.svy=0;G.tick(1/30);}o.followDmg=Math.round(h-P.hp);
          o.linV=Math.round(G.LS.omega*330);o.maxR=Math.round(150/G.LS.omega);
          // 밖에 서 있으면 초당 8%
          P.hp=P.max;h=P.hp;for(let i=0;i<30*2;i++){P.x=G.IMAP.cx+Math.cos(B.ang+Math.PI)*330;P.y=G.IMAP.cy+Math.sin(B.ang+Math.PI)*330;P.svx=0;P.svy=0;__cl();G.tick(1/30);}o.outPctPerS=Math.round((h-P.hp)/P.max*100/2);
          // 마찰 0: 키를 떼도 미끄러진다
          P.x=G.IMAP.cx+Math.cos(B.ang)*330;P.y=G.IMAP.cy+Math.sin(B.ang)*330;P.svx=120;P.svy=0;const x0=P.x;for(let i=0;i<30;i++){P.inv=1;G.tick(1/30);}o.slide1s=Math.round(P.x-x0);o.sv=Math.round(P.svx);
          // 방향 전환
          const d0=B.dir;B.revT=0.01;for(let i=0;i<30*2;i++){P.inv=1;G.tick(1/30);}o.rev=[d0,B.dir];o.ex=G.lsExPause(e);
          // 샹들리에는 안전지대 안쪽에
          B.ch=0;G.tick(1/30);o.chInWedge=G.LSW.chand.map(c=>G.lsInWedge(c.x,c.y));return o}""")
        print('B',json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,B=G.LSW.ball;P.x=G.IMAP.cx+Math.cos(B.ang)*330;P.y=G.IMAP.cy+Math.sin(B.ang)*330;P.svx=0;P.svy=0;B.ch=0;for(let i=0;i<20;i++){P.inv=1;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=B+'lil_ball.png')
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;delete G.SAVE.ach.done.h5;delete G.SAVE.ach.done.lil_waltz;G.LSW.gazed=false;const k0=G.SAVE.dex.kills.boss16|0;
          P.inv=1;e.invul=false;G.hurtEnemy(e,e.max*5,0,0,0);for(let i=0;i<60;i++){P.hp=P.max;P.inv=1;G.tick(1/30);}
          o.dead=!G.boss||G.boss.hp<=0;o.kills=(G.SAVE.dex.kills.boss16|0)-k0;o.h5=!!G.SAVE.ach.done.h5;o.waltz=!!G.SAVE.ach.done.lil_waltz;o.clr=G.SAVE.diff.clr;o.ice=G.lsIce();o.chill=P.chillT;
          delete G.SAVE.ach.done.h5;G.achSync();o.h5sync=!!G.SAVE.ach.done.h5;o.ach=G.ACH.map(a=>a.id).slice(0,6).join(',');return o}""")
        print('X',json.dumps(R,ensure_ascii=False))
        print('errs',errs[:5])
        await b.close()
asyncio.run(main())
