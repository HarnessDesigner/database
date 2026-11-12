# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Put the sizes TE's DRAWINGS give for the solder sleeves into ``TE/splices.json``, add the sleeves the catalog was missing, and give
the ones that can be used on a shielded cable the type ``Shielding Solder Sleeve``.

TE's catalog data for a sleeve is often wrong or missing (``Product Length`` is empty for about half of them, the recovered/expanded
diameters of a family are sometimes a stand-in), so the figures below were read by the user from the customer drawing of each
sleeve (2026-11-11) and are taken as correct. Each drawing covers a series; a sleeve is matched to the drawing figure by part number,
except where the drawing's own name for it is not a catalog part number (see ``DRAWING_FIGURES``, the comments name the part).

Rules:

* ``min_dia`` is the RECOVERED inside diameter and ``max_dia`` the EXPANDED one (the convention of ``te_tables.splice``).
* A catalog value that is within ``TOLERANCE`` of the drawing's figure is left as it is (the drawing gives 1 or 2 decimals, the catalog
  has TE's own conversion from inches, e.g. 8.89 against 8.9); anything else is replaced by the drawing's figure.
* ``None`` in a figure means "the drawing does not give it (or the figure is not usable)": the catalog value is kept.
* B-023-0X cannot be used (the ends differ in diameter); B-058's catalog numbers are the correct ones (user, 2026-11-11).
* The type ``Shielding Solder Sleeve`` goes to the sleeves of ``SHIELDING`` (the ones whose drawing shows a plain, round sleeve that
  can be used on a shielded cable). A sleeve that comes with a pigtail keeps "Pre-Installed Lead" in its description, which is what
  ``Splice.has_pigtail`` reads for it. The pigtail of all of them is 150 mm long, measured from the middle of the sleeve.
* Sleeves the catalog does not hold are built from TE's raw record with ``te_tables.splice`` (needs ``--raw``, the folder
  ``collect.py`` wrote) so they are made exactly like the rest.

    python scripts/sleeve_sizes_from_drawings.py --raw D:/harness_designer_tmp/te_raw [--dry]
