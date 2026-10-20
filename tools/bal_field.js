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
 if(window.__FW){ G.SAVE.fw.snap=G.snapP(); G.SAVE.fw.open=true; G.startFw(); P=G.P; for(let i=0;i<110;i++){ G.tick(dt); } } else { G.enterArena(); for(let i=0;i<110;i++){ pump(); G.tick(dt); } }
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
 while(bt<DUR && G.boss && G.state==='play'){
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