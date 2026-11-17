"""v10.61 종말의 쌍두천사(보스전 체험): 입장 · 패턴별 화면 · 극성 흡수/정화 · 가위질 판정 · 웅덩이 레이저 · 광륜 · 종말의 찬가 성공/실패 · 처치 · 오류"""
import asyncio, sys
from playwright.async_api import async_playwright
from h301 import newpage
START = """async (c)=>{const G=__G;G.startBossTrial('twa',c);let n=0;
  while(n++<6000){ if(__s())continue; if(G.arena&&G.boss&&G.boss.bk==='twa')break; G.P.hp=G.P.max;G.P.inv=9;G.tick(1/30); if(n%40===0)await new Promise(r=>setTimeout(r,30)); }
  const b=G.boss;if(!b)return {st:G.state,n,lv:G.P.lvl};
  const P=G.P;P.x=b.x;P.y=b.y+700;for(let i=0;i<200&&b.st==='Intro';i++){P.inv=9;G.tick(1/30);}
  return {bk:b.bk,st:b.st,x:b.x,y:b.y,hp:Math.round(b.hp),lvl:P.lvl,tier:P.tier,pan:!!G.arena.pan,img:!!G.IMG?1:0}}"""
async def shot(pg, name): await pg.wait_for_timeout(120); await pg.screenshot(path=f'build/twa/{name}.png')
FORCE = """([k,t,px,py,ph])=>{const G=__G,P=G.P,e=G.boss,A=G.twa;G.twaClear();const a2=new G.TwinAngelAI(e);G.twa=a2;
  e.ph=ph||1;e.hp=e.max*(ph===2?0.3:0.9);e.st='Idle';e.stT=99;e.invul=false;e.tele=[];
  P.x=e.x+px;P.y=e.y+py;G.cam.x=P.x;G.cam.y=P.y-200;a2.k=1;a2['enter'+k]();
  for(let i=0;i<Math.round(t*60);i++){P.inv=9;P.hp=P.max;G.tick(1/60)}
  const W=G.TWW;return {st:e.st,orbs:W.orbs.length,drops:W.drops.length,pools:W.pools.length,links:W.links.length,las:W.lasers.length,bl:!!W.blades,halo:!!W.halo,bells:W.bells.length,stig:W.stig,pol:W.pol,chg:W.chg}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1400, 820)
        print(await pg.evaluate(START, sys.argv[1] if len(sys.argv) > 1 else 'wolf'))
        await shot(pg, 'intro')
        for k, t, px, py, ph, name in (('PolarityHymn', 2.4, 0, 420, 1, 'hymn'), ('SixArmScissor', 1.0, 0, 380, 1, 'sc_warn'), ('SixArmScissor', 1.75, 0, 380, 1, 'sc_sweep'), ('SixArmScissor', 2.8, 0, 380, 1, 'sc_rest'),
                                       ('BloodTearResonance', 0.6, 0, 600, 1, 'tear_drop'), ('BloodTearResonance', 2.6, 0, 600, 1, 'tear_pool'), ('HaloGuillotine', 0.6, 0, 520, 1, 'halo_warn'), ('HaloGuillotine', 3.0, 0, 520, 1, 'halo_spin'), ('HaloGuillotine', 7.9, 0, 700, 1, 'halo_eject'),
                                       ('ApocalypseChant', 3.5, 0, 450, 2, 'chant'), ('PalmStrike', 0.6, 60, 160, 1, 'palm')):
            r = await pg.evaluate(FORCE, [k, t, px, py, ph]); print(name, r); await shot(pg, name)
        # 극성: 같은 색 흡수 → 정화 / 다른 색 피해
        r = await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();const A=new G.TwinAngelAI(e);G.twa=A;e.ph=1;e.hp=e.max*0.9;e.st='Idle';e.stT=99;e.invul=false;
          P.x=e.x;P.y=e.y+500;W.stig=true;W.pol='g';W.polT=4;W.chg=0.95;W.orbs=[{x:P.x,y:P.y,vx:0,vy:0,c:'g',t:0.5}];P.inv=0;P.hp=P.max;const h0=P.hp;G.tick(1/60);
          const r1={chg:W.chg,wing:W.wingT,hp:h0-P.hp,beam:!!W.beam};P.inv=0;W.orbs=[{x:P.x,y:P.y,vx:0,vy:0,c:'c',t:0.5}];const h1=P.hp;G.tick(1/60);r1.wrong=h1-P.hp;
          // 돌날개: 옆 −60% · 정화 중 ×1.25
          W.wingT=0;P.x=e.x+600;P.y=e.y-50;r1.side=G.twaDmgMul(e,true);P.x=e.x;P.y=e.y+500;r1.front=G.twaDmgMul(e,true);W.wingT=3;P.x=e.x+600;P.y=e.y-50;r1.wingSide=G.twaDmgMul(e,true);W.wingT=0;return r1}""")
        print('polarity', r)
        # 가위질 판정: 안전 부채꼴(가까이) 무피해 · 바깥 옆 피해 · 맨 아래 먼 끝 무피해
        for nm, px, py in (('near', 0, 180), ('side', -700, 300), ('far', 0, 1200), ('mid', 300, 600)):
            r = await pg.evaluate("""([px,py])=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();const A=new G.TwinAngelAI(e);G.twa=A;e.ph=1;e.hp=e.max*0.9;e.st='Idle';e.stT=99;
              A.k=1;A.enterSixArmScissor();A.q=[];let dm=0;for(let i=0;i<60*4;i++){P.x=e.x+px;P.y=e.y+py;P.inv=0;const h=P.hp;G.tick(1/60);dm+=Math.max(0,h-P.hp);P.hp=P.max;}return {dm:Math.round(dm),inPoly:G.inPoly(e.x+px,e.y+py)}}""", [px, py])
            print('scissor', nm, r)
        # 웅덩이 레이저: 두 웅덩이가 닿으면 레이저 · 선분 위면 피해
        r = await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();const A=new G.TwinAngelAI(e);G.twa=A;e.st='Idle';e.stT=99;
          W.pools=[{x:e.x-220,y:e.y+700,t:0,r:55,K:1,fade:false},{x:e.x+220,y:e.y+700,t:0,r:55,K:1,fade:false}];P.x=e.x;P.y=e.y+700;let dm=0,lz=0,t0=-1;
          for(let i=0;i<60*5;i++){P.inv=0;const h=P.hp;G.tick(1/60);dm+=Math.max(0,h-P.hp);P.hp=P.max;if(W.lasers.length&&t0<0){t0=i/60;lz++;}}return {t:t0,dm:Math.round(dm),links:W.links.length}}""")
        print('laser', r)
        # 광륜: 투사체 막힘
        r = await pg.evaluate("""()=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();const A=new G.TwinAngelAI(e);G.twa=A;e.st='Idle';e.stT=99;A.k=1;A.enterHaloGuillotine();for(let i=0;i<80;i++)G.tick(1/60);
          const H=W.halo,RO=G.twRingInfo(H,false);let blade=0,gap=0;for(let a=0;a<360;a+=2){const x=e.x+Math.cos(a/57.3)*295,y=e.y+Math.sin(a/57.3)*295;if(G.twRingAt(RO,x,y,4))blade++;else gap++;}return {blade,gap}}""")
        print('halo', r)
        # 종말의 찬가 성공 / 실패
        for ok in (1, 0):
            r = await pg.evaluate("""(ok)=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();const A=new G.TwinAngelAI(e);G.twa=A;e.ph=1;e.hp=e.max*0.34;e.st='Idle';e.stT=99;e.invul=false;
              P.x=e.x;P.y=e.y+500;for(let i=0;i<60*2.5;i++){P.inv=9;P.hp=P.max;G.tick(1/60);}
              const bells=W.bells.slice();if(ok){for(const b of bells.slice(0,4))for(let h=0;h<3;h++){b.hitT=0;G.hurtEnemy(b,10,0,0,0,false);}}
              const hp0=P.max;let st=[];for(let i=0;i<60*16;i++){P.inv=0;if(i===0)P.hp=hp0;G.tick(1/60);if(!st.includes(e.st))st.push(e.st);if(e.st!=='ApocalypseChant')break;}
              return {ok,bells:bells.length,broken:bells.filter(b=>b.broken).length,st:e.st,fall:W.fallT,hpPct:Math.round(P.hp/P.max*100),seen:st}}""", ok)
            print('chant', r)
            if ok: await shot(pg, 'exposed')
        # 실제 전투: 무적으로 자동 공격하며 끝까지
        r = await pg.evaluate("""async()=>{const G=__G,P=G.P,e=G.boss,W=G.TWW;G.twaClear();G.twa=new G.TwinAngelAI(e);P.hp=P.max;e.hp=e.max;e.ph=1;e.st='Idle';e.stT=0.5;e.tele=[];const seen={};let n=0;
          while(n++<60*500&&G.state==='play'&&e.hp>0){P.inv=1;P.hp=P.max;seen[e.st]=1;const bs=W.bells.filter(b=>!b.broken&&!b.invul);if(bs.length&&n%20===0){bs[0].hitT=0;G.hurtEnemy(bs[0],10,0,0,0,false);}
            if(n%15===0&&!e.invul){e.hp-=e.max*0.0012;} if(e.hp<=0){G.bossDefeated(e);break;} G.tick(1/60); if(n%600===0)await new Promise(r=>setTimeout(r,5));}
          return {n,state:G.state,hp:Math.round(e.hp),seen:Object.keys(seen)}}""")
        print('fight', r)
        await pg.evaluate("()=>{for(let i=0;i<60;i++)__G.tick(1/30)}"); await shot(pg, 'death')
        print('errs', pg.errs); await b.close()
if __name__ == "__main__": asyncio.run(main())
