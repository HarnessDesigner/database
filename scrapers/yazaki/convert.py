# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Turn the raw Yazaki catalog downloaded by ``collect.py`` into ``Yazaki/<table>.json``.

Where each Yazaki part class goes
---------------------------------
=====================================  =================================================
Yazaki class                           JSON file
=====================================  =================================================
Housing                                housings.json
Terminal, Eyelet / Earth terminal      terminals.json
Wire seal                              seals.json  (type "Single Wire Seal", or "Gasket")
Dummy plug                             seals.json  (type "Cavity Plug")
Installation possible part: cover/cap  covers.json
Installation possible part: the rest   accessories.json  (rear / front holders ...)
=====================================  =================================================

The ``compat_*`` lists come from the detail page's "Mating Part Numbers", "Terminal", "Wire seal", "Dummy plug" and
"Installation possible part" rows; a link found on one part is written to both.

Run ``collect.py`` first, then::

    python convert.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402


HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, 'raw')
OUT_DIR = os.path.join(common.REPO, 'Yazaki')

MFG = 'Yazaki'

# the detail page rows that name other parts
LINK_LABELS = ('Mating Part Numbers', 'Terminal', 'Wire seal', 'Dummy plug', 'Installation possible part')

COLORS = {}

PLATINGS = {
    'Tin Plating': 'Tin',
    'Gold Plating': 'Gold',
    'Silver Plating': 'Silver',
    'Without plating': None,
}

NUMBERS = re.compile(r'\d+\.?\d*')
SIGNED = re.compile(r'[-+]?\d+')
COVER_WORDS = re.compile(r'\b(CAP|COVER)\b', re.I)

catalog = common.Catalog()


def field(detail: dict, label: str) -> str:
    return detail['fields'].get(label, {}).get('text', '').strip()


def floats(value: str) -> list[float]:
    return [float(v) for v in NUMBERS.findall(value)]


def dimension(detail: dict, label: str) -> float:
    values = floats(field(detail, label))

    if values:
        return values[0]

    return 0.0


def temperatures(detail: dict) -> tuple[str | None, str | None]:
    """``"-40 to 100deg.C"`` / ``"-40℃〜150℃"`` / ``"-40°C to 140°C"`` -> ``("-40°C", "+100°C")``."""
    values = SIGNED.findall(field(detail, 'Temperature Range'))

    if len(values) < 2:
        return None, None

    return common.temperature(int(values[0])), common.temperature(abs(int(values[1])))


def common_fields(part_id: str, row: dict, detail: dict) -> dict:
    """The fields every Yazaki part has."""
    files = detail['files']

    image = files.get('product')
    if image and 'nowprinting' in image:
        image = None

    low, high = temperatures(detail)
    color = field(detail, 'Color') or row['color_name'].strip()

    return dict(
        part_number=part_id, description=row['part_name'].strip(), mfg=MFG, family=field(detail, 'Family') or None,
        color=catalog.color(color, COLORS), image=image, cad=files.get('draw'), min_temp=low, max_temp=high,
    )


def gender(detail: dict) -> str | None:
    return catalog.choose('genders', field(detail, 'Male/Female'))


def housing(part_id: str, row: dict, detail: dict) -> dict:
    return common.new_row(
        'housings', **common_fields(part_id, row, detail), gender=gender(detail),
        sealing=int(field(detail, 'Unsealed/Seald') == 'Sealed'),
        num_pins=int(dimension(detail, 'Number of Poles')),
        terminal_sizes=floats(field(detail, 'Tab size (mm)')),
        length=dimension(detail, 'Length'), width=dimension(detail, 'Width'), height=dimension(detail, 'Height'),
    )


def terminal(part_id: str, row: dict, detail: dict) -> dict:
    amps = floats(field(detail, 'Allowable Current(Ref.)'))
    max_current_ma = 0
    if amps:
        max_current_ma = int(round(amps[0] * 1000))

    sizes = common.cross_sizes(dimension(detail, 'Size (Min)') or None, dimension(detail, 'Size (Max)') or None)

    tab = floats(field(detail, 'Tab size (mm)'))
    blade_size = 0.0
    if tab:
        blade_size = tab[0]

    return common.new_row(
        'terminals', **common_fields(part_id, row, detail), plating=catalog.plating(field(detail, 'Plating'), PLATINGS),
        gender=gender(detail), sealing=int(field(detail, 'Unsealed/Seald') == 'Sealed'), blade_size=blade_size,
        max_current_ma=max_current_ma, **sizes,
        length=dimension(detail, 'Length'), width=dimension(detail, 'Width'), height=dimension(detail, 'Height'),
    )


def seal(part_id: str, row: dict, detail: dict, kind: str) -> dict:
    return common.new_row(
        'seals', **common_fields(part_id, row, detail), type=kind,
        length=dimension(detail, 'Length'), width=dimension(detail, 'Width'), height=dimension(detail, 'Height'),
    )


def cover(part_id: str, row: dict, detail: dict) -> dict:
    return common.new_row(
        'covers', **common_fields(part_id, row, detail), pins=int(dimension(detail, 'Number of Poles')),
        length=dimension(detail, 'Length'), width=dimension(detail, 'Width'), height=dimension(detail, 'Height'),
    )


def accessory(part_id: str, row: dict, detail: dict) -> dict:
    fields = common_fields(part_id, row, detail)

    # add_accessory has no temperature columns
    del fields['min_temp']
    del fields['max_temp']

    return common.new_row(
        'accessories', **fields, material=field(detail, 'Materials') or None,
        length=dimension(detail, 'Length'), width=dimension(detail, 'Width'), height=dimension(detail, 'Height'),
    )


def main() -> None:
    lists = common.load_json(os.path.join(RAW_DIR, 'lists.json'))
    details = common.load_json(os.path.join(RAW_DIR, 'details.json'))

    rows = {table: {} for table in common.OUTPUT_FILES}
    links = []
    missing = 0

    for name, entries in lists.items():
        for row in entries:
            part_id = row['part_id']
            detail = details.get(part_id)

            if detail is None:
                missing += 1
                continue

            if name == 'housing':
                table, new = 'housings', housing(part_id, row, detail)
            elif name in ('terminal', 'eyelet'):
                table, new = 'terminals', terminal(part_id, row, detail)
            elif name == 'wire_seal':
                kind = 'Single Wire Seal'
                if 'GASKET' in row['part_name'].upper():
                    kind = 'Gasket'

                table, new = 'seals', seal(part_id, row, detail, catalog.choose('seal_types', kind))
            elif name == 'dummy_plug':
                table, new = 'seals', seal(part_id, row, detail, catalog.choose('seal_types', 'Cavity Plug'))
            elif name == 'cover' or (name == 'other' and COVER_WORDS.search(row['part_name'])):
                table, new = 'covers', cover(part_id, row, detail)
            else:
                table, new = 'accessories', accessory(part_id, row, detail)

            if part_id in rows[table]:
                continue

            rows[table][part_id] = new

            for label in LINK_LABELS:
                for other in detail['fields'].get(label, {}).get('links', []):
                    links.append((part_id, other))

    common.fill_compat(rows, links)
    common.write_rows(OUT_DIR, rows)
    common.report(catalog)

    if missing:
        print(f'{missing} parts have no detail page downloaded -- run collect.py again')


if __name__ == '__main__':
    main()
