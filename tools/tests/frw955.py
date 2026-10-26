"""v9.55 서리혈랑 (지하 25층 릴세르카 판 미니 보스): 등장 분기 · 패턴 3가지 맞음/피함(이속 150 기준) · 분노(영혼의 겨울) · 처치 · 스크린샷 · 오류
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/frw955.py [폴더]"""
import asyncio, sys, os, json
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/fw2'; os.makedirs(OUT, exist_ok=True)
JS = """(rage)=>{const G=__G,o={};G.SAVE.diff.max=25;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(15);P.tier=24;P.bossK='lil';
  for(const e of G.enemies)e.hp=0;G.spawnMini();const e=G.mini;o.bk=e&&e.bk;o.hp=Math.round(e.max);if(rage){e.rage=true;}
  const V=150/30;
  const run=(k,d0,mode)=>{e.x=P.x+d0;e.y=P.y;e.st='chase';e.tele=[];e.zf=[];e.cd=99;P.max=5000;P.hp=P.max;P.inv=0;P.shield=0;P.dodge=0;P.slowT=0;const h0=P.hp;G.frwAtk(e,k);
    let dir=null;for(let i=0;i<30*4.5;i++){
      if(mode==='away'){const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;P.x+=dx/d*V;P.y+=dy/d*V;}
      else if(mode==='in'){const dx=e.x-P.x,dy=e.y-P.y,d=Math.hypot(dx,dy)||1;if(d>40){P.x+=dx/d*V;P.y+=dy/d*V;}}
      else if(mode==='diag'){const ts=e.tele.filter(q=>q.k==='rect'&&!q.done);if(ts.length&&ts[ts.length-1]!==dir){dir=ts[ts.length-1];}if(dir){const a=dir.ang+Math.PI/4;P.x+=Math.cos(a)*V;P.y+=Math.sin(a)*V;}}
      P.inv=0;for(const q of G.enemies)if(q!==e){q.x=P.x+3000;q.y=P.y+3000;}G.ebul&&(G.ebul.length=0);G.tick(1/30);if(e.st==='chase')e.cd=99;}
    return Math.round(h0-P.hp)+'/d'+Math.round(Math.hypot(P.x-e.x,P.y-e.y))};
  o.slash=[run('fslash',150,'stand'),run('fslash',150,'away')];
  o.spike=[run('fspike',320,'stand'),run('fspike',320,'diag')];
  o.storm=[run('fstorm',230,'stand'),run('fstorm',230,'in'),run('fstorm',360,'away')];
  return o}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.frw&&__G.IMG.frwW', timeout=90000)
        print('보통', json.dumps(await pg.evaluate(JS, False), ensure_ascii=False))
        print('분노', json.dumps(await pg.evaluate(JS, True), ensure_ascii=False))
        r = await pg.evaluate("()=>{const G=__G,P=G.P,e=G.mini;e.rage=false;e.hp=e.max*0.4;e.st='chase';e.cd=5;e.tele=[];P.inv=99;G.tick(1/30);const a=e.st,b=e.invul;for(let i=0;i<45;i++)G.tick(1/30);return {st0:a,inv:b,after:e.st,rage:e.rage}}")
        print(r)
        for k in ('fslash', 'fspike', 'fstorm'):
            await pg.evaluate("(k)=>{const G=__G,P=G.P,e=G.mini;P.inv=99;e.x=P.x+(k==='fspike'?320:200);e.y=P.y-30;e.st='chase';e.tele=[];e.zf=[];G.frwAtk(e,k);for(let i=0;i<(k==='fslash'?30:k==='fspike'?33:40);i++){G.tick(1/30);if(e.st==='chase')e.cd=99;}}", k)
            await pg.screenshot(path=f'{OUT}/frw_{k}.png')
        await pg.evaluate("()=>{const G=__G,e=G.mini;e.tele=[];G.miniDefeated(e);const i=G.enemies.indexOf(e);if(i>=0)G.enemies.splice(i,1);for(let t=0;t<15;t++)G.tick(1/30);}")
        await pg.screenshot(path=f'{OUT}/frw_death.png')
        print('도감:', await pg.evaluate("()=>__G.SAVE.dex.seen.frw"), '오류:', pg.errs); await b.close()
asyncio.run(main())
