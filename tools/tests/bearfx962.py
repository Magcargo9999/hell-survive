"""v9.62 백곰 이펙트 도트 — 장벽·균열·빙창·눈보라·동상 스크린샷 + 게이지 규칙 + 콘솔 오류
사용: GAME_URL=http://localhost:8765/build/hell_survive.html PYTHONPATH=tools python3 tools/tests/bearfx962.py [폴더]"""
import asyncio, sys
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.bear&&__G.IMG.bearfx', timeout=90000)
        await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=21;G.SAVE.diff.sel=20;G.SAVE.shards=1e7;G.startGame('archer');__lv(28);G.raiseCastle();G.enterArena();for(let i=0;i<60;i++)G.tick(1/30);}""")
        prep = "const G=__G,P=G.P,e=G.boss;P.hp=P.max;P.inv=99;P.x=G.IMAP.cx;P.y=G.IMAP.cy;e.x=P.x+20;e.y=P.y+420;e.hp=e.max;e.st='chase';e.stT=99;for(const k in G.pb.cd)G.pb.cd[k]=99;G.PBW.walls=[];G.PBW.fis=[];G.PBW.spears=[];G.PBW.bz=null;G.PBW.fx=[];P.frzT=0;"
        async def shot(name, js, adv=0):
            await pg.evaluate("()=>{"+prep+js+"for(let i=0;i<"+str(adv)+";i++)G.tick(1/30);G.render()}")
            await pg.screenshot(path=f'{OUT}/bfx_{name}.png')
        await shot('walls', "G.pb.wq=G.pb.wallSpots();G.pb.wallRise();", 25)
        await shot('rise', "G.pb.wq=G.pb.wallSpots();G.pb.wallRise();", 5)
        await shot('crack', "G.PBW.fis.push(new G.Fissure(e.x,e.y-60,Math.atan2(P.y-e.y,P.x-e.x),0));", 6)
        await shot('spike', "G.PBW.fis.push(new G.Fissure(e.x,e.y-60,Math.atan2(P.y-e.y,P.x-e.x),0));", 21)
        await shot('spear', "G.PBW.spears.push(new G.IceSpear(P.x-300,P.y-30,0),new G.IceSpear(P.x+300,P.y-130,Math.PI));", 3)
        await shot('blizzard', "G.PBW.bz={t:1,ux:1,uy:0,shade:false};G.PBW.frost=60;", 3)
        await shot('frozen', "G.PBW.frost=0;G.FrostMgr.freeze();", 3)
        # 게이지 규칙: 눈보라 없음 → 안 내려감 / 벽 근처 → 내려감
        r = await pg.evaluate("()=>{"+prep+"const o={};G.PBW.frost=50;for(let i=0;i<60;i++)G.tick(1/30);o.noWall=Math.round(G.PBW.frost);"
            "G.PBW.walls=[new G.IceWall(P.x+100,P.y,80,160,9,false)];G.PBW.walls[0].t=1;G.PBW.frost=50;for(let i=0;i<30;i++){P.inv=99;G.tick(1/30);}o.nearWall=Math.round(G.PBW.frost);"
            "G.PBW.walls=[new G.IceWall(P.x+600,P.y,80,160,9,false)];G.PBW.walls[0].t=1;G.PBW.frost=50;for(let i=0;i<30;i++){P.inv=99;G.tick(1/30);}o.farWall=Math.round(G.PBW.frost);return o}")
        print(r); print('오류:', pg.errs); await b.close()
asyncio.run(main())
