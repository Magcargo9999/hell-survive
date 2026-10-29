"""v10.16 마석이 보스 러시에서도 적용되며 심장은 제외되고 새 획득분은 다음 판부터."""
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
          const G=window.__G, S=G.SAVE;
          S.diff.clr=29; S.diff.max=5; S.shards=1000000;
          S.stone={inv:[],eq:null,n:0}; S.heart.inv=[]; S.heart.eq=[];
          G.startRush('wolf');
          const base={dmg:G.P.dmg,hp:G.P.max,aspd:G.P.aspd,shard:G.runBonus().shard};
          S.stone={inv:[{id:1,g:'legend'}],eq:1,n:1};
          S.heart.inv=[{id:700,g:'legend',b:'monkey',st:'atk',v:50}];
          S.heart.eq=[700];
          G.startRush('wolf');
          const rushBonus=G.runBonus(), withStone={dmg:G.P.dmg,hp:G.P.max,aspd:G.P.aspd};
          const rushStart={dmgRatio:withStone.dmg/base.dmg,hpRatio:withStone.hp/base.hp,
            aspdDelta:withStone.aspd-base.aspd,shard:rushBonus.shard,atk:rushBonus.atk};
          G.startGame('wolf');
          const normalBonus=G.runBonus();
          S.stone={inv:[{id:1,g:'rare'}],eq:1,n:1}; S.heart.inv=[]; S.heart.eq=[];
          G.startRush('wolf');
          const rare={dmgRatio:G.P.dmg/base.dmg,hpRatio:G.P.max/base.hp,
                      aspdDelta:G.P.aspd-base.aspd,bonus:G.runBonus().atk};
          S.stone={inv:[],eq:null,n:0};
          G.startRush('wolf');
          const none={dmg:G.P.dmg,hp:G.P.max,aspd:G.P.aspd,shard:G.runBonus().shard};
          return {base,rushStart,normalBonus,rare,none};
        }""")
        def near(a, b, tol=0.002): return abs(a-b)<tol
        q=result["rushStart"]
        ok=(near(q["dmgRatio"],1.06) and near(q["hpRatio"],1.06,0.01)
            and near(q["aspdDelta"],0.06) and q["shard"]==6 and q["atk"]==6
            and result["normalBonus"]["atk"]>50
            and near(result["rare"]["dmgRatio"],1.01)
            and result["rare"]["bonus"]==1
            and near(result["none"]["dmg"],result["base"]["dmg"])
            and result["none"]["shard"]==0
            and not page.errs)
        print(json.dumps(result,ensure_ascii=False))
        print("errs",page.errs[:5])
        print("OK" if ok else "FAIL")
        await browser.close()
        if not ok: raise AssertionError("v10.16 보스 러시 마석 회귀 검증 실패")


if __name__=="__main__":
    asyncio.run(main())
