"""v9.10 마하칼 루드라 (지하 23층 100% · 24층 70%)
 확률 · 패턴 순환 · 업보의 염주(투사체 흡수 · 마왕 피해 흡수 · 폭발) · 침묵의 진언(통로 · 기본 공격 봉인 · 스킬 반사) · 만트라 · 청련 ·
 2페이즈 8자 질주 + 지뢰(바깥 안전 지대) · 처치 · 업적 · 층 개방 · 스크린샷"""
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
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.ifloor&&__G.IMG.rud',timeout=90000)
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.silImm=0}}")
        R=await pg.evaluate("""()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.r22=cnt(21,'rud');o.r23=cnt(22,'rud');o.r24=cnt(23,'rud');o.b24=cnt(23,'bear');o.r25=cnt(24,'rud');o.open=G.OPEN_TIER;
          G.SAVE.diff.max=23;G.SAVE.diff.sel=22;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;o.tier=P.tier;o.bossK=P.bossK;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);"""+STEP+"""const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.ice=!!(G.arena&&G.arena.ice);
          const seen={},sts=[];let last='';
          for(let i=0;i<30*90;i++){P.hp=P.max;P.inv=1;bo.hp=Math.max(bo.max*0.6,Math.min(bo.hp,bo.max*0.95));G.tick(1/30);"""+STEP+"""const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,26).join('>');return o}""")
        print('A',json.dumps(R,ensure_ascii=False))
        # 업보의 염주
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.rd;for(const k in AI.cd)AI.cd[k]=99;G.RDW.wave=null;G.RDW.lines=[];G.RDW.lotus=[];G.RDW.petals=[];G.RDW.beads=[];e.tele=[];P.silT=0;P.silImm=0;
          P.x=G.IMAP.cx;P.y=G.IMAP.cy+300;e.x=G.IMAP.cx;e.y=G.IMAP.cy-400;e.st='chase';e.stT=99;AI.karma();o.n=G.RDW.beads.length;
          for(let i=0;i<30;i++){P.hp=P.max;G.tick(1/30);}
          const b0=G.RDW.beads[0];o.on=b0.on;o.sep=Math.round(Math.min(...G.RDW.beads.slice(1).map(q=>Math.hypot(q.x-b0.x,q.y-b0.y))));
          // 투사체: 염주 옆을 지나가는 화살이 휘어 삼켜진다
          const sh={x:b0.x-200,y:b0.y-30+120,vx:600,vy:0,life:2,pierce:1,hit:new Set(),dmg:10,arrow:true,sz:1};G.shards.push(sh);let eaten=-1;for(let i=0;i<40;i++){G.tick(1/30);if(!G.shards.includes(sh)){eaten=i;break}}o.shotEaten=eaten;o.n1=b0.n;
          // 마왕이 염주 둘레 안: 피해 0 · 업보 +1 / 밖: 피해 들어감
          e.x=b0.x+40;e.y=b0.y+20;const h0=e.hp;G.hurtEnemy(e,500,0,0,0);o.inAura=Math.round(h0-e.hp);o.n2=b0.n;G.hurtEnemy(e,500,0,0,0,true);o.n3=b0.n;
          e.x=G.IMAP.cx;e.y=G.IMAP.Y1-150;for(const q of G.RDW.beads)if(Math.hypot(q.x-e.x,q.y-e.y)<400){q.x+=900}const h1=e.hp;G.hurtEnemy(e,500,0,0,0);o.outAura=Math.round(h1-e.hp);
          // 가득 채우면 2.5초 뒤 폭발 · 반경 밖은 안전 / 안은 35%
          P.x=b0.x+G.RD.bmR+80;P.y=b0.y;b0.eat(99);o.boom=+b0.boom.toFixed(1);o.ex=G.rdExPause(e);let hp=P.hp=P.max;for(let i=0;i<30*3.4;i++){P.x=b0.x+G.RD.bmR+80;P.y=b0.y;G.tick(1/30);}o.outDmg=Math.round(hp-P.hp);o.gone=!G.RDW.beads.includes(b0);o.boomed=G.RDW.boomed;
          const b1=G.RDW.beads[0];P.x=b1.x+100;P.y=b1.y;P.hp=P.max;__cl();b1.eat(99);for(let i=0;i<30*3.4;i++){P.x=b1.x+100;P.y=b1.y;G.tick(1/30);}o.inDmgPct=Math.round((P.max-P.hp)/P.max*100);
          // 2.5초면 가장 느린 이속(150)으로 반경 460을 벗어날 수 있나 (규칙 9)
          o.escape=Math.round(150*G.RD.bmWarn);o.bmR=G.RD.bmR;return o}""")
        print('K',json.dumps(R,ensure_ascii=False))
        # 침묵의 진언
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.rd;G.RDW.beads=[];P.hp=P.max;P.silT=0;P.silImm=0;
          e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=e.x+500;P.y=e.y;AI.penance();const w=G.RDW.wave;w.gaps=[Math.PI];   // 통로는 반대쪽
          let t=0;for(let i=0;i<30*3;i++){P.x=e.x+500;P.y=e.y;P.hp=P.max;G.tick(1/30);if(P.silT>0){t=i/30;break}}o.silAt=+t.toFixed(2);o.sil=+P.silT.toFixed(1);
          // 침묵 중: 기본 공격(화살)이 안 나간다
          const n0=G.shards.length;let shots=0;const S=new Set(G.shards);for(let i=0;i<30*2;i++){P.hp=P.max;G.tick(1/30);for(const s of G.shards)if(!S.has(s)&&!s.sk){shots++;S.add(s)}}o.shotsSilenced=shots;o.atk=P.atkTimer;
          // 스킬을 쓰면 반사 피해
          P.skT=0;P.hp=P.max;__cl();const h0=P.hp;(G.castSkill||G.cast)();o.skill=P.skill;o.reflectPct=Math.round((h0-P.hp)/P.max*100);
          // 통로 안이면 침묵 없음
          P.silT=0;P.silImm=0;G.RDW.wave=null;AI.penance();const w2=G.RDW.wave;w2.gaps=[0];P.x=e.x+500;P.y=e.y;let s2=0;for(let i=0;i<30*3;i++){P.x=e.x+500;P.y=e.y;P.hp=P.max;G.tick(1/30);if(P.silT>0)s2=1}o.inGapSil=s2;
          for(let i=0;i<30*4;i++){P.hp=P.max;G.tick(1/30);}o.after=+P.silT.toFixed(1);return o}""")
        print('S',json.dumps(R,ensure_ascii=False))
        # 만트라 · 청련
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.rd;G.RDW.wave=null;P.silT=0;
          e.x=G.IMAP.cx-500;e.y=G.IMAP.cy;P.x=e.x+300;P.y=e.y;__cl();P.hp=P.max;AI.mantra();o.lines=G.RDW.lines.length;o.mlMin=Math.round(Math.min(...G.RDW.lines.flatMap(l=>l.pts.map(q=>Math.hypot(q[0]-P.x,(q[1]-P.y)*1.2)))));o.pts=G.RDW.lines.map(l=>l.pts.length);let h=P.hp;
          for(let i=0;i<30*2;i++){P.x=e.x+300;P.y=e.y;G.tick(1/30);}o.mlHit=Math.round(h-P.hp);
          P.hp=P.max;__cl();h=P.hp;AI.lotus();o.lotus=G.RDW.lotus.length;for(let i=0;i<30*1.6;i++){G.tick(1/30);}o.ltHit=Math.round(h-P.hp);o.petals=G.RDW.petals.length;
          for(let i=0;i<30*3;i++){P.hp=P.max;G.tick(1/30);}o.left=G.RDW.lotus.length+G.RDW.petals.length;return o}""")
        print('M',json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,AI=G.rd;P.x=G.IMAP.cx+200;P.y=G.IMAP.cy+250;e.x=G.IMAP.cx-150;e.y=G.IMAP.cy-50;AI.karma();for(let i=0;i<25;i++)G.tick(1/30);G.RDW.beads.forEach((b,i)=>b.n=6+i*8);AI.penance();AI.lotus();for(let i=0;i<30;i++)G.tick(1/30);P.hp=P.max;G.render();}""")
        await pg.screenshot(path=B+'rud_p1.png')
        # 2페이즈
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss,AI=G.rd;G.RDW.beads=[];G.RDW.wave=null;G.RDW.lines=[];G.RDW.lotus=[];G.RDW.petals=[];P.silT=0;P.silImm=0;
          e.hp=e.max*0.29;P.x=G.IMAP.cx;P.y=G.IMAP.Y0+120;for(let i=0;i<5;i++){P.hp=P.max;P.inv=1;G.tick(1/30);}o.st=e.st;o.ph2=e.ph2;o.ex=G.rdExPause(e);
          const xs=[],ys=[];let quad={};let pauses=0,last='';
          for(let i=0;i<30*24;i++){P.x=G.IMAP.cx;P.y=G.IMAP.Y0+120;P.hp=P.max;P.inv=1;e.hp=Math.max(e.hp,e.max*0.2);G.tick(1/30);"""+STEP+"""if(e.st==='orbit'){xs.push(e.x);ys.push(e.y);const k=(e.x>G.IMAP.cx?'R':'L')+(e.y>G.IMAP.cy?'D':'U');quad[k]=1}if(e.st!==last){last=e.st;if(e.st==='pause')pauses++}}
          o.xr=[Math.round(Math.min(...xs)),Math.round(Math.max(...xs))];o.yr=[Math.round(Math.min(...ys)),Math.round(Math.max(...ys))];o.quad=Object.keys(quad).sort().join(',');o.pauses=pauses;
          const M=G.RDW.lotus.filter(l=>l.mine);o.mines=M.length;
          const safe=[[G.IMAP.cx,G.IMAP.Y0+120],[G.IMAP.cx,G.IMAP.Y1-120],[G.IMAP.X0+300,G.IMAP.Y0+300],[G.IMAP.X1-300,G.IMAP.Y1-300]];
          o.lobe=[[G.IMAP.cx-600,G.IMAP.cy],[G.IMAP.cx+600,G.IMAP.cy]].map(([x,y])=>M.filter(l=>Math.hypot(l.x-x,l.y-y)<150).length);o.safeMines=safe.map(([x,y])=>M.filter(l=>Math.hypot(l.x-x,l.y-y)<200).length);o.inHall=M.every(l=>G.inPoly(l.x,l.y));
          const sp=[];let px=e.x,py=e.y;return o}""")
        print('P',json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P;P.x=G.boss.x+250;P.y=G.boss.y+120;G.render();}""")
        await pg.screenshot(path=B+'rud_p2.png')
        # 지뢰 밟기 · 처치 · 업적
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={},e=G.boss;const m=G.RDW.lotus.find(l=>l.mine&&l.t>G.RD.mnArm&&l.pop<0);if(m){P.x=m.x;P.y=m.y;__cl();P.hp=P.max;const h=P.hp;G.tick(1/30);G.tick(1/30);o.mineHit=Math.round(h-P.hp)}
          G.RDW.boomed=false;delete G.SAVE.ach.done.rud_clean;delete G.SAVE.ach.done.k_rud;const k0=G.SAVE.dex.kills.boss15|0;P.inv=1;e.invul=false;G.hurtEnemy(e,e.max*5,0,0,0);for(let i=0;i<60;i++){P.hp=P.max;G.tick(1/30);}
          o.dead=!G.boss||G.boss.hp<=0;o.kills=(G.SAVE.dex.kills.boss15|0)-k0;G.achSync();o.ach=[!!G.SAVE.ach.done.k_rud,!!G.SAVE.ach.done.rud_clean];o.clear=G.RDW.beads.length+G.RDW.lotus.length;o.clr=G.SAVE.diff.clr;
          o.achN=G.ACH.filter(a=>['k_bear','k_rud','rud_clean'].includes(a.id)).length;return o}""")
        print('X',json.dumps(R,ensure_ascii=False))
        print('errs',errs[:5])
        await b.close()
asyncio.run(main())
