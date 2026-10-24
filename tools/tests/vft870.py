"""v8.70 파리지옥 마왕: 11층 100% · 12층 70% · 패턴 순환(A 포자·B 유혹·C 덫·D 해골) · 흡혈 · 출혈 · 매혹 · 2페이즈(붉은 안개 · 하트 파동 통로 · 덫 3연속) · 스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        await pg.wait_for_function('__G.IMG.vft&&__G.IMG.gmap',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};const cnt=t=>{const c={};for(let i=0;i<4000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1}return Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/40)]))};
          o.p11=cnt(10);o.p12=cnt(11);o.p13=cnt(12);o.p17=cnt(16);o.p18=cnt(17);
          G.SAVE.diff.max=19;G.SAVE.diff.sel=10;G.SAVE.shards=1e7;G.startGame('wolf');const P=G.P;o.bossK=P.bossK;__lv(24);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);o.gard=!!(G.arena&&G.arena.gard);
          const seen={spray:0,lure:0,trap:0,skull:0,bite:0,charm:0,bleed:0,maxTrap:0,maxSkull:0,maxSpore:0,stun:0},sts=[];let last='',c0=0,b0=0,s0=0;
          for(let i=0;i<30*75;i++){P.hp=P.max;bo.hp=Math.min(bo.hp,bo.max*0.95);G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;if(seen[e.st]!==undefined)seen[e.st]++;sts.push(e.st)}
            if(P.charmT>0&&!c0)seen.charm++;c0=P.charmT>0;if(P.bleedT>0&&!b0)seen.bleed++;b0=P.bleedT>0;if(P.stunT>0&&!s0)seen.stun++;s0=P.stunT>0;
            seen.maxTrap=Math.max(seen.maxTrap,G.VFW.traps.length);seen.maxSkull=Math.max(seen.maxSkull,G.enemies.filter(q=>q.kind==='vskull').length);seen.maxSpore=Math.max(seen.maxSpore,G.VFW.spores.length)}
          o.seen=seen;o.seq=sts.slice(0,24).join('>');o.leech=Math.round(G.VFW.leech||0);o.leechPct=+((G.VFW.leech||0)/bo.max*100).toFixed(1);
          const sk=new G.VfSkull(P.x+100,P.y);sk.rise=0;G.enemies.push(sk);G.hurtEnemy(sk,sk.max+1,0,0,0,false);o.skullKilled=sk.hp<=0&&!(G.VFW.fx.some(q=>q.k==='sboom'&&Math.hypot(q.x-sk.x,q.y-sk.y)<2));o.dexSkull=G.SAVE.dex.kills.vskull;
          // 흡혈: 내 최대 체력 50%를 잃으면 보스 최대 체력의 3%
          bo.hp=bo.max*0.5;G.vfLeech(P.max*0.5);o.leech50=+((bo.hp/bo.max-0.5)*100).toFixed(2);
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P;for(let i=0;i<300;i++){P.hp=P.max;G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();if(G.VFW.traps.some(t=>t.state==='warn')&&G.VFW.spores.length)break}G.render()}"""); await pg.screenshot(path=B+'vft_p1.png')
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={};const e=G.boss;e.hp=e.max*0.29;let waves=0,wl=null;
          for(let i=0;i<30*4;i++){P.hp=P.max;G.tick(1/30)}o.ph2=e.ph2;o.fog=!!G.VFW.fog;o.cyc=G.vf&&G.vf.cyc.join(',');
          // 하트 파동 통로 시험: 통로 방향에 서 있으면 안 걸리고, 통로 밖이면 매혹 + 덫 3연속
          const test=(inGap)=>{for(const k in G.vf.cd)G.vf.cd[k]=99;e.st='chase';e.stT=99;e.tele=[];G.VFW.spores=[];G.VFW.traps=[];P.charmT=0;P.charmImm=0;P.inv=0;P.shield=0;const w={x:e.x,y:e.y,t:0,r:0,gaps:[0.3,2.394,4.488],hit:false};G.VFW.wave=w;const a=inGap?0.3:1.35,d=300;P.x=e.x+Math.cos(a)*d;P.y=e.y+Math.sin(a)*d/1.5;
            let ch=0,combo=0,bites=0,h0=0;for(let i=0;i<30*2.5;i++){P.hp=P.max;if(!P.charmT)P.inv=0;const sx=P.x,sy=P.y;G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();if(!P.charmT){P.x=sx;P.y=sy}if(P.charmT>0)ch=1;combo=Math.max(combo,G.VFW.traps.filter(t=>t.combo).length)}for(let i=0;i<30*2;i++){const hb=P.hp;G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();if(P.hp<hb-P.max*0.2)bites++;P.hp=P.max}return {ch,combo,bites}};
          o.gap=test(true);o.noGap=test(false);
          let maxSkull=0;for(let i=0;i<30*30;i++){P.hp=P.max;P.inv=1;G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();maxSkull=Math.max(maxSkull,G.enemies.filter(q=>q.kind==='vskull').length);if(G.VFW.wave&&G.VFW.wave.t<0.6)waves=1}
          o.wave=waves;o.maxSkull2=maxSkull;o.st=e.st;return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("""()=>{const G=__G,P=G.P;for(let i=0;i<600;i++){P.hp=P.max;P.inv=1;G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();if(G.VFW.wave&&G.VFW.wave.t>0.5&&G.VFW.wave.t<0.9)break}G.render()}"""); await pg.screenshot(path=B+'vft_p2.png')
        R=await pg.evaluate("""()=>{const G=__G,e=G.boss;G.hurtEnemy(e,e.hp+10,0,0,0,false);for(let i=0;i<60;i++)G.tick(1/30);if(G.state!=='play'&&G.state!=='over')__s();return {boss:!!G.boss,left:G.enemies.filter(q=>q.kind==='vskull').length,dex:G.SAVE.dex.kills.boss11,charm:G.P.charmT,bleed:G.P.bleedT}}""")
        print(json.dumps(R)); print('errs',pg.errs); await b.close()
asyncio.run(main())
