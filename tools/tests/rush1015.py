"""v10.15: 보스 러시 진화 잠금 해제, 타락한 혈랑 표시, 일반 모드 회귀 확인."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
import h301

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await h301.newpage(browser, 1280, 720)
        await page.wait_for_timeout(1200)
        result = await page.evaluate("""() => {
          const G = window.__G;
          G.SAVE.diff.clr = 29; G.SAVE.chars.wolf = true;
          G.SAVE.fw.open = false; G.SAVE.fw.cleared = false;
          G.SAVE.holyBlood = false;
          G.startGame('wolf');
          Object.assign(G.P.up, {thirst:0, speed:0, heart:0});
          const keys = [['wolf','crimson'],['wolf','twin'],['wolfFin','holy'],
              ['snail','lava'],['chimera','dream'],['archer','skel'],
              ['archerFin','holy'],['lizard','guard'],['lizardFin','rage']];
          const normal = keys.map(([g,k]) => !!condItem(g,k).locked);
          G.P.route = 'crimson'; G.P.fin = null; openFinal();
          const hiddenNormal = G.choices.some(x=>x.key==='fallen');
          G.startRush('wolf');
          Object.assign(G.P.up, {thirst:0,speed:0,heart:0});
          const free = keys.map(([g,k]) => {
              const x=condItem(g,k); return !x.locked && x.tag?.includes('자유 진화');
          });
          G.P.route='crimson'; G.P.fin=null; openFinal();
          const hiddenRush=G.choices.find(x=>x.key==='fallen');
          const hint=document.getElementById('levelHint').textContent;
          G.P.route=null; openRoute();
          const wolf=G.choices.map(x=>({key:x.key,locked:!!x.locked}));
          return {normal,hiddenNormal,free,hiddenRush:!!hiddenRush,
                  hiddenLocked:!!hiddenRush?.locked,hint,wolf};
        }""")
        ok = (all(result["normal"]) and not result["hiddenNormal"]
              and all(result["free"]) and result["hiddenRush"]
              and not result["hiddenLocked"] and all(not x["locked"] for x in result["wolf"])
              and "조건 없이" in result["hint"] and not page.errs)
        print(json.dumps(result,ensure_ascii=False))
        print("errs",page.errs[:5])
        await browser.close()
        if not ok: raise AssertionError("보스 러시 진화 해금 회귀 실패")

if __name__ == "__main__":
    asyncio.run(main())
