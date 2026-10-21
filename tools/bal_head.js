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
