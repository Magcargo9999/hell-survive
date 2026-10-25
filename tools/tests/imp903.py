"""v9.03 황금 악마 임프 · 업적 '진정한 불운의 아이콘' · 성유물 도트
 임프: 21층 미만 안 나옴 · 돌진→한 대→도망 · 처치 시 조각 +10000 + 상자 · 시간 지나면 소멸 · 업적: 재설정 10연속 등급업 실패"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.imp&&__G.IMG.relkey',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};
          G.SAVE.diff.max=21;G.SAVE.shards=1e7;G.SAVE.diff.sel=19;G.startGame('archer');let P=G.P;o.t19=P.tier;G.impAt=0;for(let i=0;i<5;i++)G.trySpawnImp();o.n19=G.enemies.filter(e=>e.kind==='imp').length;
          G.SAVE.shards=1e7;G.SAVE.diff.sel=20;G.startGame('archer');P=G.P;o.t20=P.tier;__lv(20);G.impAt=0;G.trySpawnImp();G.trySpawnImp();const im=G.impOf();o.n20=G.enemies.filter(e=>e.kind==='imp').length;o.hp=Math.round(im.max);
          const seq=[];let last='',hp0=P.hp;P.x=0;P.y=0;
          for(let i=0;i<30*3;i++){G.tick(1/30);"""+STEP+"""if(im.st!==last){last=im.st;seq.push(im.st+'@'+(i/30).toFixed(1))}if(im.hp<=0)break}
          o.seq=seq.join(' ');o.dmg=Math.round(hp0-P.hp);
          // 도망 속도 · 소멸
          const d0=Math.hypot(im.x-P.x,im.y-P.y);for(let i=0;i<30*3;i++){P.hp=P.max;G.tick(1/30);"""+STEP+"""}o.fleeD=Math.round(Math.hypot(im.x-P.x,im.y-P.y)-d0);o.st=im.st;o.life=+im.life.toFixed(1);
          for(let i=0;i<30*15;i++){P.hp=P.max;P.x=0;P.y=0;G.tick(1/30);"""+STEP+"""if(im.hp<=0)break}o.gone=im.hp<=0&&!!im.gone;o.alive=!!G.impOf();
          // 처치 보상 (새 판)
          G.startGame('archer');P=G.P;__lv(20);G.impAt=0;G.trySpawnImp();const e2=G.impOf();const s0=G.SAVE.shards,ch0=G.items.filter(i=>i.type==='chest').length,k0=G.SAVE.dex.kills.imp|0;
          e2.x=P.x+40;e2.y=P.y;e2.st='flee';G.hurtEnemy(e2,e2.max*2,1,0,0);o.shards=G.SAVE.shards-s0;o.chest=G.items.filter(i=>i.type==='chest').length-ch0;o.dexKill=(G.SAVE.dex.kills.imp|0)-k0;o.udeath=G.udeath.some(u=>u.uk==='imp');
          // 보스방 진입 시 정리
          G.impAt=0;G.impAt=0;G.trySpawnImp();o.again=!!G.impOf();return o}""")
        print('A',json.dumps(R,ensure_ascii=False))
        # 화면
        R=await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=1e7;G.SAVE.diff.sel=20;G.startGame('archer');__lv(20);G.impAt=0;G.trySpawnImp();const im=G.impOf();const P=G.P;im.x=P.x+160;im.y=P.y-20;im.st='flee';im.fled=true;im.life=9;im.face=1;for(let i=0;i<3;i++){G.tick(1/30);}G.render();return 1}""")
        await pg.screenshot(path=B+'imp_scene.png')
        # 업적: 연속 10번 재설정에서 등급업 없음
        R=await pg.evaluate("""()=>{const G=__G,o={};const S=G.SAVE;S.shards=1e7;S.heart.inv=[];S.ach.done={};S.ach.got={};S.heart.dry=0;
          const h=G.heartGain('rare','angel');const rnd=Math.random;Math.random=()=>0.99;let r;for(let i=0;i<9;i++){r=G.rerollHeart(h.id)}o.d9=S.heart.dry;o.done9=!!S.ach.done.luck;r=G.rerollHeart(h.id);o.d10=S.heart.dry;o.done10=!!S.ach.done.luck;o.achName=r.ach&&r.ach.name;
          // 등급업이 나오면 카운터 초기화
          S.ach.done={};S.heart.dry=7;Math.random=()=>0;const h2=G.heartGain('rare','shk');r=G.rerollHeart(h2.id);o.up=r.up;o.dryAfterUp=S.heart.dry;Math.random=rnd;
          // 레전더리는 등급업 불가 → 카운터 안 오름
          h2.g='legend';S.heart.dry=3;G.rerollHeart(h2.id);o.dryLegend=S.heart.dry;
          // 보상
          S.ach.done={luck:1};S.ach.got={};G.openAch();o.rows=document.querySelectorAll('#achList .achrow').length;o.txt=[...document.querySelectorAll('#achList .achrow')].filter(r=>r.textContent.includes('불운')).map(r=>r.textContent.replace(/\\s+/g,' ')).join('|');
          const btn=[...document.querySelectorAll('#achList .achrow')].find(r=>r.textContent.includes('불운')).querySelector('button');const s1=S.shards;btn.click();o.reward=S.shards-s1;
          // 업적 목록에서 불운은 처음에 자동 달성되지 않는다
          S.ach.done={};G.achSync();o.autoDone=!!S.ach.done.luck;return o}""")
        print('B',json.dumps(R,ensure_ascii=False))
        # 성유물 아이콘
        R=await pg.evaluate("""()=>{const G=__G;const c=document.createElement('canvas');c.width=300;c.height=100;const g=c.getContext('2d');g.fillStyle='#240a30';g.fillRect(0,0,300,100);['key','phoenix','fang'].forEach((k,i)=>G.relicIcon(g,k,i*100+10,10,80));document.body.appendChild(c);c.style.cssText='position:fixed;left:0;top:0;z-index:99999';return 1}""")
        await pg.screenshot(path=B+'relic_icons.png',clip={'x':0,'y':0,'width':300,'height':100})
        print('errs',errs[:5])
        await b.close()
asyncio.run(main())
