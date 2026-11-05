# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Turn the pages downloaded by ``collect.py`` into ``TE/<table>.json``.

    python convert.py --raw FOLDER [--out FOLDER] [--report FILE]

``te_classify.py`` decides which table a product belongs to (see ``README.md``), ``te_tables.py`` builds the row. This file
reads the pages, applies the rule for parts that share a marketing part number, checks the transitions against
``Universal/transitions.json`` and writes the result.

Parts that share a part number (user, 2026-11-04): the record with the lowest ``tcpn`` keeps the part number. Another record with
the same number whose data is identical is dropped; one whose data differs gets ``-<its tcpn>`` added to the part number.

Transitions (user, 2026-11-04): a part number that is already in ``Universal/transitions.json`` is skipped. A new one is written,
with its data, to ``transitions_review.json`` for inspection (the builder does not read that file).

Genders (user, 2026-11-04): a housing and the terminals that fit it have the same gender. With ``--cache FOLDER`` the converter
writes ``FOLDER/tcpn_index.json`` (every housing and terminal by TE's part number) for ``genders.py``, which searches the
related parts for the gender TE does not state and writes ``FOLDER/genders.json``; the next run applies it.
"""

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # NOQA: E402
import te_classify  # NOQA: E402
import te_tables  # NOQA: E402
from te_product import Product  # NOQA: E402


HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(common.REPO, 'TE')

BUILDERS = {
    'housings': te_tables.housing, 'terminals': te_tables.terminal, 'seals': te_tables.seal, 'covers': te_tables.cover,
    'boots': te_tables.boot, 'splices': te_tables.splice, 'bundles': te_tables.bundle, 'accessories': te_tables.accessory,
}


def write_list(path: str, data: list) -> None:
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(data, f, indent=4)
        f.write('\n')


def pages(raw_dir: str):
    """Every product of every page, category folders and pages in order."""
    for folder in sorted(os.listdir(raw_dir)):
        path = os.path.join(raw_dir, folder)

        if not os.path.isdir(path):
            continue

        for name in sorted(os.listdir(path)):
            if name.startswith('page_') and name.endswith('.json'):
                with open(os.path.join(path, name), 'r', encoding='utf-8') as f:
                    yield from json.load(f)['products']


def transition_review_entry(p: Product) -> dict:
    """What TE says about a transition that is not in Universal/transitions.json, for someone to look at."""
    min_temp, max_temp = p.temperatures()

    return dict(part_number=p.part_number, tcpn=p.tcpn, description=p.description, family=p.family, series=p.series,
                image=p.image, datasheet=p.datasheet, cad=p.cad, min_temp=min_temp, max_temp=max_temp,
                shape=p.first('Molded Part Shape'), shape_code=p.first('Molded Part Shape Code'),
                branch_count=p.number('Number of Branches'), material=p.first('Primary Product Material'),
                material_code=p.first('Material Code'), adhesive=p.first('Adhesive Requirement'),
                adhesive_code=p.first('Adhesive Code'), protection=p.first('Resistance Protection'))


GENDERS = ('Male', 'Female')

# parts that have no gender at all (a lug, a ring terminal, a shield terminator, a power cable termination): they are not searched
NO_GENDER_CATEGORIES = {
    'Compression Connectors', 'Power Cable Terminations', 'SolderSleeve Shield Terminators', 'Ring Terminals', 'Spade Terminals',
    'Magnet Wire Terminals', 'Crimp Wire Pins, Tabs & Ferrules', 'Foil Terminals', 'Special Purpose Terminals', 'Power Terminals',
}


def apply_genders(rows: dict, groups: dict, categories: dict, cache: str) -> int:
    """Write the tcpn index for ``genders.py`` and fill the gender it found into housings and terminals that have none.

    :returns: how many rows got a gender.
    """
    index = {}

    for table in ('housings', 'terminals'):
        for part_number, records in groups.get(table, {}).items():
            for tcpn, row, _entry in records:
                if categories.get(tcpn) in NO_GENDER_CATEGORIES:
                    continue

                # a record that shares its number with an earlier one and differs from it was renamed ``<number>-<tcpn>``
                final = row['part_number']

                if final in rows[table]:
                    index[tcpn] = [table, final]

    os.makedirs(cache, exist_ok=True)
    common.write_json(os.path.join(cache, 'tcpn_index.json'), index)
    path = os.path.join(cache, 'genders.json')

    if not os.path.exists(path):
        return 0

    found = common.load_json(path)
    filled = 0

    for table in ('housings', 'terminals'):
        for part_number, row in rows.get(table, {}).items():
            if row.get('gender') not in GENDERS and found.get(part_number) in GENDERS:
                row['gender'] = found[part_number]
                filled += 1

    return filled


def convert(raw_dir: str, out_dir: str, report_path: str | None, cache: str | None = None) -> None:
    catalog = common.Catalog()
    known_transitions = {row['part_number'] for row in common.load_json(os.path.join(common.UNIVERSAL, 'transitions.json'))}

    groups = collections.defaultdict(lambda: collections.defaultdict(list))   # table -> part number -> [(tcpn, row, entry)]
    dropped = collections.Counter()
    drop_examples = collections.defaultdict(list)
    wire_notes = collections.Counter()
    wire_note_examples = collections.defaultdict(list)
    transitions = []
    transitions_known = 0
    seen_tcpn = set()
    categories = {}
    total = 0

    for raw in pages(raw_dir):
        product = Product(raw)
        total += 1

        if product.tcpn in seen_tcpn:
            dropped['seen twice in the download'] += 1
            continue

        seen_tcpn.add(product.tcpn)
        table, reason = te_classify.classify(product)

        if table is None:
            dropped[reason] += 1

            if len(drop_examples[reason]) < 3:
                drop_examples[reason].append(f'{product.part_number} ({product.category})')

            continue

        if table == 'transitions':
            if product.part_number in known_transitions:
                transitions_known += 1
            else:
                transitions.append(transition_review_entry(product))

            continue

        entry = None

        if table == 'wires':
            row, entry, notes = te_tables.wire(product, catalog)

            for note in notes:
                wire_notes[note.split(';')[0][:60]] += 1

                if len(wire_note_examples[note.split(';')[0][:60]]) < 3:
                    wire_note_examples[note.split(';')[0][:60]].append(product.part_number)
        elif table in ('tpa_locks', 'cpa_locks'):
            row = te_tables.lock(table, product, catalog)
        else:
            row = BUILDERS[table](product, catalog)

        if reason:
            dropped[f'kept, but: {reason}'] += 1

        groups[table][row['part_number']].append((product.tcpn, row, entry))
        categories[product.tcpn] = product.category

    # parts that share a part number. The links (image, datasheet, drawing, 3D model) are different for every record, they hold
    # TE's own number, so they are not part of the data that is compared.
    rows = {}
    wire_entries = []
    identical = renamed = description_only = 0
    links = ('part_number', 'image', 'datasheet', 'cad', 'model3d')

    for table, by_number in groups.items():
        rows[table] = {}

        for part_number, records in by_number.items():
            records.sort(key=lambda r: r[0])
            first = records[0]
            rows[table][part_number] = first[1]

            if first[2]:
                wire_entries.append(first[2])

            for tcpn, row, entry in records[1:]:
                other = {k: v for k, v in row.items() if k not in links}
                same = {k: v for k, v in first[1].items() if k not in links}

                if other == same:
                    identical += 1
                    continue

                renamed += 1

                if {k: v for k, v in other.items() if k != 'description'} == {k: v for k, v in same.items() if k != 'description'}:
                    description_only += 1

                new_number = f'{part_number}-{tcpn}'
                row['part_number'] = new_number
                rows[table][new_number] = row

                if entry:
                    entry['wire'] = new_number
                    wire_entries.append(entry)

    gender_fills = apply_genders(rows, groups, categories, cache) if cache else 0

    os.makedirs(out_dir, exist_ok=True)
    common.write_rows(out_dir, rows)

    if wire_entries:
        write_list(os.path.join(out_dir, 'wire_conductors.json'), sorted(wire_entries, key=lambda e: e['wire']))

    if transitions:
        write_list(os.path.join(out_dir, 'transitions_review.json'), sorted(transitions, key=lambda e: e['part_number']))

    lines = [f'products read: {total}', '']
    lines.append(f'{"table":14} {"rows":>7}')

    for table in sorted(rows):
        lines.append(f'{table:14} {len(rows[table]):7}')

    lines += ['', f'wire_conductors entries (cables with per-conductor colours): {len(wire_entries)}',
              f'transitions already in Universal: {transitions_known}; new, written to transitions_review.json: {len(transitions)}',
              f'genders filled in from the related parts (genders.py): {gender_fills}',
              f'shared part numbers: {identical} identical records dropped, {renamed} different records kept with -tcpn '
              f'({description_only} of those differ only in the description)', '',
              'left out / noted:']

    for reason, count in dropped.most_common():
        lines.append(f'  {count:6}  {reason}   e.g. {", ".join(drop_examples.get(reason, []))}')

    if wire_notes:
        lines += ['', 'wire notes:']

        for note, count in wire_notes.most_common(12):
            lines.append(f'  {count:6}  {note}   e.g. {", ".join(wire_note_examples[note])}')

    text = '\n'.join(lines)
    print('\n' + text)

    if report_path:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(text + '\n')

    common.report(catalog)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--raw', required=True, help='the folder collect.py wrote')
    parser.add_argument('--out', default=OUT_DIR, help='where the JSON files go (default: the repo\'s TE folder)')
    parser.add_argument('--report', help='also write the summary to this file')
    parser.add_argument('--cache', help='folder for tcpn_index.json (written) and genders.json (read), see genders.py')
    args = parser.parse_args()
    convert(args.raw, args.out, args.report, args.cache)


if __name__ == '__main__':
    main()
