"""v10.13: 스킨 가챠 뽑기권 수량 0장/양수 표시, 보스 심장에서는 숨김."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await h301.newpage(browser, 1280, 720)
        await page.wait_for_timeout(1500)
        result = await page.evaluate("""() => {
          const G = window.__G;
          G.SAVE.rush.tix = 0;
          openGacha('pull');
          const zero = document.getElementById('gTix').textContent;
          G.SAVE.rush.tix = 3;
          renderGacha();
          const three = document.getElementById('gTix').textContent;
          const oneButton = document.getElementById('gOne').textContent;
          const shardsText = document.getElementById('gShards').textContent;
          openHeart();
          const heartText = document.getElementById('hStone').textContent;
          G.SAVE.rush.tix = 2;
          renderGacha();
          return {zero, three, oneButton, shardsText, heartText,
                  two: document.getElementById('gTix').textContent,
                  count: G.SAVE.rush.tix};
        }""")
        passed = (("0장" in result["zero"])
                  and ("3장" in result["three"])
                  and ("남은 3" in result["oneButton"])
                  and ("뽑기권" not in result["heartText"])
                  and ("주사기" in result["heartText"])
                  and ("마석" in result["heartText"])
                  and ("뽑기권" not in result["shardsText"])
                  and ("2장" in result["two"])
                  and result["count"] == 2
                  and not page.errs)
        print(json.dumps(result, ensure_ascii=False))
        print("OK" if passed else "FAIL")
        print("errs", page.errs[:5])
        await browser.close()
        if not passed:
            raise AssertionError("v10.13 가챠/심장 UI 회귀 테스트 실패")


if __name__ == "__main__":
    asyncio.run(main())
