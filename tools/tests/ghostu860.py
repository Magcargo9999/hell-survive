"""v8.60 곰 후드 총령(유니크) · 토끼 후드 늑대(에픽) · 1층 원숭이 마왕 십자 균열"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.sk_ghostU&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};o.grades=[G.skinG('wolfB').grade,G.skinG('ghostU').grade,G.skinG('ghostG').grade];
          const S=G.SAVE.skin;S.own={ghostU:true};S.on={ghost:'ghostU'};G.SAVE.diff.max=0;G.SAVE.diff.sel=0;Object.assign(G.SAVE.chars,{ghost:true});
          G.startGame('ghost');G.P.form=2;o.on=!!G.skinOn('ghost');return o}""")
        print(json.dumps(R,ensure_ascii=False))
        for an in ('idle','walk','attack','skill','hit','death'):
            err=await pg.evaluate("(a)=>{const G=__G,P=G.P;P.anim=a;P.animT=0.25;try{G.render();return 0}catch(e){return String(e)}}",an)
            if an in('idle','attack'): await pg.screenshot(path=B+f'ghostu_{an}.png',clip={'x':440,'y':200,'width':400,'height':300})
            print(an,err)
        R=await pg.evaluate("""()=>{const G=__G,o={};G.startGame('wolf');const P=G.P;P.bossK='monkey';__lv(12);G.raiseCastle();G.enterArena();
          let seen=false;for(let i=0;i<30*40;i++){P.inv=99;P.hp=P.max;G.tick(1/30);const b=G.boss;if(b&&b.ex&&!o.ex)o.ex=b.ex.slice();if(b&&b.tele&&b.tele.some(t=>t.k==='rect'&&t.len===760))seen=true}
          o.crossSeen=seen;return o}""")
        print(json.dumps(R)); print('errs',pg.errs); await b.close()
asyncio.run(main())
