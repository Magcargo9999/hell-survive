"""v10.58 화염 충격파: 시너지 카드가 나오고(충격파+불길 오라) · 충격파에 맞은 적이 0.5초 뒤 폭발 · 보스는 체력비례 추가"""
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
from amk1046 import START
JS = """()=>{const G=__G,P=G.P,b=G.boss;P.syn.blastwave=true;P.up.nova=3;P.up.aura=2;P.dmg=30;b.invul=false;b.x=P.x+60;b.y=P.y;b.st='intro';b.stT=99;b.invul=false;
 const mx=b.max;b.hp=mx;G.castNova({R:300,cd:5,dm:1.0});const h1=b.hp;
 for(let i=0;i<10;i++){b.invul=false;G.tick(1/60)}const h2=b.hp;for(let i=0;i<40;i++){b.invul=false;G.tick(1/60)}const h3=b.hp;
 return {bwT:b.bwT,cardHas:G.SYNERGIES.some(s=>s.id==='blastwave'),maxHp:mx,nova:Math.round(mx-h1),afterWait:Math.round(mx-h2),afterBoom:Math.round(mx-h3),boomPct:+((h2-h3)/mx*100).toFixed(3)}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.evaluate(START, 'wolf')
        print(await pg.evaluate(JS)); print('errs', pg.errs); await b.close()
asyncio.run(main())
