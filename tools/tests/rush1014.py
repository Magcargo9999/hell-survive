"""v10.14 보스 러시: 이동속도 카드 제외 / 기본 이속 하한 소폭 상향, 일반 모드 유지."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
import h301


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await h301.newpage(browser, 1280, 720)
        await page.wait_for_timeout(1500)
        result = await page.evaluate("""() => {
          const G = window.__G;
          G.SAVE.diff.clr = 29;
          G.SAVE.diff.max = 5;
          G.SAVE.shards = 1000000;
          G.startGame('wolf');
          const normal = G.cardDefs().some(u => u.id === 'move');
          const normalHint = G.cardView(G.cardDefs().find(u => u.id === 'speed')).syn;
          G.startRush('wolf');
          const rushHasMove = G.cardDefs().some(u => u.id === 'move');
          const rushHint = G.cardView(G.cardDefs().find(u => u.id === 'speed')).syn;
          const initialMove = G.choices.some(u => u.id === 'move');
          const min = BR.spdMin, max = BR.spdMax;
          let steps = 0;
          while (steps++ < 1000) {
            if (G.state === 'levelup' && document.getElementById('levelTitle').textContent.includes('몇 개')) {
              G.pick(0); continue;
            }
            if (window.__s()) continue;
            if (G.state === 'play' && G.rush && G.rush.init) {
              G.tick(1 / 30); continue;
            }
            break;
          }
          const state = G.state, level = G.P.lvl;
          G.P.spd = 100;
          G.tick(1 / 30);
          const effectiveLow = G.P.espd;
          G.P.spd = 1000;
          G.tick(1 / 30);
          const effectiveHigh = G.P.espd;
          G.startGame('wolf');
          const regularAfter = G.cardDefs().some(u => u.id === 'move');
          return {normal, normalHint, rushHasMove, rushHint, initialMove,
                  min, max, state, level, effectiveLow, effectiveHigh, regularAfter, steps};
        }""")
        passed = (result["normal"]
                  and result["regularAfter"]
                  and not result["rushHasMove"]
                  and not result["initialMove"]
                  and "질주" in result["normalHint"]
                  and "질주" not in result["rushHint"]
                  and result["min"] == 250
                  and result["max"] == 290
                  and result["state"] == "play"
                  and result["level"] >= 20
                  and 249 <= result["effectiveLow"] <= 251
                  and 289 <= result["effectiveHigh"] <= 291
                  and not page.errs)
        print(json.dumps(result, ensure_ascii=False))
        print("OK" if passed else "FAIL")
        print("errs", page.errs[:5])
        await browser.close()
        if not passed:
            raise AssertionError("v10.14 보스 러시 이속 카드/속도 테스트 실패")


if __name__ == "__main__":
    asyncio.run(main())
