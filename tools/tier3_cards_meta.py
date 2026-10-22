"""cards.json: 게임 원본 템플릿에서 카드 목록(공용 강화·고유 강화·시너지·스킬)을 뽑는다. 사용: python3 tools/tier3_cards_meta.py <out.json>"""
import re, json, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'src', 'game_template.html'), encoding='utf8').read()
def seg(a, b): i = s.index(a); return s[i:s.index(b, i)]
U = seg('const UPGRADES = [', 'const UNIQUE = {'); Q = seg('const UNIQUE = {', 'const SYNERGIES = ['); Y = seg('const SYNERGIES = [', '\n];\n'); K = seg('const SKILLS = {', '\n};\n')
r = {'aug_common': [{'id': m[0], 'name': m[1], 'kind': 'stat'} for m in re.findall(r"^  \{ id: '(\w+)',\s+name: '([^']*)'", U, re.M)]}
uq = {}; cur = None
for l in Q.split('\n'):
    m = re.match(r"^  (\w+): \[", l)
    if m: cur = m.group(1); uq[cur] = []
    m = re.search(r"\{ id: '(\w+)', name: '([^']*)'", l)
    if m and cur: uq[cur].append({'id': m.group(1), 'name': m.group(2), 'kind': 'unique'})
r['aug_unique'] = uq
r['synergies'] = [{'id': m[0], 'name': m[1], 'need': re.findall(r"'(\w+)'", m[2]), 'only': (re.search(r"only: '(\w+)'", m[3]) or [None, None])[1]} for m in re.findall(r"\{ id: '(\w+)',\s+name: '([^']*)',[^\n]*?need: \[([^\]]*)\]([^\n]*)", Y)]
r['skills'] = [{'id': m[0], 'name': m[1]} for m in re.findall(r"^  (\w+): +\{ name: '([^']*)'", K, re.M)]
json.dump(r, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
print({k: (len(v) if isinstance(v, list) else {a: len(b) for a, b in v.items()}) for k, v in r.items()})
