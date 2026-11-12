# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Put the sizes and the type of the TE solder sleeves into ``TE/splices.json`` without regenerating the file.

``scrapers/te/convert.py`` writes only what the current raw download holds (916 splices), while ``TE/splices.json`` also holds
rows of earlier scrapes, so the file cannot simply be replaced. After ``te_tables.splice`` learned a sleeve's own sizes (min =
recovered inside diameter, max = expanded inside diameter) and its type (``Solder Sleeve w/Pigtail`` when it has a lead fitted),
run ``convert.py --out SOME_FOLDER`` and then::

    python scripts/sleeve_sizes_from_te.py SOME_FOLDER/splices.json

Only the ``min_dia``, ``max_dia`` and ``type`` of solder sleeve rows (matched on part number and description) are changed; the file's
layout is kept exactly (4 spaces, CRLF, escaped non ASCII).
"""

import json
import os
import sys

TARGET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TE', 'splices.json')
FIELDS = ('min_dia', 'max_dia', 'type')


def main(converted: str) -> None:
    with open(TARGET, encoding='utf8', newline='') as f:
        rows = json.loads(f.read())

    with open(converted, encoding='utf8') as f:
        fresh = {(r['part_number'], r['description']): r for r in json.load(f)
                 if (r.get('type') or '').startswith('Solder Sleeve')}

    changed = 0

    for row in rows:
        new = fresh.get((row['part_number'], row['description']))

        if new is None:
            continue

        for field in FIELDS:
            if row.get(field) != new[field]:
                row[field] = new[field]
                changed += 1

    text = json.dumps(rows, indent=4, ensure_ascii=True).replace('\n', '\r\n') + '\r\n'

    with open(TARGET, 'w', encoding='utf8', newline='') as f:
        f.write(text)

    print(f'{len(fresh)} solder sleeves found in the converted file, {changed} values changed in {TARGET}')


if __name__ == '__main__':
    main(sys.argv[1])
