"""v6.50 지하 10층: 난이도 UI 0~9 · 해금 · 층별 보스전 오류 없음  PYTHONPATH=tools python3 tools/tests/tier10.py"""
import asyncio, json
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        r = await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=99999;G.SAVE.diff.max=5;G.SAVE.diff.sel=5;
          const out={};const pl=document.getElementById('diffPlus');for(let i=0;i<8;i++)pl.click();
          out.sel=G.SAVE.diff.sel;out.txt=document.getElementById('diffTxt').textContent;out.desc=document.getElementById('diffDesc').textContent;
          G.SAVE.diff.max=9;for(let i=0;i<8;i++)pl.click();out.sel2=G.SAVE.diff.sel;out.txt2=document.getElementById('diffTxt').textContent;out.desc2=document.getElementById('diffDesc').textContent;return out}""")
        print(json.dumps(r, ensure_ascii=False))
        for bk in ['monkey', 'eye', 'skel', 'angel']:
            r = await pg.evaluate("""(bk)=>{const G=__G;G.SAVE.shards=99999;G.SAVE.diff.max=9;G.SAVE.diff.sel=9;G.startGame('wolf');const P=G.P;P.bossK=bk;P.tier=9;
              __lv(8);G.enterArena&&0;G.raiseCastle&&0;G.spawnBoss();const b=G.boss;if(!b)return {nb:1};
              let min=1e9;for(let i=0;i<600;i++){P.inv=99;P.hp=P.max;G.tick(1/30)}
              return {bk,tier:P.tier,bossHp:Math.round(b.max),mobHp:G.enemies[0]?Math.round(G.enemies[0].max):0,state:G.state}}""", bk)
            print(r)
        r = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;P.tier=5;const a=G.SAVE.diff.max;G.SAVE.diff.max=5;P.tier=5;G.spawnBoss();G.bossDefeated();const m5=G.SAVE.diff.max;
          G.SAVE.diff.max=8;G.startGame('wolf');G.P.tier=8;G.spawnBoss();G.bossDefeated();return {after5:m5,after8:G.SAVE.diff.max,unlocked:G.P.unlocked}}""")
        print(r, 'errs', pg.errs)
        await b.close()
asyncio.run(main())
