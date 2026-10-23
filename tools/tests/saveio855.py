"""v8.55 세이브 옮기기: 파일 저장 · 코드 복사(gzip) · 불러오기(파일/코드) · 잘못된 입력 · 백업 · 스크린샷"""
import asyncio,sys,json,os
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); ctx=await b.new_context(accept_downloads=True,viewport={'width':1280,'height':800},permissions=['clipboard-read','clipboard-write'])
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(h301.URL); await pg.wait_for_function('window.__G&&__G.IMG&&__G.IMG.boss',timeout=90000)
        await pg.evaluate("()=>{const G=__G;G.SAVE.shards=4321;G.SAVE.chars.octo=true;G.SAVE.diff.max=7;G.SAVE.playT=7200;G.SAVE.dex.kills.bug=99;G.saveSave()}")
        await pg.evaluate("()=>{window.confirm=()=>true}")
        # 파일 저장
        await pg.click('#setBtn')
        async with pg.expect_download() as d: await pg.click('#svFile')
        dl=await d.value; path=B+'save_test.json'; await dl.save_as(path); j=json.load(open(path)); print('file',dl.suggested_filename,j['game'],j['save']['shards'])
        # 코드 복사
        await pg.click('#svCopy'); code=await pg.input_value('#svCode'); print('code',code[:8],len(code)); print('msg',await pg.inner_text('#svMsg'))
        # 세이브 바꿔 놓고 코드로 복구
        await pg.evaluate("()=>{const G=__G;G.SAVE.shards=1;G.saveSave()}")
        await pg.evaluate("()=>{window.__reloaded=0}")
        r=await pg.evaluate("""async(c)=>{const t=document.getElementById('svCode');t.value=c;let reloaded=false;const j=await __G.svParse(c);return {shards:j.save.shards,octo:j.save.chars.octo,dk:j.save.dex.kills.bug}}""",code)
        print('parse',r)
        bad=await pg.evaluate("""async()=>{const o=[];for(const t of ['','abc','{"a":1}','HS1:@@@','HS1z:AAAA']){try{await __G.svParse(t);o.push('ok?')}catch(e){o.push('err')}}return o}""")
        print('bad',bad)
        # 실제 불러오기 (reload 포함)
        await pg.fill('#svCode',code)
        async with pg.expect_navigation(timeout=90000): await pg.click('#svLoadC')
        await pg.wait_for_function('window.__G&&__G.SAVE',timeout=90000)
        print('after',await pg.evaluate("()=>({s:__G.SAVE.shards,octo:__G.SAVE.chars.octo,max:__G.SAVE.diff.max,bak:JSON.parse(localStorage.getItem('hellSurvivorSave1_bak')).shards})"))
        await pg.click('#setBtn'); await pg.screenshot(path=B+'saveio.png')
        print('errs',errs); await b.close()
asyncio.run(main())
