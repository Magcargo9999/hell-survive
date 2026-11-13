"""v10.46 각성한 원숭이 마왕 — 이속 공정성: 같은 회피 봇(지금 보이는 예고만 보고 곧게 달릴 방향을 고른다)이 이속 140~360에서 모든 패턴을 피하는지,
그리고 터지는 순간의 여유 거리(px)를 이속 × 예고 배율로 나눈 값이 이속과 무관하게 비슷한지 잰다."""
import asyncio, json, sys
from playwright.async_api import async_playwright
from h301 import newpage
from amk1046 import START
BOT = r"""(arg)=>{const [pat,S,ox,oy,ph,lag]=arg;const G=__G,P=G.P,e=G.boss,A=G.amk,W=G.AMW,M=G.IMAP;const cx=(M.X0+M.X1)/2,cy=(M.Y0+M.Y1)/2;
 e.tele=[];A.q=[];W.cracks=[];W.waves=[];W.clones=[];W.fx=[];e.hide=false;e.jh=0;A.lp=null;e.ph=ph;e.hp=e.max*(ph===2?0.45:0.9);e.x=cx;e.y=cy;e.invul=false;
 P.x=cx+ox;P.y=cy+oy;P.spd=S;P.slowT=0;P.max=1e6;P.hp=1e6;P.shield=0;P.dodge=0;P.up.guard=0;P.pals=null;P.pet=null;P.rel={};
 A.chase(99);for(const k in A.cd)A.cd[k]=99; A.k=G.amkK(); if(pat==='claw')A.clawStart();else A[pat+'Start']();
 const pad=8+18, K=A.k; let hits=0, minC=1e9, fr=0;
 const clr=(t,x,y)=>{ // 모양 밖으로 얼마나 나와 있나 (+면 안전)
   if(t.k==='circle')return Math.hypot(x-t.x,y-t.y)-t.r;
   if(t.k==='donut'){const d=Math.hypot(x-t.x,y-t.y);return Math.max(t.r-d,d-t.r2);}
   if(t.k==='rect'){const dx=x-t.x,dy=y-t.y,c=Math.cos(t.ang),s=Math.sin(t.ang),al=dx*c+dy*s,pe=-dx*s+dy*c;return Math.max(-al,al-t.len,Math.abs(pe)-t.w/2);}
   if(t.k==='fan'){const dx=x-t.x,dy=y-t.y,d=Math.hypot(dx,dy);let da=Math.atan2(dy,dx)-t.ang;while(da>Math.PI)da-=6.283;while(da<-Math.PI)da+=6.283;return Math.min(d-56,Math.max(d-t.len,(Math.abs(da)-t.half)*Math.max(d,1)));}   // 몸 한가운데(반경 약 50)는 각도와 상관없이 맞는다
   return 1e9;};
 const dt=1/60;
 while(fr++<60*14){
   const T=e.tele.filter(t=>!t.done&&(t.fire||t.k==='rect')&&t.t>=(lag||0)*t.dur);   // lag: 예고의 앞부분을 못 본 척한다(반응 지연)
   // 방향 고르기: 가만히 / 24방향 — 각 예고가 터질 때의 내 자리에서 가장 덜 위험한 쪽
   let best=null,bv=-1e9;
   for(let i=-1;i<24;i++){const a=i*6.283/24,ux=i<0?0:Math.cos(a),uy=i<0?0:Math.sin(a);let v=1e9,ok=true;
     for(const t of T){const tau=Math.max(0,t.dur-t.t),x=P.x+ux*S*tau,y=P.y+uy*S*tau;if(!G.inPoly(x,y)){ok=false;break}v=Math.min(v,clr(t,x,y));}
     if(!ok)continue; if(i<0&&v>=pad+6){best=[0,0];bv=v;break} if(v>bv+(best&&best[0]===0&&best[1]===0?0:0.01)){bv=v;best=[ux,uy];}}
   if(best&&(best[0]||best[1])){const nx=P.x+best[0]*S*dt,ny=P.y+best[1]*S*dt;if(G.inPoly(nx,ny)){P.x=nx;P.y=ny}P.vx=best[0]*S;P.vy=best[1]*S}else{P.vx=0;P.vy=0}
   for(const t of T)if(t.fire&&t.dur-t.t<=dt*1.01)minC=Math.min(minC,clr(t,P.x,P.y));
   P.inv=0;P.hitT=0;P.stunT=0;const vx=P.vx,vy=P.vy;G.tick(dt);P.vx=vx;P.vy=vy;if(P.inv>0.3)hits++;
   if(G.state!=='play')break;
   if((e.st==='chase'||e.st==='recover')&&!e.tele.length&&!W.waves.length&&!W.clones.length&&!A.q.length)break;
 }
 return {hits,minC:Math.round(minC),K:+K.toFixed(2),norm:+(minC/(S*K)).toFixed(3),sec:+(fr/60).toFixed(1)}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        print(await pg.evaluate(START, 'wolf'))
        await pg.evaluate("()=>{for(let i=0;i<90;i++){__G.P.hp=__G.P.max;__G.P.inv=1;__G.tick(1/30)}}")
        bad = 0; SP = (140, 200, 280, 360); CASES = [('claw', 1, [(110, 0), (0, 120), (-90, -70)]), ('claw', 2, [(240, 0), (110, 0)]), ('shatter', 1, [(120, 0), (150, 0), (400, 0), (0, 700)]), ('shatter', 2, [(120, 0), (300, 0)]),
                              ('whirl', 1, [(110, 0), (0, -110), (300, 0)]), ('pillar', 1, [(110, 0), (300, 200)]), ('leap', 1, [(320, 0), (0, 500)]), ('phantom', 2, [(240, 0), (0, 300), (-500, -200)])]
        for lag in (0.2, 0.35, 0.5):   # 반응이 늦을 때: 맞는 횟수가 이속과 무관하게 같은지
            tot = {S: 0 for S in SP}
            for pat, ph, offs in CASES:
                for ox, oy in offs:
                    for S in SP: tot[S] += (await pg.evaluate(BOT, [pat, S, ox, oy, ph, lag]))['hits']
            print(f'반응 지연 {int(lag * 100)}% → 이속별 맞은 횟수', tot)
        for pat, ph, offs in CASES:
            for ox, oy in offs:
                row = []
                for S in (140, 200, 280, 360):
                    r = await pg.evaluate(BOT, [pat, S, ox, oy, ph, 0]); row.append(r); bad += r['hits']
                print(f"{pat:8s} ph{ph} ({ox:4d},{oy:4d})  " + '  '.join(f"S{S}: hit {r['hits']} 여유 {r['minC']:4d}px K{r['K']} ({r['sec']}s)" for S, r in zip((140, 200, 280, 360), row)))
        print('TOTAL HITS', bad, 'errs', pg.errs)
        await b.close()
asyncio.run(main())
