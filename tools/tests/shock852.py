"""v8.52 열충격(점화+빙결 조합): 재료 Lv.3 두 장이면 후보에 뜨고, 점화+빙결 동시에 걸린 적이 터져 주변 피해 · 딜미터기 이름 '★열충격'"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG', timeout=90000)
        R = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P,o={};
          o.before=G.SYNERGIES.filter(s=>s.id==='shock').length;
          P.up.ignite=2;P.up.freeze=3;o.avail2=G.availSyn().some(s=>s.id==='shock');
          P.up.ignite=3;o.avail3=G.availSyn().some(s=>s.id==='shock');
          const c=G.synCard(G.SYNERGIES.find(s=>s.id==='shock'));o.card=c.name+' | '+c.sub;c.apply(P);
          G.enemies.length=0;
          const mk=(x)=>{G.spawnEnemy&&G.spawnEnemy();const e=G.enemies[G.enemies.length-1];e.x=P.x+x;e.y=P.y;e.hp=e.max=5000;return e};
          const a=mk(200),n=mk(240);a.ignT=3;G.freezeE(a,true);
          o.aHp=a.hp<5000;o.nHp=n.hp<5000;o.ign=a.ignT;o.dm=Object.keys(G.DMETER).map(k=>G.dmName(k));return o}""")
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
