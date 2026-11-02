"""보스전 전용 테스트 HTML: build/hell_survive.html 에 런처를 끼워 넣는다 (세이브는 읽지도 쓰지도 않음).
사용: python3 tools/bosstest_build.py [버전]  → '<repo>/hell survive v.<버전> 보스전.html'"""
import sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ver = sys.argv[1] if len(sys.argv) > 1 else '10.22'
s = open(os.path.join(R, 'build', 'hell_survive.html'), encoding='utf-8').read()
HEAD = """<script>/* 보스전 테스트: 진행 기록 보호 — 이 파일은 실제 세이브를 읽지도 쓰지도 않는다 */
(()=>{const K='hellSurvivorSave1',g=Storage.prototype.getItem,st=Storage.prototype.setItem;
Storage.prototype.getItem=function(k){return k===K?null:g.call(this,k)};Storage.prototype.setItem=function(k,v){if(k===K)return;return st.call(this,k,v)}})();</script>"""
TAIL = r"""<script>
(()=>{
const PRI=['deadeye','gCryo','claw','speed','crit','gReload','gEmber','gSpec','gRico','heart','armor','guard','gBounty','move'];
const BOSS={byu:{n:'업경의 심판수 반업수',t:32,imgs:['arena','dmap','byu']},stl:{n:'철식 강철이',t:34,imgs:['arena','dmap','stl']}};
const css=document.createElement('style');css.textContent='#btL{position:fixed;inset:0;z-index:99999;background:#0b0710;color:#eee;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;font-family:sans-serif}#btL button{font-size:20px;padding:14px 28px;min-width:320px;border:2px solid #c33;background:#2a0c10;color:#fff;border-radius:8px;cursor:pointer}#btL button:hover{background:#5a1a22}#btL small{opacity:.7;max-width:420px;text-align:center;line-height:1.5}#btR{position:fixed;right:8px;bottom:8px;z-index:99998;font-size:12px;padding:5px 9px;opacity:.55;cursor:pointer}';document.head.appendChild(css);
const box=document.createElement('div');box.id='btL';box.innerHTML='<h2>⚔ 보스전 테스트 — 악마처형자 Lv.30</h2><small>증강은 승률 높은 조합(급소 사냥꾼·서리 도탄·공격·공속·치명·장전·불씨…)으로 자동 선택됩니다. 이 파일은 진행 기록을 건드리지 않아요.</small><button data-k="byu">🪞 업경의 심판수 반업수</button><button data-k="stl">⛓ 철식 강철이</button><small id="btM"></small>';document.body.appendChild(box);
const rb=document.createElement('button');rb.id='btR';rb.textContent='↺ 메뉴로';rb.onclick=()=>location.reload();document.body.appendChild(rb);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function auto(){const G=window.__G;let g=0;
 while(g++<5000){const s=G.state;
  if(s==='levelup'){const c=G.choices;let b=-1,bp=1e9;c.forEach((u,i)=>{if(u.locked)return;let p=PRI.indexOf(u.id);if(p<0)p=500;if(u.preview||/진화|루트/.test(document.getElementById('levelTitle').textContent))p=-1;if(p<bp){bp=p;b=i}});if(b<0)b=c.findIndex(u=>!u.locked);G.pick(b);continue}
  if(s==='evolve'){G.tick(1/30);continue}
  if(s==='play'){if(G.P.lvl>=30)break;G.P.hp=G.P.max;G.P.inv=9;G.addExp(G.P.need);G.tick(1/30);continue}
  break}
 return G.P.lvl}
async function go(k){const G=window.__G,B=BOSS[k],m=document.getElementById('btM');
 m.textContent='불러오는 중…';
 try{ G.SAVE.chars.gun=true;G.SAVE.diff.max=34;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;
  const t0=Date.now();while(!G.imgReady(B.imgs)&&Date.now()-t0<60000){await sleep(500)}
  G.startGame('gun');await sleep(300);const P=G.P;
  m.textContent='Lv.30까지 증강 선택 중…';auto();
  P.tier=B.t;P.fset='dosan';P.bossK=k;G.enemies.length=0;G.raiseCastle();G.enterArena();
  P.hp=P.max;box.remove();
 }catch(e){m.textContent='오류: '+e.message}}
box.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>go(b.dataset.k));
})();
</script>"""
assert s.count('<head>') == 1 and s.count('</body>') == 1
s = s.replace('<head>', '<head>' + HEAD, 1).replace('</body>', TAIL + '</body>', 1)
out = os.path.join(R, f'hell survive v.{ver} 보스전.html')
open(out, 'w', encoding='utf-8').write(s); print(out, len(s))
