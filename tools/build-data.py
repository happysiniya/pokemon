"""PokeAPI CSV 데이터로 pokemon-data.js(한국어 포켓몬 목록)를 다시 만들어요.

사용법 (도감 폴더에서):
    python -I tools/build-data.py

- PokeAPI GitHub 저장소의 CSV 파일을 임시 폴더에 받아서 사용해요 (인터넷 필요).
- 한국어 language_id = 3.
- 도감 설명은 한국어가 있는 가장 최신 게임 버전의 것을 써요.
"""
import csv, json, os, sys, tempfile, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

BASE = 'https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/'
FILES = ['pokemon_species_names', 'pokemon_species', 'pokemon_types', 'type_names', 'pokemon_species_flavor_text']
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
types = {}
for r in rows('pokemon_types'):
    if int(r['pokemon_id']) <= max_id:  # 기본 모습만 (10001번 이후는 다른 폼)
        types.setdefault(r['pokemon_id'], []).append((int(r['slot']), tnames[r['type_id']]))
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
        't': [t for _, t in sorted(types.get(i, []))],  # 타입
        'from': int(r['evolves_from_species_id'] or 0),  # 진화 전 번호
        'ch': int(r['evolution_chain_id']),    # 진화 계열 번호
        'leg': 2 if r['is_mythical'] == '1' else (1 if r['is_legendary'] == '1' else 0),  # 1 전설, 2 환상
        'd': desc.get(i, (0, ''))[1],          # 도감 설명
    })
data.sort(key=lambda x: x['id'])

with open(out, 'w', encoding='utf-8') as f:
    f.write('// PokeAPI 데이터(https://pokeapi.co)로 만든 한국어 포켓몬 목록\nconst POKEMON = ')
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')

gens = sorted({x['gen'] for x in data})
print(f'완료: {len(data)}마리, 세대 {gens[0]}~{gens[-1]}, 설명 없음 {sum(1 for x in data if not x["d"])}마리')
print('영어 이름으로 남은 포켓몬(한국어 이름 없음):', [x['n'] for x in data if x['n'].isascii()][:20])
