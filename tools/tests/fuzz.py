"""v6.30 오류 찾기: 모든 캐릭터·루트로 필드를 무작위 카드로 오래 돌리고(그리기 포함) 마왕전까지 들어가 콘솔 오류를 모은다.
게임 루프는 한 프레임 오류를 삼키고 계속 돌기 때문에(console.error) 눈에 안 띄는 오류를 여기서 잡는다.
사용: PYTHONPATH=tools python3 tools/tests/fuzz.py [초=240] [단계=0]"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from h301 import newpage
CASES = [('wolf', 0, 0), ('wolf', 1, 1), ('wolf', 2, 0), ('wolf', 1, 2), ('snail', 0, 0), ('snail', 1, 0), ('snail', 2, 0), ('archer', 0, 0), ('archer', 0, 1), ('archer', 1, 0),
         ('chimera', 0, 0), ('chimera', 1, 0), ('chimera', 2, 0), ('lizard', 0, 0), ('lizard', 0, 1), ('lizard', 1, 0), ('twins', 0, 0), ('ghost', 0, 0), ('octo', 0, 0), ('gun', 0, 0)]
BOSSES = ['monkey', 'eye', 'skel', 'angel']
JS = """([ch,rt,fin,secs,tier,bk])=>{const G=__G;G.SAVE.holyBlood=true;Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true,ghost:true,octo:true,gun:true});
 G.SAVE.diff.max=5;G.SAVE.shards=99999;G.SAVE.diff.sel=tier;G.SAVE.set.speed=0;G.startGame(ch);G.P.bossK=bk;window.__rt=rt;window.__fin=fin;
 const P=G.P;let s=7;const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff};
 const pick=()=>{const t=document.getElementById('levelTitle').textContent,c=G.choices;let i;if(t.indexOf('갈림길')>=0)i=rt;else if(t.indexOf('최종')>=0)i=fin;else i=Math.floor(rnd()*c.length);if(!c[i]||c[i].locked)i=c.findIndex(u=>!u.locked);G.pick(Math.max(0,i))};
 let t=0,n=0;const keys=['KeyW','KeyA','KeyS','KeyD'],E=new Set();const T=f=>{try{f()}catch(e){E.add(String(e&&e.stack||e).slice(0,260))}};
 while(t<secs&&n++<200000){const st=G.state;if(st==='levelup'){pick();continue}if(st==='evolve'||st==='slot'){T(()=>G.tick(1/30));if(st==='slot'&&G.slotUI){try{G.closeSlot()}catch(e){}}continue}
  if(st!=='play'&&st!=='dead')break;if(st==='dead')break;
  if(n%40===0){for(const k of keys)G.keys.delete(k);G.keys.add(keys[Math.floor(rnd()*4)]);if(rnd()<0.5)G.keys.add(keys[Math.floor(rnd()*4)]);}
  if(P.skill&&P.skT<=0&&rnd()<0.05)G.cast();
  P.hp=Math.max(P.hp,P.max*0.5);P.cond&&0;if(P.lvl>=3){P.lavaT=Math.max(P.lavaT,5);P.bugF0=true;P.low10=true;P.poisoned=true;}
  T(()=>G.tick(1/30));t+=1/30;if(n%15===0)T(()=>G.render());if(P.lvl<26&&n%30===0)G.addExp(P.need*0.25);}
 return {lvl:P.lvl,form:P.form,route:P.route,fin:P.fin,t:Math.round(t),state:G.state,arena:!!G.arena,boss:G.boss&&G.boss.bk,bhp:G.boss?Math.round(G.boss.hp/G.boss.max*100):null,E:[...E]}}"""
async def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 240; tier = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); bad = 0
        for i, (ch, rt, fin) in enumerate(CASES):
            pg = await newpage(b, 960, 600); errs = pg.errs
            pg.on('console', lambda m, errs=errs: errs.append(m.text[:300]) if m.type == 'error' else None)
            r = await pg.evaluate(JS, [ch, rt, fin, secs, tier, BOSSES[i % 4]])
            if r['arena'] is False and r['state'] == 'play':   # 마왕성까지 못 갔으면 직접 들어가 마왕전도 조금 돈다
                r['E'] += await pg.evaluate("()=>{const G=__G,E=new Set(),T=f=>{try{f()}catch(e){E.add(String(e&&e.stack||e).slice(0,260))}};if(!G.castle)G.raiseCastle();G.enterArena();for(let i=0;i<900;i++){G.P.hp=G.P.max;T(()=>G.tick(1/30));if(i%15===0)T(()=>G.render());if(G.state==='levelup')G.pick(0);}return [...E]}")
            u = sorted(set(errs + r['E'])); bad += len(u); r.pop('E')
            print(ch, rt, fin, r, 'ERR' if u else 'ok', u[:4]); await pg.close()
        print('total distinct errors', bad); await b.close()
asyncio.run(main())
