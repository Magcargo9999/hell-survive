"""v8.63 타락한 원예의 여왕: 15층 고정 · 패턴 순환(A·B·C) · 속박 · 포자 주머니 · 2페이즈(꽃가루 · 식인 버섯 성장/폭발) · 스크린샷"""
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
        await pg.wait_for_function('__G.IMG.qn&&__G.IMG.smap',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};o.pick=[...new Set(Array.from({length:40},()=>G.pickBossK(14)))];o.pick13=[...new Set(Array.from({length:80},()=>G.pickBossK(12)))].sort();o.pick16=[...new Set(Array.from({length:80},()=>G.pickBossK(15)))].sort();
          G.SAVE.diff.max=19;G.SAVE.diff.sel=14;G.SAVE.shards=1e7;G.startGame('wolf');const P=G.P;o.bossK=P.bossK;__lv(24);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);
          const seen={cannon:0,root:0,acid:0,lash:0,bind:0,sack:0,pool:0,spore:0},sts=[];let last='';
          for(let i=0;i<30*70;i++){P.hp=P.max;G.tick(1/30);const e=G.boss;if(!e)break;if(e.st!==last){last=e.st;if(seen[e.st]!==undefined)seen[e.st]++;sts.push(e.st)}
            if(P.bindT>0&&!o._b){o._b=1;seen.bind++}if(P.bindT<=0)o._b=0;seen.spore=Math.max(seen.spore,G.QNW.spores.length);seen.pool=Math.max(seen.pool,G.QNW.pools.length);seen.sack=Math.max(seen.sack,G.enemies.filter(q=>q.kind==='qsack').length)}
          o.seen=seen;o.seq=sts.slice(0,30).join('>');o.bossHpLeft=+(G.boss.hp/G.boss.max).toFixed(3);
          // 포자 주머니 직접 부수기
          const sk=new G.SporeSack(P.x+100,P.y);G.enemies.push(sk);G.hurtEnemy(sk,sk.max+1,0,0,0,false);o.sackKilled=sk.hp<=0&&!sk.boomed;o.dexSack=G.SAVE.dex.kills.qsack;
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("()=>{__G.render()}"); await pg.screenshot(path=B+'qn_p1.png')
        R=await pg.evaluate("""()=>{const G=__G,P=G.P,o={};const e=G.boss;e.hp=e.max*0.29;let grew=0,boom=0,maxM=0;
          for(let i=0;i<30*40;i++){P.hp=P.max;G.tick(1/30);const ms=G.enemies.filter(q=>q.kind==='qmush');maxM=Math.max(maxM,ms.length);if(ms.some(q=>q.stage===2))grew=1}
          o.ph2=e.ph2;o.pollen=!!G.QNW.pollen;o.maxMush=maxM;o.grewBomb=grew;o.st=e.st;return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("()=>{__G.render()}"); await pg.screenshot(path=B+'qn_p2.png')
        R=await pg.evaluate("""()=>{const G=__G,e=G.boss;G.hurtEnemy(e,e.hp+10,0,0,0,false);for(let i=0;i<60;i++)G.tick(1/30);return {boss:!!G.boss,left:G.enemies.filter(q=>q.kind==='qmush'||q.kind==='qsack').length,dex:G.SAVE.dex.kills.boss10}}""")
        print(json.dumps(R)); print('errs',pg.errs); await b.close()
asyncio.run(main())
# 규칙 9 확인(웅덩이·포자 주머니 최대일 때 내 주변 260px 안전 바닥 비율)은 v8.63 작업 때 따로 측정: 최소 50%