"""

import argparse
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'scrapers'))
sys.path.insert(0, os.path.join(REPO, 'scrapers', 'te'))

TARGET = os.path.join(REPO, 'TE', 'splices.json')
TYPE = 'Shielding Solder Sleeve'
TOLERANCE = 0.051

# catalog part number -> (length mm, recovered dia mm, expanded dia mm) as the drawing gives them
DRAWING_FIGURES = {
    # B-053-70/-02/-03/-04: the drawing's expanded figure of -02, -03 and -04 (23.5, 25.3, 19.5) is not a diameter (it is the
    # length of -03 and -04, and -02's is 0.3 off its own length), so the catalog's stay
    'B-053-70': (29.7, 8.9, 13.3),
    'B-053-70-02': (23.8, 3.6, None),
    'B-053-70-03': (25.3, 3.2, None),
    'B-053-70-04': (19.5, 2.4, None),
    'B-053-70-01': (32.1, 4.4, 10.0),
    'B-053-70-05': (26.2, 4.5, 8.6),
    'B-023-00-55-22-9': (31.0, 3.0, 4.3),
    'B-023-07-55-22-9': (29.0, 2.4, 3.1),
    # B-003-0X (pigtail)
    'B-003-00': (16.5, 1.6, 3.1),
    'B-003-01': (16.5, 2.1, 4.9),
    'B-003-02': (21.5, 3.2, 7.4),
    # B-058-0X (pigtail): the catalog's own numbers are the correct ones (user, 2026-11-11), so they are written back
    'B-058-00': (16.51, 1.52, 2.59),
    'B-058-01': (16.51, 2.03, 4.39),
    'B-058-02': (22.1, 3.18, 6.9),
    'D-106-6009': (50.0, 4.4, 9.0),
    'D-106-6012': (50.0, 6.4, 12.0),
    'D-106-6015': (50.0, 9.6, 15.0),
    'D-106-6018': (50.0, 12.1, 18.0),
    'D-106-6021': (50.0, 14.7, 21.0),
    'D-106-6025': (50.0, 17.2, 25.0),
    'D-106-6030': (50.0, 19.8, 30.0),
    'B-051-00-01': (27.0, 10.0, 17.0),
    'B-051-01-01': (27.5, 12.7, 23.0),
    'B-051-02-01': (33.2, 19.1, 33.0),
    'B-051-65': (31.5, 5.8, 11.6),
    'B-004-00': (8.5, 1.1, 2.3),
    'B-022-05': (24.5, 4.3, 9.8),
    'B-022-06': (30.5, 3.8, 10.0),
    'B-900-22': (20.8, 3.6, 7.4),
    # SO63-A-55-GA-CL (pigtail), the drawing's size 4
    'SO63-4-55-20-0': (19.1, 3.3, 6.45),
    # the drawing names D-101-08, D-104-00 and CWT-9005; the catalog knows them by TE's other numbers
    '2-1194898-2': (17.25, 2.5, 4.55),      # D-101-08
    '7-1194897-0': (29.75, 5.7, 11.43),     # D-104-00
    '2-1190624-2': (42.0, 3.2, 7.0),        # CWT-9005 (the only SolderSleeve of drawing CWT-900X; sizes follow CWT-9004's)
    # B-050-00/01/02 (drawing names D-050-00, -01 and -02, in the order of their sizes and lengths)
    '8-1195424-2': (55.0, 9.0, 16.0),       # D-050-00
    '8-1195424-4': (80.0, 12.0, 21.5),      # D-050-01
    '9-1195355-4': (80.0, 19.0, 32.0),      # D-050-02
    # CWT-900X: catalog rows that TE types as crimp splices, same drawing as 2-1190624-2
    '054955-000': (26.0, 0.4, 1.7),         # CWT-9001
    'CWT-9002': (42.0, 1.3, 2.7),
    'CWT-9003': (42.0, 1.8, 4.5),
    'CWT-9004': (42.0, 2.8, 6.0),
}

# parts the catalog does not have as splices (TE files most of them as terminals): built from the raw record
NEW_PARTS = ('D-106-6030', '8-1195424-4', '9-1195355-4')

# B-023-0X cannot be used (user, 2026-11-11: the ends have different diameters): the rows an earlier run added are removed, and B-023-00 /
# B-023-07 go back to their own type. (Their pigtail twins, drawing B-023-XX-55-22-9, are a different drawing and stay.)
REMOVE = ('B-023-01', 'B-023-02', 'B-023-03', 'B-023-04')
NOT_SHIELDING = {'B-023-00': 'Solder Sleeve', 'B-023-07': 'Solder Sleeve'}

# the sleeves that are plain round sleeves, usable on a shielded cable (the rest of the 72 have ends of different diameters, an odd shape
# or are made for a terminal: their type stays ``Solder Sleeve`` / ``Solder Sleeve w/Pigtail``)
SHIELDING = set(DRAWING_FIGURES) | {'1-1194267-2'}


def close(a: float, b: float) -> bool:
    return abs(a - b) <= TOLERANCE


def build_new_rows(raw: str) -> dict:
    import common
    import te_product
    import te_tables

    catalog = common.Catalog()
    rows = {}

    for path in glob.glob(os.path.join(raw, '*', 'page_*.json')):
        with open(path, encoding='utf-8') as f:
            for rec in json.load(f)['products']:
                product = te_product.Product(rec)

                if product.part_number in NEW_PARTS and product.part_number not in rows:
                    rows[product.part_number] = te_tables.splice(product, catalog)

                    # te_tables.splice only gives a sleeve its own sizes when TE calls it a SolderSleeve (these records have no
                    # splice type): recovered = min, expanded = max
                    recovered = product.number('Recovered Inside Diameter (Max)', to='mm') or 0.0
                    expanded = product.number('Expanded Inside Diameter (Min)', to='mm') or 0.0
                    rows[product.part_number]['_sizes'] = (min(recovered, expanded), max(recovered, expanded))

    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', required=True)
    parser.add_argument('--dry', action='store_true')
    args = parser.parse_args()

    with open(TARGET, encoding='utf8', newline='') as f:
        rows = json.loads(f.read())

    removed = [r['part_number'] for r in rows if r['part_number'] in REMOVE]
    rows[:] = [r for r in rows if r['part_number'] not in REMOVE]

    if removed:
        print(f'REMOVED {removed}')

    have = {r['part_number']: r for r in rows}

    for part_number, type_name in NOT_SHIELDING.items():
        if have[part_number]['type'] != type_name:
            print(f'TYPE    {part_number:20s} {have[part_number]["type"]} -> {type_name}')
            have[part_number]['type'] = type_name

    new_rows = build_new_rows(args.raw)
    missing = [p for p in NEW_PARTS if p not in new_rows]

    if missing:
        raise SystemExit(f'not in the raw download: {missing}')

    for part_number, row in new_rows.items():
        low, high = row.pop('_sizes')

        if part_number in have:
            row = have[part_number]
        else:
            rows.append(row)
            print(f'ADDED   {part_number}')

        if not row['min_dia'] and not row['max_dia']:
            row['min_dia'], row['max_dia'] = low, high
            print(f'SIZES   {part_number}: {low} to {high} (TE)')

        if part_number in have:
            continue

        have[part_number] = row

    for part_number, (length, low, high) in DRAWING_FIGURES.items():
        row = have.get(part_number)

        if row is None:
            print(f'MISSING {part_number}: not in the catalog')
            continue

        for field, value in (('length', length), ('min_dia', low), ('max_dia', high)):
            if value is None:
                continue

            if not close(row[field], value):
                print(f'CHANGED {part_number:20s} {field:8s} {row[field]!s:>6} -> {value}')
                row[field] = value

    for part_number in SHIELDING:
        row = have.get(part_number)

        if row is not None:
            if row['type'] != TYPE:
                print(f'TYPE    {part_number:20s} {row["type"]} -> {TYPE}')

            row['type'] = TYPE

    if args.dry:
        return

    text = json.dumps(rows, indent=4, ensure_ascii=True).replace('\n', '\r\n') + '\r\n'

    with open(TARGET, 'w', encoding='utf8', newline='') as f:
        f.write(text)

    print(f'written {TARGET}')


if __name__ == '__main__':
    main()
