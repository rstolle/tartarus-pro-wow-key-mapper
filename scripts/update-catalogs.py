"""Refresh embedded Retail and progression Classic ability/talent snapshots.

Run manually with Python 3; the shipped app makes no network requests.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
import base64
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'tartarus-wow.html'
CLASSES = {'Warrior': 1, 'Paladin': 2, 'Hunter': 3, 'Rogue': 4,
           'Priest': 5, 'Death Knight': 6, 'Shaman': 7, 'Mage': 8,
           'Warlock': 9, 'Monk': 10, 'Druid': 11, 'Demon Hunter': 12, 'Evoker': 13}


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as response:
        return response.read()


def catalog(task):
    flavor, prefix, cls, class_id = task
    slug = cls.lower().replace(' ', '-')
    rows, details, patch = [], {}, None
    for category in ('abilities', 'talents'):
        url = f'https://www.wowhead.com/{prefix}spells/{category}/{slug}'
        text = fetch(url).decode()
        version = re.search(r'latest patch \(([\d.]+)\)', text)
        if version:
            patch = version[1]
        match = re.search(r'var listviewspells\s*=\s*(\[.*?\]);', text, re.S)
        if not match:
            raise ValueError(f'No spell list: {url}')
        rows.extend(json.loads(re.sub(r'([,{])\s*(\w+):', r'\1"\2":', match[1])))
        for match in re.finditer(r'WH.Gatherer.addData\(6,\s*\d+,\s*', text):
            data, _ = json.JSONDecoder().raw_decode(text[match.end():])
            details.update(data)
    if flavor == 'classic':
        text = fetch(f'https://www.wowhead.com/{prefix}class={class_id}/{slug}').decode()
        match = re.search(r'new Listview\(\{template: .spell.*?data:\s*(\[.*?\])\s*\}', text, re.S)
        if not match:
            raise ValueError(f'No specialization list for {cls}')
        rows.extend(row for row in json.loads(match[1]) if row['cat'] == -12)
        for match in re.finditer(r'WH.Gatherer.addData\(6,\s*\d+,\s*', text):
            data, _ = json.JSONDecoder().raw_decode(text[match.end():])
            details.update(data)
    found = {}
    for row in rows:
        info = details.get(str(row['id']), {})
        if not info or 'passive' in info.get('rank_enus', '').lower():
            continue
        name = info['name_enus']
        found.setdefault(name, {'id': f'{flavor}-{class_id}-{row["id"]}',
            'name': name, 'class': cls, 'school': 'Ability / talent',
            'icon': '/wowhead/' + info['icon'] + '.jpg', 'flavor': flavor,
            'sourceId': row['id']})
        level = row.get('level')
        if isinstance(level, int) and level > 0:
            previous = found[name].get('level')
            found[name]['level'] = min(previous, level) if previous else level
        else:
            found[name].setdefault('level', None)
    if len(found) < 10:
        raise ValueError(f'Suspiciously small catalog: {flavor} {cls}')
    if not patch:
        raise ValueError(f'No patch version for {flavor} {cls}')
    return {'spells': list(found.values()), 'patch': patch, 'flavor': flavor}


def main():
    text = APP.read_text(encoding='utf-8')
    match = re.search(r'(<script id="spell-data"[^>]*>)(.*?)(</script>)', text, re.S)
    data = json.loads(match[2])
    data['spells'] = [dict(spell, flavor='forever') for spell in data['spells']
                      if spell.get('flavor', 'forever') == 'forever']
    # Match Forever levels by class and exact name, preserving legacy spell IDs.
    def forever_levels(cls):
        slug = cls.lower().replace(' ', '-')
        source = json.loads(fetch(f'https://wowforever.wclbox.com/shuju/en/spellbook/{slug}.json'))
        levels = {}
        for tab in source['tabs']:
            for spell in tab['spells']:
                # Talent spell records can report level 1 as an engine default;
                # that is not a sourced talent unlock level.
                if spell.get('status') == 'talent':
                    continue
                values = [rank.get('forever', {}).get('level')
                          for rank in spell.get('ranks', []) if rank.get('forever')]
                values = [level for level in values if isinstance(level, int) and level > 0]
                level = min(values) if values else spell.get('level')
                if isinstance(level, int) and level > 0:
                    levels[spell['name']] = level
        return cls, levels

    with ThreadPoolExecutor(max_workers=4) as pool:
        levels = dict(pool.map(forever_levels, sorted({s['class'] for s in data['spells']})))
    for spell in data['spells']:
        spell['level'] = levels[spell['class']].get(spell['name'])
    tasks = [(flavor, prefix, cls, cid)
             for flavor, prefix in [('retail', ''), ('classic', 'mop-classic/')]
             for cls, cid in CLASSES.items() if flavor == 'retail' or cid <= 11]
    versions = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(catalog, tasks):
            flavor = result['flavor']
            if flavor in versions and versions[flavor] != result['patch']:
                raise ValueError(f'Inconsistent patch versions for {flavor}')
            versions[flavor] = result['patch']
            data['spells'].extend(result['spells'])
    # Reuse identical embedded icons and only download additional artwork.
    by_name = {Path(key).name: value for key, value in data['icons'].items()}
    missing = sorted({spell['icon'] for spell in data['spells']} - data['icons'].keys())

    def icon(key):
        name = Path(key).name
        try:
            return key, by_name.get(name) or 'data:image/jpeg;base64,' + base64.b64encode(
                fetch('https://wow.zamimg.com/images/wow/icons/medium/' + name)).decode()
        except HTTPError as error:
            if error.code != 404:
                raise
            print('Icon unavailable; app will show initials:', name)
            return key, ''

    with ThreadPoolExecutor(max_workers=8) as pool:
        data['icons'].update(pool.map(icon, missing))
    today = datetime.now(timezone.utc).date().isoformat()
    data['catalogs'] = {
        'retail': {'label': 'Retail · Midnight ' + versions['retail'], 'snapshot': today,
                   'source': 'https://www.wowhead.com/spells/abilities'},
        'classic': {'label': 'Classic · Mists of Pandaria ' + versions['classic'], 'snapshot': today,
                    'source': 'https://www.wowhead.com/mop-classic/spells/abilities'},
        'forever': {'label': 'Forever · WCLBox snapshot', 'snapshot': '2026-11-10',
                    'source': 'https://wowforever.wclbox.com/en'}}
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    APP.write_text(text[:match.start(2)] + payload + text[match.end(2):], encoding='utf-8')
    print({flavor: sum(s['flavor'] == flavor for s in data['spells'])
           for flavor in data['catalogs']})


if __name__ == '__main__':
    main()
