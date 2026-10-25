import asyncio,sys,json,os,statistics as st
from playwright.async_api import async_playwright
URL=os.environ.get('SIMURL','file://'+os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'build','hell_survive.html'))
JS="""([ch,route,fin,prof,L,gt0,win,boss,seed,tier,god,bk])=>{
 const G=__G; if(G.setDbg)G.setDbg(true); G.SAVE.holyBlood=true; Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true,ghost:true,octo:true,gun:true}); G.SAVE.diff.max=Math.max(5,tier||0); G.SAVE.shards=Math.max(G.SAVE.shards,99999); G.SAVE.diff.sel=tier||0; G.startGame(ch);   /* v6.30: 해금·참가비가 없으면 startGame이 0단계로 낮춰서 tier 인자가 무시되던 것 수정 */ let P=G.P; const keys=G.keys; if(window.__TW&&ch==='lizard'){ P.dmg*=window.__TW.dmg||1; P.cd*=window.__TW.cd||1; P.armor*=window.__TW.armor||1; P.spd*=window.__TW.spd||1; P.spd0=P.spd; P.max=Math.round(P.max*(window.__TW.hp||1)); P.hp=P.max; } const dt=1/30; P.uniqSeen={belia:true,celia:true};
 let s=seed*7919+13; const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};
 const PROF={
  std:['★','날카로운 발톱','날렵한 발톱','지옥의 심장','피의 갈증','끈적한 독','번지는 독','다발 사격','관통 화살','질주','넓은 발톱','카이팅 사격','지옥 낙뢰','회전 칼날','충격파','불길 오라','단단한 피부','영혼 자석','배움의 눈','급소 노리기','저격 시선','지옥불 구슬','뼈 투사체','밀치기'],
  cards:['★','지옥 낙뢰','회전 칼날','충격파','불길 오라','날카로운 발톱','날렵한 발톱','지옥의 심장','질주','피의 갈증','끈적한 독','다발 사격','단단한 피부','넓은 발톱','영혼 자석','배움의 눈','급소 노리기'],
  tank:['★','지옥의 심장','단단한 피부','날카로운 발톱','날렵한 발톱','질주','피의 갈증','끈적한 독','다발 사격','넓은 발톱','지옥 낙뢰','불길 오라','회전 칼날','영혼 자석','배움의 눈'],
  move:['★','질주','날카로운 발톱','날렵한 발톱','지옥의 심장','피의 갈증','끈적한 독','다발 사격','넓은 발톱','지옥 낙뢰','회전 칼날','단단한 피부']
 };
 let PRI=(PROF[prof]||PROF.std).slice(); if(window.__NOSPD) PRI=PRI.filter(x=>x!=='질주');
 if(ch==='lizard') PRI=['★','대검 단련','가벼운 휘두르기','대검 내려찍기','가시 비늘','피에 굶주린 광기','끝없는 광란','깊은 물결','지옥의 심장','단단한 피부',...PRI.filter(x=>x!=='질주')];
 if(ch==='chimera') PRI=['★','날 선 바람','날카로운 발톱','날렵한 발톱','쌍날 바람','멀리 나는 바람','더 높은 하늘','불씨 강화','넓은 불길','끓는 숨결','늘어난 촉수','뜬 눈','끝없는 난무',...PRI];
 if(ch==='ghost') PRI=['★','구슬 늘리기','분노한 머리','유령의 칼날','진한 저승 기운','빠른 손짓','빠른 칼놀림','유령 보법','멀리 뿌리기',...PRI];
 if(ch==='gun') PRI=['★','강화 화약','빠른 방아쇠','특수탄 강화','빠른 장전','불씨 각인','현상금 사냥','지옥의 심장','긴 총열',...PRI];
 if(ch==='twins') PRI=['★','무거운 동생','무거운 창날','원심력','달군 사슬','쌍둥이의 호흡','폭군의 사슬','쌍둥이의 분노','악마의 분노','빠른 손놀림','긴 사슬',...PRI];
 if(bk) P.bossK=bk; if(window.__EYE) Object.assign(G.EYE,window.__EYE); if(window.__AN) Object.assign(G.AN,window.__AN);
 if(route==='crimson') PRI=['★','피의 갈증',...PRI]; if(route==='twin') PRI=['★','날렵한 발톱',...PRI]; if(fin==='holy') PRI=['★',(ch==='archer'?'저격 시선':'지옥의 심장'),...PRI];
 function choose(){ const c=G.choices, title=document.getElementById('levelTitle').textContent;
   if(title.indexOf('갈림길')>=0||title.indexOf('최종')>=0){ const want=title.indexOf('최종')>=0?fin:route; let i=c.findIndex(u=>u.key===want&&!u.locked); if(i<0)i=c.findIndex(u=>!u.locked); return i<0?0:i; }
   if(title.indexOf('특수')>=0) return 0;
   if(window.__RANDPICK){ const ok=c.map((u,i)=>i).filter(i=>!c[i].locked); const sy=ok.filter(i=>c[i].cls==='syn'); if(sy.length&&rnd()<0.6) return sy[0]; const nn=ok.filter(i=>c[i].cls!=='syn'); const pool=nn.length?nn:ok; return pool.length?pool[Math.floor(rnd()*pool.length)]:0; }
   let best=0,bp=999; c.forEach((u,i)=>{ const nm=u.name||''; if(window.__BAN&&window.__BAN.some(x=>nm.indexOf(x)>=0)&&c.length>1) return; let p=PRI.findIndex(x=>nm.indexOf(x)>=0); if(p<0)p=PRI.length+(u.eff===true&&!u.def?5:0); if(nm.indexOf('★')>=0&&u.cls==='syn')p=-1; if(p<bp){bp=p;best=i;} }); return best; }
 function pump(){ const x=G.state; if(x==='levelup'){G.pick(choose());return true;} if(x==='evolve'){G.tick(dt);return true;} return false; }
 let guard=0;
 while(P.lvl<L && guard++<30000){ if(pump())continue; if(G.state==='play'){ if(P.lvl>=8){ if(route==='lava')P.lavaT=Math.max(P.lavaT,5); if(route==='skel')P.poisoned=true; if(route==='dream')P.bugF0=true; if(fin==='rage')P.low10=true; if(fin==='holy'&&ch==='archer'){P.up.range=Math.max(1,P.up.range||0);P.potions=Math.max(6,P.potions||0);} } P.hp=P.max; P.inv=9; G.addExp(P.need); G.tick(dt);} else break; }
 while(G.state==='levelup'||G.state==='evolve'){ if(!pump())break; }
 const UPS=JSON.parse(JSON.stringify(P.up)), SYN=Object.keys(P.syn).filter(k=>P.syn[k]);
 const rec={cards:UPS,synk:SYN,lvl:P.lvl,dmg:Math.round(P.dmg),cd:+(P.cd/P.aspd).toFixed(2),hp:P.max,rng:Math.round(P.rng),spd:Math.round(P.spd),skill:P.skill,tempo:+(Math.min(1.35,Math.max(1,P.spd0*1.25/P.spd))).toFixed(2),ups:Object.keys(P.up).length,syn:Object.keys(P.syn).filter(k=>P.up[k]).join('/')};
 let casts=0;
 function botMove(){
   if(G.holyQ){keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');return;}
   G.slots.length=0; let vx=0,vy=0,ne=null,nd=1e9,near=0;
   const lowhp=P.hp<P.max*0.4;
   for(const e of G.enemies){ if(e.hp<=0)continue; const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy); if(d<nd){nd=d;ne=e;} if(d<260)near++; }
   if(ch==='wolf'||ch==='chimera'||ch==='lizard'||ch==='twins'){
     // 근접 캐릭터: 체력이 충분하면 가장 가까운 적에게 붙어 싸우고, 위험해지면 물러난다
     const R=lowhp?240:(near>14?150:80);
     for(const e of G.enemies){ if(e.hp<=0)continue; const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy); if(d<R){const w=(R-d)/R; vx+=dx/(d||1)*w*(lowhp?1.6:0.9); vy+=dy/(d||1)*w*(lowhp?1.6:0.9);} }
     if(ne&&!lowhp){ const want=ch==='twins'?G.twLen()*0.6:P.rng*0.7+ne.r*0.4; if(nd>want){ const k=Math.min(1,(nd-want)/60); vx+=(ne.x-P.x)/nd*k*1.2; vy+=(ne.y-P.y)/nd*k*1.2; } }
   } else {
     for(const e of G.enemies){ if(e.hp<=0)continue; const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy); const R=260; if(d<R){const w=(R-d)/R; vx+=dx/(d||1)*w*1.5; vy+=dy/(d||1)*w*1.5;} }
   }
   keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');
   if(ne&&near>0){ const tx=-(ne.y-P.y)/(nd||1),ty=(ne.x-P.x)/(nd||1); const sg=(Math.floor(G.gt/6)%2)?1:-1; const tk=ch==='twins'?1.1:0.5; vx+=tx*tk*sg; vy+=ty*tk*sg; }
   if(near<=2){ let bo=null,bd=320; for(const o of G.orbs){const d=Math.hypot(o.x-P.x,o.y-P.y); if(d<bd){bd=d;bo=o;}} if(bo){vx+=(bo.x-P.x)/bd*0.5;vy+=(bo.y-P.y)/bd*0.5;} }
   vx+=(rnd()-0.5)*0.2; vy+=(rnd()-0.5)*0.2;
   if(Math.abs(vx)>0.12) keys.add(vx>0?'KeyD':'KeyA'); if(Math.abs(vy)>0.12) keys.add(vy>0?'KeyS':'KeyW');
   if(P.skill&&P.skT<=0&&near>=4&&!window.__NOCAST){G.cast();casts++;}
 }
 if(!boss){
   G.enemies.length=0; G.setT(gt0); P.hp=P.max; P.inv=0;
   const k0=P.kills,l0=P.lvl,n0=P.need,e0=P.exp; let loss=0,t=0,deaths=0,minhp=P.max,hurtN=0; const exp0=P.exp;
   let edmg=0; let expGain=0, lastLv=P.lvl, lastExp=P.exp, lastNeed=P.need;
   while(t<win && guard++<400000){
     if(pump())continue; if(G.state!=='play')break;
     botMove();
     const hb=P.hp; const pre=new Map(); for(const e of G.enemies) if(e.hp>0) pre.set(e,e.hp); G.tick(dt); t+=dt; G.setT(gt0+t); { const live=new Set(G.enemies); for(const [e,h] of pre){ edmg+= live.has(e)? Math.max(0,h-Math.max(0,e.hp)) : Math.max(0,h); } }
     if(P.lvl!==lastLv){ expGain+=lastNeed-lastExp+P.exp; lastLv=P.lvl; lastNeed=P.need; lastExp=P.exp; } else { expGain+=P.exp-lastExp; lastExp=P.exp; }
     if(G.state==='dead'){break;}
     if(P.hp<hb){loss+=hb-P.hp; hurtN++;}
     if(P.hp<=0||P.hp<hb*0){ }
     minhp=Math.min(minhp,P.hp);
     if(P.hp<P.max*0.15){ deaths++; P.hp=P.max; P.inv=2; }   // 거의 죽을 뻔한 횟수
   }
   rec.dm=Object.fromEntries(Object.entries(G.DMETER).map(([k,v])=>[G.dmName?G.dmName(k):k,Math.round(v)])); rec.unk=G.DUNK; rec.dboss=Object.fromEntries(Object.entries(G.DBOSS).map(([k,v])=>[G.dmName(k),Math.round(v)]));
   rec.win={edmg:Math.round(edmg),casts:casts,kills:P.kills-k0,loss:Math.round(loss),near:deaths,exp:Math.round(expGain),t:Math.round(t),dead:G.state==='dead'};
   return rec;
 }
 // ---- 마왕전 (이동·회피하는 봇, 무적 아님) ----
 if(window.__FW){ G.SAVE.fw.snap=G.snapP(); G.SAVE.fw.open=true; G.startFw(); P=G.P; for(let i=0;i<110;i++){ G.tick(dt); } } else { G.enterArena(); for(let i=0;i<110;i++){ pump(); G.tick(dt); } }
 let bt=0,bloss=0; const REACT=0.16;
 function esc(b){ let fx=0,fy=0; const M=30;
   const TLs=b.tele.slice(); for(const m of G.enemies) if((m.kind==='skm'||m.kind==='mini')&&m.hp>0&&m.tele) for(const t of m.tele) TLs.push(t);
   for(const q of TLs){ if(q.done||q.t<REACT)continue; const dx=P.x-q.x,dy=P.y-q.y;
     if(q.k==='circle'){const sy=q.r/(q.ry||q.r),d=Math.hypot(dx,dy*sy); if(d<q.r+M){const u=d>1?[dx/d,dy*sy/d]:[1,0]; fx+=u[0];fy+=u[1];}}
     else if(q.k==='donut'){const d=Math.hypot(dx,dy)||1; if(d>q.r-M&&d<q.r2+M){const sg=d<(q.r+q.r2)/2?-1:1; fx+=sg*dx/d;fy+=sg*dy/d;}}
     else if(q.k==='fan'){const d=Math.hypot(dx,dy)||1; let da=Math.atan2(dy,dx)-q.ang; da=Math.atan2(Math.sin(da),Math.cos(da)); if(d<q.len+M&&Math.abs(da)<q.half+0.3){ const sg=da>=0?1:-1, ta=q.ang+sg*(q.half+0.5); fx+=Math.cos(ta)*1.2+dx/d*0.5; fy+=Math.sin(ta)*1.2+dy/d*0.5; }}
     else if(q.k==='rect'){const c=Math.cos(q.ang),s=Math.sin(q.ang),lx=dx*c+dy*s,ly=-dx*s+dy*c; if(lx>-M&&lx<q.len+M&&Math.abs(ly)<q.w/2+M){const sg=ly>=0?1:-1; fx+=-s*sg; fy+=c*sg;}} }
   const EB=(G.ebul||[]).concat((G.skp||[]).map(w=>{ if(w._p===undefined) w._p={r:40,get x(){return w.x},get y(){return w.y},vx:Math.cos(w.ang)*w.sp,vy:Math.sin(w.ang)*w.sp}; return w._p; })).concat((G.anOrbs||[]).filter(o=>!o.white).map(o=>{ if(o._p===undefined) o._p={r:o.r,get x(){return o.x},get y(){return o.y},vx:Math.cos(o.a)*o.sp,vy:Math.sin(o.a)*o.sp}; return o._p; }));
   for(const q of EB){ if(q._ig===undefined) q._ig=rnd()<(+window.__IGN||0.25); if(q._ig) continue; const dx=P.x-q.x,dy=P.y-q.y,d=Math.hypot(dx,dy); const R0=q.r+75; if(d<R0){ const sp=Math.hypot(q.vx,q.vy)||1,ux=q.vx/sp,uy=q.vy/sp; const along=dx*ux+dy*uy; if(along>-25){ const side=dx*(-uy)+dy*ux, sg=side>=0?1:-1, w=(R0-d)/R0; fx+=-uy*sg*w*2.4; fy+=ux*sg*w*2.4; fx+=dx/(d||1)*w*0.8; fy+=dy/(d||1)*w*0.8; } } }
   if(b.st==='dash'||b.st==='air'||b.st==='rDash'||b.st==='gcharge'||b.st==='pAir'){ const d=Math.hypot(P.x-b.x,P.y-b.y); if(d<b.r+120){fx+=(P.x-b.x)/(d||1);fy+=(P.y-b.y)/(d||1);} }
   return [fx,fy]; }
 const HL={}; const hp0=P.hp; let bcasts=0, deadAt=null; const SMART0=false; const DUR=window.__DUR||(god?400:300); if(window.__BIGHP&&G.boss){G.boss.hp=G.boss.max=1e7;} if(window.__NOEX&&G.boss){G.boss.ex=[];} if(window.__TANK){P.max=P.hp=1e6;}   // TANK: 죽지 않게 체력만 크게 (받은 피해를 그대로 잰다)
 while(bt<DUR && G.boss && (G.state==='play'||G.state==='levelup'||G.state==='evolve')){   /* v9.40: 보스전 중 레벨업(영혼 구슬)이 나와도 판이 끝나지 않게 */
   const b=G.boss; if(pump())continue; let TG=b; if(b.shield){ let bd=1e9; for(const q of G.enemies) if(q.kind==='skh'&&q.hp>0){ const dd=Math.hypot(q.x-P.x,q.y-P.y); if(dd<bd){bd=dd;TG=q;} } }
   let dx=TG.x-P.x,dy=TG.y-P.y,d=Math.hypot(dx,dy)||1; if(d<30){ const a=(Math.floor(bt*2)%8)*0.785; dx=-Math.cos(a)*30; dy=-Math.sin(a)*30; d=30; }
   keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');
   let [fx,fy]=esc(b); let vx=0,vy=0; const st=TG===b?b.st:'-';
   const danger=(st==='slash'||st==='rWind'||st==='rDash'||st==='gcWind'||st==='gcharge'||st==='frenzy'||st==='frenzyEnd'||st==='bite'||st==='gsweep'||st==='pAir'||st==='combo'||st==='tailWind'||st==='dashWind'||st==='dash'||st==='waveWind'||st==='sweepWind'||st==='jumpWind'||st==='air'||st==='roar'||st==='slamUp'||st==='slamDrop'||st==='wave'||st==='spikes'||st==='souls');
   const reach=P.rng+TG.r*0.8;   // 이 거리 안이면 보스를 칠 수 있다
   let wo=null; if(b.bk==='angel'){ let wd=1e9; for(const o of (G.anOrbs||[])){ if(!o.white)continue; if(o._ig===undefined)o._ig=rnd()<(+window.__WIGN||0.15); if(o._ig)continue; const dd=Math.hypot(o.x-P.x,o.y-P.y); if(dd<wd){wd=dd;wo=o;} } }   // 타락천사: 흰 구체는 직접 닿아야 한다 (가끔 놓친다)
   if(fx||fy){ vx=fx; vy=fy; }
   else if(wo){ const dd=Math.hypot(wo.x-P.x,wo.y-P.y)||1; vx=(wo.x-P.x)/dd; vy=(wo.y-P.y)/dd; }
   else if(b.bk==='angel'&&b.shT>0){ const bx=b.x-Math.cos(b.sAng)*150,by=b.y-Math.sin(b.sAng)*110,dd=Math.hypot(bx-P.x,by-P.y)||1; if(dd>30){vx=(bx-P.x)/dd;vy=(by-P.y)/dd;} }   // 방패: 등 뒤로 돌아간다
   else if(danger && !SMART0){ const safe=(st==='combo'||st==='tailWind')?((ch==='wolf'||ch==='chimera'||ch==='lizard')?Math.max(reach-10,238):262):270; if(d<safe){vx=-dx/d;vy=-dy/d;} else { vx=-(dy/d)*0.6; vy=(dx/d)*0.6; } }
   else if(ch==='twins'){ const want=Math.max(95,G.twLen?G.twLen()*0.85+TG.r*0.4:120); if(d>want+30){vx=dx/d;vy=dy/d;} else if(d<want-30){vx=-dx/d;vy=-dy/d;} else { vx=-(dy/d); vy=(dx/d); } }
   else { const ML=(ch==='wolf'||ch==='chimera'||ch==='lizard'); const want=ML?Math.max(70,reach*0.85):250; if(d>want+25){vx=dx/d;vy=dy/d;} else if(!ML&&d<want-60){vx=-dx/d;vy=-dy/d;} else if(ML&&d<want-30){vx=-dx/d*0.3;vy=-dy/d*0.3;} else { vx=-(dy/d)*0.4; vy=(dx/d)*0.4; } }
   { const L0=Math.hypot(vx,vy); if(L0>0.05){ let bs=-9,bx=vx/L0,by=vy/L0; for(let k=0;k<16;k++){ const a=k*Math.PI/8,cx=Math.cos(a),cy=Math.sin(a); const sc=cx*vx/L0+cy*vy/L0; let pen=0; for(const dd of [40,90,150]) if(!G.inPoly(P.x+cx*dd,P.y+cy*dd)) pen+=2.2; const v=sc-pen; if(v>bs){bs=v;bx=cx;by=cy;} } vx=bx; vy=by; } }
   if(Math.abs(vx)>0.3) keys.add(vx>0?'KeyD':'KeyA'); if(Math.abs(vy)>0.3) keys.add(vy>0?'KeyS':'KeyW');
   if(P.skill&&P.skT<=0&&d<420&&!window.__NOCAST){G.cast();bcasts++;}
   if(god){P.hp=9999;} const hb=P.hp, st0=G.boss?G.boss.st:'-'; G.tick(dt); bt+=dt; if(P.hp<hb&&!(god&&hb-P.hp>5000)){bloss+=hb-P.hp; HL[st0]=(HL[st0]||0)+Math.round(hb-P.hp);}   /* v9.40: GOD에서 레벨업 등으로 체력이 최대치로 잘리는 건 피해로 안 센다 */
   if(G.state==='dead'){deadAt=bt;break;}
   if(!G.arena||!G.arena.k){ if(P.y>1055)P.y=1055; } else if(G.arena.k==='angel'&&P.y>1740)P.y=1740;
 }
 rec.dm=Object.fromEntries(Object.entries(G.DMETER).map(([k,v])=>[G.dmName?G.dmName(k):k,Math.round(v)])); rec.unk=G.DUNK; rec.dboss=Object.fromEntries(Object.entries(G.DBOSS).map(([k,v])=>[G.dmName(k),Math.round(v)]));
 rec.boss={bdmg:G.boss?Math.round(G.boss.max-G.boss.hp):0,mx:G.boss?Math.round(G.boss.max):0,t:Math.round(bt),dead:G.state==='dead',left:G.boss?Math.round(G.boss.hp):0,loss:Math.round(bloss),hp0:Math.round(hp0),casts:bcasts,hl:HL};
 return rec;
}"""
SEM=asyncio.Semaphore(int(os.environ.get('PAR','4')))
async def run(b,cfg):
    async with SEM:
        pg=await b.new_page(viewport={'width':800,'height':500})
        if os.environ.get('SEED'): await pg.add_init_script("(()=>{let a=%d*2654435761>>>0;Math.random=function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};})()" % (cfg[8]*7+int(os.environ.get('SEED'))))
        await pg.goto(URL);await pg.wait_for_function('window.__G&&__G.ready',timeout=60000)
        if os.environ.get('NOSPD'): await pg.evaluate('()=>{window.__NOSPD=1}')
        if os.environ.get('FW'): await pg.evaluate('()=>{window.__FW=1}')
        if os.environ.get('TWJ'): await pg.evaluate('(j)=>{window.__TW=JSON.parse(j)}',os.environ['TWJ'])
        if os.environ.get('BANJ'): await pg.evaluate('(j)=>{window.__BAN=JSON.parse(j)}',os.environ['BANJ'])
        if os.environ.get('RANDPICK'): await pg.evaluate('()=>{window.__RANDPICK=1}')
        if os.environ.get('NOCAST'): await pg.evaluate('()=>{window.__NOCAST=1}')
        if os.environ.get('BIGHP'): await pg.evaluate('()=>{window.__BIGHP=1}')
        if os.environ.get('DUR'): await pg.evaluate('(d)=>{window.__DUR=d}',float(os.environ['DUR']))
        if os.environ.get('SKCD'): await pg.evaluate('(j)=>{window.__SKCD=JSON.parse(j)}',os.environ['SKCD'])
        if os.environ.get('EYEJ'): await pg.evaluate('(j)=>{window.__EYE=JSON.parse(j)}',os.environ['EYEJ'])
        if os.environ.get('ANJ'): await pg.evaluate('(j)=>{window.__AN=JSON.parse(j)}',os.environ['ANJ'])
        if os.environ.get('NOEX'): await pg.evaluate('()=>{window.__NOEX=1}')
        if os.environ.get('TANK'): await pg.evaluate('()=>{window.__TANK=1}')
        try: r=await pg.evaluate(JS,cfg)
        except Exception as e: r={'err':str(e)[:1500]}
        await pg.close();return r
