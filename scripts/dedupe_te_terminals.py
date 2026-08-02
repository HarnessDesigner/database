"""One-off cleanup: remove duplicate rows from TE/terminals.json.

part_number is the only field on the terminals table with a UNIQUE
constraint besides the primary key, so it's the only thing that matters for
"duplicate" here. Keeps the first occurrence of each part_number, drops the
rest. Backs up the original file (terminals.json.bak) before overwriting.
"""

import json
import os
import shutil

TE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TE')
TARGET = os.path.join(TE_DIR, 'terminals.json')
BACKUP = os.path.join(TE_DIR, 'terminals.json.bak')


def main():
    shutil.copy2(TARGET, BACKUP)
    print(f'backed up {TARGET} -> {BACKUP}')

    with open(TARGET, 'r', encoding='utf-8') as f:
        data = json.load(f)

    seen = set()
    deduped = []
    removed = 0

    for row in data:
        part_number = row.get('part_number')
        if part_number in seen:
            removed += 1
            continue
        seen.add(part_number)
        deduped.append(row)

    print(f'{len(data)} rows -> {len(deduped)} rows ({removed} duplicates removed)')

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(json.dumps(deduped, indent=4))

    print(f'wrote {TARGET}')


if __name__ == '__main__':
    main()
