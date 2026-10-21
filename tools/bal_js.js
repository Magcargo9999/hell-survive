([ch,route,fin,prof,L,gt0,win,boss,seed,tier,god,bk])=>{
 const G=__G; G.SAVE.holyBlood=true; Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true,ghost:true,octo:true}); G.SAVE.diff.sel=tier||0; G.SAVE.fw.open=true; G.SAVE.fw.cleared=true; G.startGame(ch); let P=G.P; const keys=G.keys; if(window.__TW&&ch==='lizard'){ P.dmg*=window.__TW.dmg||1; P.cd*=window.__TW.cd||1; P.armor*=window.__TW.armor||1; P.spd*=window.__TW.spd||1; P.spd0=P.spd; P.max=Math.round(P.max*(window.__TW.hp||1)); P.hp=P.max; } const dt=1/30; P.uniqSeen={belia:true,celia:true};
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
 if(ch==='ghost') PRI=['★','구슬 늘리기','진한 저승 기운','빠른 손짓','넓게 흩뿌리기','멀리 뿌리기',...PRI];
 if(ch==='twins') PRI=['★','무거운 동생','무거운 창날','원심력','달군 사슬','쌍둥이의 호흡','폭군의 사슬','쌍둥이의 분노','악마의 분노','빠른 손놀림','긴 사슬',...PRI];
 if(bk) P.bossK=bk; if(window.__EYE) Object.assign(G.EYE,window.__EYE);
 if(route==='crimson') PRI=['★','피의 갈증',...PRI]; if(route==='twin') PRI=['★','날렵한 발톱',...PRI]; if(fin==='holy') PRI=['★',(ch==='archer'?'저격 시선':'지옥의 심장'),...PRI];
 function choose(){ const c=G.choices, title=document.getElementById('levelTitle').textContent;
   if(title.indexOf('갈림길')>=0||title.indexOf('최종')>=0){ const want=title.indexOf('최종')>=0?fin:route; let i=c.findIndex(u=>u.key===want); if(i>=0&&c[i].locked) c[i].locked=false; if(i<0)i=c.findIndex(u=>!u.locked); return i<0?0:i; }
   if(title.indexOf('특수')>=0) return 0;
   if(window.__RANDPICK){ const ok=c.map((u,i)=>i).filter(i=>!c[i].locked); const sy=ok.filter(i=>c[i].cls==='syn'); if(sy.length&&rnd()<0.6) return sy[0]; const nn=ok.filter(i=>c[i].cls!=='syn'); const pool=nn.length?nn:ok; return pool.length?pool[Math.floor(rnd()*pool.length)]:0; }
   let best=0,bp=999; c.forEach((u,i)=>{ const nm=u.name||''; if(window.__BAN&&window.__BAN.some(x=>nm.indexOf(x)>=0)&&c.length>1) return; let p=PRI.findIndex(x=>nm.indexOf(x)>=0); if(p<0)p=PRI.length+(u.eff===true&&!u.def?5:0); if(nm.indexOf('★')>=0&&u.cls==='syn')p=-1; if(p<bp){bp=p;best=i;} }); return best; }
 function pump(){ const x=G.state; if(x==='levelup'){G.pick(choose());return true;} if(x==='evolve'){G.tick(dt);return true;} return false; }

 let guard=0, casts=0;
 function hash2(x, y, s) {
   let h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(s || 0, 1442695041)) | 0;
   h = Math.imul(h ^ (h >>> 13), 1274126177);
   h ^= h >>> 16;
   return (h >>> 0) / 4294967296;
 }
 function vnoise(x, y) {
   const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
   const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
   const a = hash2(xi, yi, 7), b = hash2(xi + 1, yi, 7), c = hash2(xi, yi + 1, 7), d = hash2(xi + 1, yi + 1, 7);
   return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
 }
 // 용암 웅덩이: 시작 지점 주변은 안전지대
 function isLava(tx, ty) {   // 큰 덩어리 대신 작은 웅덩이가 여기저기 흩어져 있다 (평균 3칸, 가끔 큰 것)
   if (tx * tx + ty * ty < 80) return false;
   return vnoise(tx / 4 + 31, ty / 4 + 17) * 0.6 + vnoise(tx / 2 + 5, ty / 2 + 9) * 0.4 > 0.7 && vnoise(tx / 14 + 50, ty / 14 + 70) > 0.42;
 }
 const lavaAt=(x,y)=>isLava(Math.floor(x/64),Math.floor(y/64));
 function botMove(){
   if(G.holyQ){keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');return;}
   G.slots.length=0;
   keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');
   const ranged=(ch==='archer'||ch==='ghost'||ch==='octo'||ch==='snail');
   const atkR=ch==='archer'?P.rng*4.4+40:ch==='ghost'?400*Math.min(1.8,Math.max(1,P.rng/100)):ch==='octo'?430*Math.min(1.6,Math.max(1,P.rng/100)):ch==='snail'?340:ch==='twins'?(G.twLen?G.twLen():120):P.rng;
   const hpR=P.hp/P.max; const DW=(window.__DW||1)*(hpR<0.5?1.5:1);
   const NB=[]; let ne=null,nd=1e9,near=0;
   for(const e of G.enemies){ if(e.hp<=0)continue; const dx=e.x-P.x,dy=e.y-P.y,d=Math.hypot(dx,dy); if(d<nd&&e.kind!=='bug'){nd=d;ne=e;} if(d<480)NB.push(e); if(d<260)near++; }
   let want=ranged?atkR*0.55:Math.max(35,atkR*0.55);
   if(!ranged&&hpR<0.45) want=atkR*2.2;
   if(ranged&&hpR<0.4) want=atkR*0.8;
   const EB=(G.ebul||[]);
   let bs=-1e9,bx=0,by=0;
   const spd=P.spd||180;
   let ovx=0,ovy=0; for(const o of G.orbs){ const dx=o.x-P.x,dy=o.y-P.y,d=Math.hypot(dx,dy); if(d>700||d<1)continue; const w=(o.val||1)/(1+d/140); ovx+=dx/d*w; ovy+=dy/d*w; } const oL=Math.hypot(ovx,ovy); const oW=oL>0?Math.min(1,oL/6)*(hpR>0.5?(window.__OW||5):2.5):0; if(oL>0){ovx/=oL;ovy/=oL;}
   let it=null,itd=520; for(const q of (G.items||[])){ if(q.type==='heal'&&hpR>0.85)continue; const d=Math.hypot(q.x-P.x,q.y-P.y); if(d<itd){itd=d;it=q;} }
   const TL=[]; for(const m of G.enemies) if(m.hp>0&&m.tele&&m.tele.length&&Math.hypot(m.x-P.x,m.y-P.y)<700) for(const q of m.tele) if(!q.done) TL.push(q);
   const inTele=(x,y)=>{ for(const q of TL){ const dx=x-q.x,dy=y-q.y, M=34;
     if(q.k==='circle'){ if(Math.hypot(dx,dy)<q.r+M) return true; }
     else if(q.k==='donut'){ const d=Math.hypot(dx,dy); if(d>q.r-M&&d<q.r2+M) return true; }
     else if(q.k==='fan'){ const d=Math.hypot(dx,dy); let da=Math.atan2(dy,dx)-q.ang; da=Math.atan2(Math.sin(da),Math.cos(da)); if(d<q.len+M&&Math.abs(da)<q.half+0.25) return true; }
     else if(q.k==='rect'){ const c=Math.cos(q.ang),s=Math.sin(q.ang),lx=dx*c+dy*s,ly=-dx*s+dy*c; if(lx>-M&&lx<q.len+M&&Math.abs(ly)<q.w/2+M) return true; } } return false; };
   for(let k=0;k<9;k++){
     const cx=k<8?Math.cos(k*Math.PI/4):0, cy=k<8?Math.sin(k*Math.PI/4):0; let sc=0;
     for(const T of [0.25,0.6]){ const px=P.x+cx*spd*T, py=P.y+cy*spd*T, wT=T<0.3?1.6:1;
       for(const e of NB){ const big=(e.kind==='mini'||e.kind==='uniq'); let safe=e.r+(ranged?70:(hpR<0.45?60:22))+(big?50:0); if(e.kind==='bug') safe=e.r+(e.fuse>0?140:40);
         const dd=Math.hypot(px-e.x,py-e.y)-(e.sp||60)*T*0.8; if(dd<safe){ const u=(safe-dd)/safe; sc-=Math.max(6,e.dmg||10)*u*u*wT*(big?2:1)*DW; } }
       for(const q of EB){ const qx=q.x+(q.vx||0)*T, qy=q.y+(q.vy||0)*T; const dd=Math.hypot(px-qx,py-qy); const safe=(q.r||8)+26; if(dd<safe) sc-=25*wT*(safe-dd)/safe; }
     }
     { const lp=P.x+cx*spd*0.25, lq=P.y+cy*spd*0.25; if(lavaAt(lp,lq)) sc-=40; if(lavaAt(P.x+cx*spd*0.5,P.y+cy*spd*0.5)) sc-=15; if(lavaAt(P.x+cx*30,P.y+cy*30)) sc-=40; }
     if(TL.length){ if(inTele(P.x+cx*spd*0.25,P.y+cy*spd*0.25)) sc-=60; if(inTele(P.x+cx*spd*0.5,P.y+cy*spd*0.5)) sc-=25; }
     if(k<8){
       if(ne){ const dx=ne.x-P.x,dy=ne.y-P.y,d=nd||1; const err=Math.max(-1,Math.min(1,(d-want)/90)); sc+=err*(cx*dx/d+cy*dy/d)*(ranged?4:6); }
       sc+=(cx*ovx+cy*ovy)*oW;
       if(it){ sc+=(cx*(it.x-P.x)+cy*(it.y-P.y))/itd*(it.type==='heal'?(hpR<0.6?9:4):3); }
       if(ne&&nd<want*1.3){ const tx=-(ne.y-P.y)/(nd||1),ty=(ne.x-P.x)/(nd||1); const sg=(Math.floor(G.gt/7)%2)?1:-1; sc+=(cx*tx+cy*ty)*sg*1.2; }
     } else sc-=1.0;
     if(sc>bs){bs=sc;bx=cx;by=cy;}
   }
   if(Math.abs(bx)>0.3) keys.add(bx>0?'KeyD':'KeyA'); if(Math.abs(by)>0.3) keys.add(by>0?'KeyS':'KeyW');
   if(P.skill&&P.skT<=0&&(near>=5||hpR<0.4||(G.mini&&Math.hypot(G.mini.x-P.x,G.mini.y-P.y)<420))&&!window.__NOCAST){G.cast();casts++;}
 }
 const DC={},DL=[],RS=[];
 const LIM=window.__LIM||1800; const lt={}; let res='timeout', lastL=P.lvl, floss=0, miniT=null, miniEnd=null, nearD=0;
 P.hp=P.max;
 while(guard++<300000){
   if(pump()) continue;
   if(G.state==='dead'){res='dead';break;}
   if(G.state!=='play'){res='state:'+G.state;break;}
   if(P.lvl>=8){ if(route==='lava')P.lavaT=Math.max(P.lavaT,5); if(route==='skel')P.poisoned=true; if(route==='dream')P.bugF0=true; if(fin==='rage')P.low10=true; if(fin==='holy'&&ch==='archer'){P.up.snipe=Math.max(1,P.up.snipe||0);P.potions=Math.max(6,P.potions||0);} }
   botMove(); const hb=P.hp; G.tick(dt); if(P.hp<hb){ floss+=hb-P.hp; let c='other',md=1e9; if(lavaAt(P.x,P.y)) c='lava'; else { for(const e of G.enemies){ if(e.hp<=0&&e.kind!=='bug')continue; const d=Math.hypot(e.x-P.x,e.y-P.y)-e.r; if(d<md){md=d;c=e.kind+(d<40?'':'~far');} } } DC[c]=(DC[c]||0)+(hb-P.hp); DL.push([G.gt,c,hb-P.hp]); }
   if(G.mini&&miniT===null) miniT=Math.round(G.gt); if(miniT!==null&&!G.mini&&miniEnd===null&&G.state==='play') miniEnd=Math.round(G.gt);
   if(P.hp>0&&P.hp<P.max*0.2&&window.__RESCUE){ RS.push([P.lvl,Math.round(G.gt)]); P.hp=P.max; P.inv=2; }
   while(lastL<P.lvl){ lastL++; lt[lastL]=Math.round(G.gt); }
   if(G.state==='dead'){res='dead';break;}
   if(P.lvl>=25){res='lv25';break;}
   if(G.gt>LIM){res='timeout';break;}
 }
 const fld={res,rs:RS,lt,lvl:P.lvl,gt:Math.round(G.gt),kills:P.kills,loss:Math.round(floss),miniT,miniEnd,miniAlive:!!G.mini,dc:Object.fromEntries(Object.entries(DC).map(([k,v])=>[k,Math.round(v)])),dlast:(()=>{const o={};for(const [t,c,v] of DL) if(t>G.gt-15) o[c]=Math.round((o[c]||0)+v); return o;})(),route:P.route,fin:P.fin,form:P.form,casts};
 const rec={field:fld,dmg:Math.round(P.dmg),hp:P.max,cards:JSON.parse(JSON.stringify(P.up)),syn:Object.keys(P.syn).filter(k=>P.syn[k])};
 if(res!=='lv25'||!boss) return rec;
 while(G.state==='levelup'||G.state==='evolve'){ if(!pump())break; }
 for(const k of ['KeyW','KeyA','KeyS','KeyD']) keys.delete(k);
 if(window.__FW){ G.SAVE.fw.snap=G.snapP(); G.SAVE.fw.open=true; G.startFw(); P=G.P; for(let i=0;i<110;i++){ G.tick(dt); } } else { let gi=0; for(;gi<400&&!G.boss;gi++){ if(!G.trans&&!G.arena&&G.state==='play') G.enterArena(); if(!pump()) G.tick(dt); } rec.diag0={gi,boss:!!G.boss,arena:!!G.arena,trans:!!G.trans,st:G.state,castle:!!G.castle}; for(let i=0;i<80;i++){ pump(); G.tick(dt); } rec.diag1={boss:!!G.boss,bst:G.boss&&G.boss.st,bhp:G.boss&&Math.round(G.boss.hp),arena:!!G.arena,st:G.state,ne:G.enemies.length}; }
 let bt=0,bloss=0; const REACT=0.16;
 function esc(b){ let fx=0,fy=0; const M=30;
   const TLs=b.tele.slice(); for(const m of G.enemies) if((m.kind==='skm'||m.kind==='mini')&&m.hp>0&&m.tele) for(const t of m.tele) TLs.push(t);
   for(const q of TLs){ if(q.done||q.t<REACT)continue; const dx=P.x-q.x,dy=P.y-q.y;
     if(q.k==='circle'){const d=Math.hypot(dx,dy); if(d<q.r+M){const u=d>1?[dx/d,dy/d]:[1,0]; fx+=u[0];fy+=u[1];}}
     else if(q.k==='donut'){const d=Math.hypot(dx,dy)||1; if(d>q.r-M&&d<q.r2+M){const sg=d<(q.r+q.r2)/2?-1:1; fx+=sg*dx/d;fy+=sg*dy/d;}}
     else if(q.k==='fan'){const d=Math.hypot(dx,dy)||1; let da=Math.atan2(dy,dx)-q.ang; da=Math.atan2(Math.sin(da),Math.cos(da)); if(d<q.len+M&&Math.abs(da)<q.half+0.3){ const sg=da>=0?1:-1, ta=q.ang+sg*(q.half+0.5); fx+=Math.cos(ta)*1.2+dx/d*0.5; fy+=Math.sin(ta)*1.2+dy/d*0.5; }}
     else if(q.k==='rect'){const c=Math.cos(q.ang),s=Math.sin(q.ang),lx=dx*c+dy*s,ly=-dx*s+dy*c; if(lx>-M&&lx<q.len+M&&Math.abs(ly)<q.w/2+M){const sg=ly>=0?1:-1; fx+=-s*sg; fy+=c*sg;}} }
   const EB=(G.ebul||[]).concat((G.skp||[]).map(w=>{ if(w._p===undefined) w._p={r:40,get x(){return w.x},get y(){return w.y},vx:Math.cos(w.ang)*w.sp,vy:Math.sin(w.ang)*w.sp}; return w._p; }));
   for(const q of EB){ if(q._ig===undefined) q._ig=rnd()<(+window.__IGN||0.25); if(q._ig) continue; const dx=P.x-q.x,dy=P.y-q.y,d=Math.hypot(dx,dy); const R0=q.r+75; if(d<R0){ const sp=Math.hypot(q.vx,q.vy)||1,ux=q.vx/sp,uy=q.vy/sp; const along=dx*ux+dy*uy; if(along>-25){ const side=dx*(-uy)+dy*ux, sg=side>=0?1:-1, w=(R0-d)/R0; fx+=-uy*sg*w*2.4; fy+=ux*sg*w*2.4; fx+=dx/(d||1)*w*0.8; fy+=dy/(d||1)*w*0.8; } } }
   if(b.st==='dash'||b.st==='air'||b.st==='rDash'||b.st==='gcharge'||b.st==='pAir'){ const d=Math.hypot(P.x-b.x,P.y-b.y); if(d<b.r+120){fx+=(P.x-b.x)/(d||1);fy+=(P.y-b.y)/(d||1);} }
   return [fx,fy]; }
 const HL={}; const hp0=P.hp; let bcasts=0, deadAt=null; const SMART0=false; const DUR=window.__DUR||(god?400:300); if(window.__BIGHP&&G.boss){G.boss.hp=G.boss.max=1e7;}
 while(bt<DUR && G.boss && (G.state==='play'||G.state==='levelup'||G.state==='evolve')){
   const b=G.boss; if(pump())continue; let TG=b; if(b.shield){ let bd=1e9; for(const q of G.enemies) if(q.kind==='skh'&&q.hp>0){ const dd=Math.hypot(q.x-P.x,q.y-P.y); if(dd<bd){bd=dd;TG=q;} } }
   let dx=TG.x-P.x,dy=TG.y-P.y,d=Math.hypot(dx,dy)||1; if(d<30){ const a=(Math.floor(bt*2)%8)*0.785; dx=-Math.cos(a)*30; dy=-Math.sin(a)*30; d=30; }
   keys.delete('KeyW');keys.delete('KeyA');keys.delete('KeyS');keys.delete('KeyD');
   let [fx,fy]=esc(b); let vx=0,vy=0; const st=TG===b?b.st:'-';
   const danger=(st==='rWind'||st==='rDash'||st==='gcWind'||st==='gcharge'||st==='frenzy'||st==='frenzyEnd'||st==='bite'||st==='gsweep'||st==='pAir'||st==='combo'||st==='tailWind'||st==='dashWind'||st==='dash'||st==='waveWind'||st==='sweepWind'||st==='jumpWind'||st==='air'||st==='roar'||st==='slamUp'||st==='slamDrop'||st==='wave'||st==='spikes'||st==='souls');
   const reach=P.rng+TG.r*0.8;   // 이 거리 안이면 보스를 칠 수 있다
   if(fx||fy){ vx=fx; vy=fy; }
   else if(danger && !SMART0){ const safe=(st==='combo'||st==='tailWind')?((ch==='wolf'||ch==='chimera'||ch==='lizard')?Math.max(reach-10,238):262):270; if(d<safe){vx=-dx/d;vy=-dy/d;} else { vx=-(dy/d)*0.6; vy=(dx/d)*0.6; } }
   else if(ch==='twins'){ const want=Math.max(95,G.twLen?G.twLen()*0.85+TG.r*0.4:120); if(d>want+30){vx=dx/d;vy=dy/d;} else if(d<want-30){vx=-dx/d;vy=-dy/d;} else { vx=-(dy/d); vy=(dx/d); } }
   else { const ML=(ch==='wolf'||ch==='chimera'||ch==='lizard'); const want=ML?Math.max(70,reach*0.85):250; if(d>want+25){vx=dx/d;vy=dy/d;} else if(!ML&&d<want-60){vx=-dx/d;vy=-dy/d;} else if(ML&&d<want-30){vx=-dx/d*0.3;vy=-dy/d*0.3;} else { vx=-(dy/d)*0.4; vy=(dx/d)*0.4; } }
   { const L0=Math.hypot(vx,vy); if(L0>0.05){ let bs=-9,bx=vx/L0,by=vy/L0; for(let k=0;k<16;k++){ const a=k*Math.PI/8,cx=Math.cos(a),cy=Math.sin(a); const sc=cx*vx/L0+cy*vy/L0; let pen=0; for(const dd of [40,90,150]) if(!G.inPoly(P.x+cx*dd,P.y+cy*dd)) pen+=2.2; const v=sc-pen; if(v>bs){bs=v;bx=cx;by=cy;} } vx=bx; vy=by; } }
   if(Math.abs(vx)>0.3) keys.add(vx>0?'KeyD':'KeyA'); if(Math.abs(vy)>0.3) keys.add(vy>0?'KeyS':'KeyW');
   if(P.skill&&P.skT<=0&&d<420&&!window.__NOCAST){G.cast();bcasts++;}
   if(god){P.hp=9999;} const hb=P.hp, st0=G.boss?G.boss.st:'-'; G.tick(dt); bt+=dt; if(P.hp<hb){bloss+=hb-P.hp; HL[st0]=(HL[st0]||0)+Math.round(hb-P.hp);}
   if(G.state==='dead'){deadAt=bt;break;}
   if(P.y>1055)P.y=1055;
 }

 rec.boss={bdmg:G.boss?Math.round(G.boss.max-G.boss.hp):0,mx:G.boss?Math.round(G.boss.max):0,t:Math.round(bt*10)/10,dead:G.state==='dead',left:G.boss?Math.round(G.boss.hp):0,loss:Math.round(bloss),casts:bcasts,bk:window.__FW?'fw':(P.bossK||'monkey'),won:G.state==='win'||(!!G.boss&&G.boss.hp<=0)||(!G.boss&&G.state!=='dead'),st:G.state};
 return rec;
}