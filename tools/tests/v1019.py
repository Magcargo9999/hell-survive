"""v10.19 검 도깨비 심장 4등급 시트 + 혈랑 최종 진화 버프 회귀 테스트."""
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
          const G=__G, I=G.IMG;
          const img=I.hdok;
          if (!img) return {imageMissing:true};
          const g=['rare','epic','unique','legend'];
          const icons=g.map(grade=>{
            const canvas=G.heartIcon(grade,80,'dok');
            const pixels=canvas.getContext('2d').getImageData(0,0,80,80).data;
            return {grade,w:canvas.width,h:canvas.height,opaque:pixels.some((v,i)=>i%4===3 && v>0)};
          });
          G.SAVE.heart.inv=[];G.SAVE.heart.eq=[];G.SAVE.heart.n=0;
          G.heartGain('rare','dok');G.openHeart();
          const dialog=document.getElementById('hCore').innerHTML;
          return {imageMissing:false,source:[img.width,img.height],icons,
                  heartDialog:dialog.includes('검 도깨비'),
                  htmlVersion:document.documentElement.innerHTML.includes('v10.19')};
        }""")
        ok=(not result.get("imageMissing") and result["source"]==[128,128]
            and len(result["icons"])==4 and all(x["opaque"] for x in result["icons"])
            and result["heartDialog"] and not page.errs)
        print(json.dumps(result,ensure_ascii=False))
        print("errs",page.errs[:5])
        await browser.close()
        if not ok: raise AssertionError("v10.19 검 도깨비 심장 표시 실패")

if __name__=="__main__":
    asyncio.run(main())
