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
