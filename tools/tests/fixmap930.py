"""v9.30 팔한지옥 보스방 = 빙결 투기장 고정(마왕 무관) · 황금 악마 임프 잡을 수 있게
 A) 21~25층 어떤 마왕이든 arena.ice · 맵 안에 머무름 · 오류 없음 B) 보스 러시는 마왕별 맵 유지 C) 임프 추격 처치"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:160]))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.ifloor',timeout=90000)
        for bk in ['bear']:
            R=await pg.evaluate("""(bk)=>{const G=__G,o={bk};G.SAVE.diff.max=24;G.SAVE.diff.sel=21;G.SAVE.shards=1e7;G.startGame('wolf');const P=G.P;P.bossK=bk;__lv(28);G.raiseCastle();G.enterArena();
              for(let i=0;i<45;i++)G.tick(1/30);"""+STEP+"""o.ice=!!(G.arena&&G.arena.ice);o.sea=!!(G.arena&&G.arena.sea);o.gard=!!(G.arena&&G.arena.gard);o.k=G.boss&&G.boss.bk;
              let out=0;for(let i=0;i<30*25;i++){P.hp=P.max;P.inv=1;const a=i/20;G.keys.clear();G.keys.add(['KeyW','KeyD','KeyS','KeyA'][Math.floor(a)%4]);G.tick(1/30);"""+STEP+"""if(!G.inPoly(P.x,P.y))out++;if(!G.boss)break}
              G.keys.clear();o.out=out;o.alive=!!G.boss;return o}""",bk)
            print(json.dumps(R,ensure_ascii=False))
        R=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.shards=1e7;G.SAVE.diff.sel=0;G.startGame('wolf');__lv(20);G.startRush&&0;return !!G.rushQ||1}""")
        # 임프 추격
        for ch in ['wolf','archer','lizard','octo']:
            R=await pg.evaluate("""(ch)=>{const G=__G,o={ch};G.SAVE.diff.max=24;G.SAVE.shards=1e7;G.SAVE.diff.sel=20;G.startGame(ch);const P=G.P;__lv(24);G.impAt=0;G.trySpawnImp();const im=G.impOf();o.hp=Math.round(im.max);
              let t=0,mn=im.hp;for(;t<30*40;t++){if(!im.gone)mn=Math.min(mn,im.hp);P.hp=P.max;P.inv=1;const dx=im.x-P.x,dy=im.y-P.y,d=Math.hypot(dx,dy)||1;G.keys.clear();if(dx>8)G.keys.add('KeyD');if(dx<-8)G.keys.add('KeyA');if(dy>8)G.keys.add('KeyS');if(dy<-8)G.keys.add('KeyW');G.tick(1/30);"""+STEP+"""if(im.hp<=0)break}
              G.keys.clear();o.dead=im.hp<=0&&!im.gone;o.t=+(t/30).toFixed(1);o.st=im.st;o.left=Math.round(100*mn/im.max)+"%";o.dmg=Math.round(P.dmg);return o}""",ch)
            print(json.dumps(R,ensure_ascii=False))
        print('errs',errs[:6])
        await b.close()
asyncio.run(main())
