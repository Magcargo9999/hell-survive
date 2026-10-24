"""v8.57 성유물 3종: 탐욕의 주머니 · 광기의 가면 · 도박꾼의 동전"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};G.startGame('wolf');const P=G.P;P.kills=400;P.lvl=10;
          const sh0=G.calcShards(),ex0=P.expMul,tk0=P.taken,cr0=P.crit,ad0=P.cd;
          G.gainRelic('pouch');G.setState('play');o.pouch={shard:[sh0,G.calcShards()],exp:[ex0,P.expMul],taken:[tk0,P.taken]};
          G.gainRelic('coin');G.setState('play');o.coin={crit:[cr0,P.crit]};
          G.gainRelic('mask');G.setState('play');
          P.hp=P.max;o.maskHi=G.relicMaskOn();P.hp=P.max*0.5;o.maskLow=G.relicMaskOn();
          P.regen=2;P.hp=P.max*0.4;const h=P.hp;P.still=0;for(let i=0;i<30;i++)G.tick(1/30);o.regenStopped=P.hp<=h+0.01;
          P.hp=P.max*0.9;const h2=P.hp-5;P.hp=h2;for(let i=0;i<30;i++)G.tick(1/30);o.regenHi=P.hp>h2;
          o.names=Object.keys(G.RELICS);
          // 비치명타 -8%: crit 0으로 두고 같은 적 두 번 때려 비교
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        print('errs',pg.errs); await b.close()
asyncio.run(main())