VAR={'archer:red':('archer','elf','red'),'archer:holy':('archer','elf','holy'),'wolf:abyss':('wolf','abyss',''),'wolf:crimson':('wolf','crimson','blood'),'wolf:holy':('wolf','crimson','holy'),'wolf:twin':('wolf','twin',''),
     'snail:venom':('snail','venom',''),'snail:lava':('snail','lava',''),'snail:bomb':('snail','bomb',''),'archer:elf':('archer','elf',''),'archer:skel':('archer','skel',''),'chimera':('chimera','',''),'chimera:flame':('chimera','flame',''),'chimera:dream':('chimera','dream',''),'lizard:rage':('lizard','','rage'),'lizard:water':('lizard','','water'),'twins':('twins','',''),'ghost':('ghost','orb',''),'ghost:knight':('ghost','knight',''),'octo':('octo','',''),'lizard:guard':('lizard','guard','guard'),'wolf:fallen':('wolf','crimson','fallen'),'wolf:blood':('wolf','crimson','blood'),'chimera:wind':('chimera','wind',''),'gun':('gun','','')}
BHP=int(os.environ.get('BHP','18000'))
async def main():
    # argv: mode(L|B) variants(json list) N prof tier
    mode=sys.argv[1]; vs=json.loads(sys.argv[2]); N=int(sys.argv[3]); prof=sys.argv[4] if len(sys.argv)>4 else 'std'; tier=int(sys.argv[5]) if len(sys.argv)>5 else 0
    stages=json.loads(os.environ.get('STAGES','[[8,150],[15,360],[22,660]]'))
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); jobs=[]
        for v in vs:
            ch,rt,fin=VAR[v]
            if mode=='B':
                for i in range(N): jobs.append((v,25,'boss',[ch,rt,fin,prof,25,0,0,True,i+1+int(os.environ.get('SOFF','0')),tier,bool(os.environ.get('GOD')),os.environ.get('BK','')]))
            else:
                for (L,g) in stages:
                    for i in range(N): jobs.append((v,L,'win',[ch,rt,fin,prof,L,g,90,False,i+1+int(os.environ.get('SOFF','0')),tier]))
        res=await asyncio.gather(*[run(b,j[3]) for j in jobs])
        out={}
        for j,r in zip(jobs,res): out.setdefault((j[0],j[1]),[]).append(r)
        for (v,L),rs in out.items():
            if any('err' in r for r in rs): print(v,L,'ERR',[r.get('err') for r in rs][:1]); continue
            r0=rs[0]
            if os.environ.get('UNK'): print('UNK',v,L,json.dumps({'dm':r0.get('dm'),'unk':r0.get('unk'),'dboss':r0.get('dboss')},ensure_ascii=False)); continue
            if mode=='B' and os.environ.get('RAW'):
                for r in rs: print('RAW',json.dumps({'v':v,'boss':r['boss'],'dmg':r['dmg'],'cards':r['cards'],'syn':r['synk'],'hp':r['hp'],'dm':r.get('dm')},ensure_ascii=False))
                continue
            if mode=='B':
                if os.environ.get('HL'): [print('   ',r['boss']['hl']) for r in rs]
                print(v.ljust(12),'build dmg',r0['dmg'],'cd',r0['cd'],'hp',r0['hp'],'spd',r0['spd'],'tempo',r0['tempo'],'| boss',[(r['boss']['t'],'D' if r['boss']['dead'] else 'W' if r['boss']['left']==0 else 'T',r['boss']['loss'],'dps%d'%round((BHP-r['boss']['left'])/max(1,r['boss']['t']))) for r in rs])
            elif os.environ.get('RAW'):
                for r in rs: print('RAWL',json.dumps({'v':v,'L':L,'win':r['win'],'dmg':r['dmg'],'cards':r['cards'],'syn':r['synk'],'dm':r.get('dm')},ensure_ascii=False))
            else:
                f=lambda k:round(st.mean([r['win'][k] for r in rs]),1)
                print(v.ljust(12),'Lv',L,'dmg',r0['dmg'],'cd',r0['cd'],'hp',r0['hp'],'spd',r0['spd'],'sk',r0['skill'],'syn',[r['syn'] for r in rs],'| kills',f('kills'),'exp',f('exp'),'loss',f('loss'),'near',f('near'),'dead',sum(r['win']['dead'] for r in rs))
        await b.close()
asyncio.run(main())
