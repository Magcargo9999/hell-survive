"""v8.61 지옥 고르기 (5층 묶음): 탭·층 버튼·잠금·참가비·스크린샷"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,800)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={},$=id=>document.getElementById(id);G.SAVE.diff.max=12;G.SAVE.diff.sel=0;G.SAVE.shards=400;G.updateDiff();
          o.tabs=[...$('hellTabs').children].map(b=>b.textContent+(b.disabled?'(X)':''));
          $('hellTabs').children[2].click();o.sel1=G.SAVE.diff.sel;   // 3지옥: 13층(=12)은 참가비 300 → 가능
          G.SAVE.shards=100;$('hellTabs').children[1].click();o.sel2=G.SAVE.diff.sel;   // 2지옥: 100조각이면 4(지하5층)… 2지옥 최소 5 = 125 → 못감
          o.hint=$('hint').textContent;G.SAVE.shards=9999;$('hellTabs').children[1].click();o.sel3=G.SAVE.diff.sel;
          $('hellFloors').children[1].click();o.sel4=G.SAVE.diff.sel;o.floors=[...$('hellFloors').children].map(b=>b.textContent);o.txt=$('diffTxt').textContent;return o}""")
        print(json.dumps(R,ensure_ascii=False))
        await pg.evaluate("document.getElementById('hellRow').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300); await pg.screenshot(path=B+'hell861.png'); print('errs',pg.errs); await b.close()
asyncio.run(main())
