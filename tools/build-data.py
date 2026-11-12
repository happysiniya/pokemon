"""PokeAPI CSV 데이터로 pokemon-data.js(한국어 포켓몬 목록)를 다시 만들어요.

사용법 (도감 폴더에서):
    python -I tools/build-data.py

- PokeAPI GitHub 저장소의 CSV 파일을 임시 폴더에 받아서 사용해요 (인터넷 필요).
- 한국어 language_id = 3.
- 도감 설명은 한국어가 있는 가장 최신 게임 버전의 것을 써요.
- 메가진화(is_mega=1)는 MEGA 배열로 따로 만들어요. 한국어 이름이 아직 없으면
  "메가" + 원래 이름 (+ X/Y/Z, 모습 이름)으로 만들어요.
"""
import csv, json, os, sys, tempfile, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

BASE = 'https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/'
KO = '3'

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, 'pokemon-data.js')
tmp = tempfile.mkdtemp(prefix='pokeapi-csv-')

def rows(name):
    path = os.path.join(tmp, name + '.csv')
    if not os.path.exists(path):
        print('받는 중:', name)
        urllib.request.urlretrieve(BASE + name + '.csv', path)
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

species = rows('pokemon_species')
max_id = max(int(r['id']) for r in species)
names = {r['pokemon_species_id']: r for r in rows('pokemon_species_names') if r['local_language_id'] == KO}
tnames = {r['type_id']: r['name'].strip() for r in rows('type_names') if r['local_language_id'] == KO}
types = {}  # pokemon_id -> 타입 (기본 모습과 메가진화 모두)
for r in rows('pokemon_types'):
    types.setdefault(r['pokemon_id'], []).append((int(r['slot']), tnames[r['type_id']]))
def type_list(pid):
    return [t for _, t in sorted(types.get(pid, []))]
desc = {}
for r in rows('pokemon_species_flavor_text'):
    if r['language_id'] == KO:
        v, s = int(r['version_id']), r['species_id']
        if s not in desc or v > desc[s][0]:
            desc[s] = (v, ' '.join(r['flavor_text'].split()))

data = []
for r in species:
    i = r['id']
    n = names.get(i, {})
    data.append({
        'id': int(i),
        'n': n.get('name', r['identifier']),   # 이름
        'g': n.get('genus', ''),               # 분류 (예: 쥐포켓몬)
        'gen': int(r['generation_id']),        # 세대
        't': type_list(i),                     # 타입
        'from': int(r['evolves_from_species_id'] or 0),  # 진화 전 번호
        'ch': int(r['evolution_chain_id']),    # 진화 계열 번호
        'leg': 2 if r['is_mythical'] == '1' else (1 if r['is_legendary'] == '1' else 0),  # 1 전설, 2 환상
        'd': desc.get(i, (0, ''))[1],          # 도감 설명
    })
data.sort(key=lambda x: x['id'])
ko_name = {x['id']: x['n'] for x in data}

# ---------- 메가진화 ----------
pokemon = {r['id']: r for r in rows('pokemon')}
form_ko = {r['pokemon_form_id']: r for r in rows('pokemon_form_names') if r['local_language_id'] == KO}
# 한국어 모습 이름이 없는 메가진화용 (식별자 조각 -> 한국어)
FORM_WORD = {
    'male': '수컷', 'female': '암컷', 'original': '500년 전의 색',
    'curly': '젖힌 모습', 'droopy': '늘어진 모습', 'stretchy': '뻗은 모습',
}
megas = []
for f in rows('pokemon_forms'):
    if f['is_mega'] != '1':
        continue
    pid = f['pokemon_id']
    sp = pokemon[pid]['species_id']
    ko = form_ko.get(f['id'], {})
    name = (ko.get('pokemon_name') or ko.get('form_name') or '').strip()
    if not name.startswith('메가'):
        # 예: raichu-mega-x -> 메가라이츄X, meowstic-female-mega -> 메가냐오닉스(암컷)
        parts = pokemon[pid]['identifier'].split('-')
        letter = parts[-1].upper() if parts[-2:-1] == ['mega'] and len(parts[-1]) == 1 else ''
        words = [FORM_WORD[w] for w in parts if w in FORM_WORD]
        name = '메가' + ko_name[int(sp)] + letter + (f'({words[0]})' if words else '')
    megas.append({
        'id': int(pid),          # 그림·울음소리 번호 (10000번대)
        'b': int(sp),            # 원래 포켓몬 번호
        'n': name,               # 이름
        't': type_list(pid),     # 메가진화 후 타입
    })
megas.sort(key=lambda x: (x['b'], x['id']))

with open(out, 'w', encoding='utf-8') as f:
    f.write('// PokeAPI 데이터(https://pokeapi.co)로 만든 한국어 포켓몬 목록\nconst POKEMON = ')
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n// 메가진화 (b = 원래 포켓몬 번호)\nconst MEGA = ')
    json.dump(megas, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')

gens = sorted({x['gen'] for x in data})
print(f'완료: {len(data)}마리, 세대 {gens[0]}~{gens[-1]}, 설명 없음 {sum(1 for x in data if not x["d"])}마리')
print(f'메가진화: {len(megas)}개')
print('영어 이름으로 남은 포켓몬(한국어 이름 없음):', [x['n'] for x in data if x['n'].isascii()][:20])
