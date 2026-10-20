# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Turn the raw KET catalog downloaded by ``collect.py`` into ``KET/<table>.json``.

Where each KET part goes
------------------------
===========================================================  =============================================
KET                                                          JSON file
===========================================================  =============================================
Connectors (wire-to-wire, PCB, joint, lamp / bulb sockets,   housings.json
high voltage, FAKRA housings, LVDS, airbag, home appliance)
Terminals (automotive, earth / ring, fuse, electronic),      terminals.json
FAKRA contacts
Splice                                                       splices.json
Connector Cover                                              covers.json
FAKRA seal                                                   seals.json
Holder, Clip & Etc, Lever, FAKRA sleeve                      accessories.json
===========================================================  =============================================

The ``compat_*`` lists come from the record's ``SPMTERMINAL`` (terminals), ``SPMWIRESEAL`` (wire seals), ``SPMCOVER``,
``SPMCONNECTOR`` (the mating connector), ``SPMCLIP`` and ``SPMRH`` (rear holder) part numbers; a link found on one part is
written to both. Links to parts that are not in the catalog are dropped.

Run ``collect.py`` first, then::

    python convert.py
"""

import glob
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402


HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, 'raw')
OUT_DIR = os.path.join(common.REPO, 'KET')

MFG = 'KET'

# the record fields that hold the part numbers of related parts
LINK_FIELDS = ('SPMTERMINAL', 'SPMWIRESEAL', 'SPMCOVER', 'SPMCONNECTOR', 'SPMCLIP', 'SPMRH')

# "Mating Tab Width(in)" -> the nominal blade width in mm (the sizes the terminal families are named after)
TAB_MM = {
    '.020': 0.5, '.025': 0.64, '.030': 0.8, '.040': 1.0, '.050': 1.3, '.060': 1.5, '.070': 1.8, '.090': 2.3,
    '.110': 2.8, '.118': 3.0, '.187': 4.8, '.250': 6.3, '.312': 7.8, '.375': 9.5,
}

COLORS = {'기타': None}

PLATINGS = {
    'Pre-Tin': 'Tin',
    'Non-Plating': None,
    'Au/Ni': 'Gold',
    'Ag/Ni': 'Silver',
    'Ni': 'Nickel',
}

# CATEGORYCODENM of the sub-parts that are not covers
ACCESSORY_NAMES = ('Holder', 'Clip&Etc', 'Lever')

SIGNED = re.compile(r'[-+]?\d+')
FLOAT = re.compile(r'\d+\.?\d*')
AWG = re.compile(r'awg\s*(\d+)\s*[-~]\s*(\d+)', re.I)

catalog = common.Catalog()


def hinted(url: str, part_number: str, extension: str) -> str:
    """Add the file type to one of KET's extension-less download links.

    ``/cm/fileDownMan.ket?attcFilSn=157043`` is served as ``application/octet-stream`` and the application, which does
    not know that content type, then looks for a known file extension in the address. The server ignores the extra
    ``file`` parameter, so it only gives the link the extension.
    """
    return f'{url}&file={urllib.parse.quote(part_number)}.{extension}'


def text(item: dict, key: str) -> str:
    value = item.get(key)

    if value is None:
        return ''

    return str(value).strip()


def numeric(item: dict, key: str) -> float | None:
    """The field as a number if it is nothing but a number (``"6.2"``), else ``None`` (``"c025 wp: 3.4*4.8"``)."""
    value = text(item, key)

    if re.fullmatch(r'\d+\.?\d*', value):
        return float(value)

    return None


def dimensions(item: dict) -> tuple[float, float, float]:
    """``SPPRODSIZE``: ``"44.7*25.8*49.4"``, ``"43.0l*14.0w*5.5h"``, ``"φ37.0*36.20"``, ``"0.4t*70.0*14"``."""
    value = text(item, 'SPPRODSIZE')
    values = [float(v) for v in FLOAT.findall(value)]

    if 'φ' in value and values:
        if len(values) > 1:
            return values[0], values[0], values[1]

        return values[0], values[0], 0.0

    if re.match(r'^[\d.]+t\*', value) and len(values) >= 3:
        # a plate: thickness first
        return values[1], values[2], values[0]

    if len(values) >= 3:
        return values[0], values[1], values[2]

    return 0.0, 0.0, 0.0


def tab_sizes(item: dict) -> list[float]:
    """``SPTABSIZE`` (``".250"``, ``".025 / .060 / .110"``, inches) as the nominal widths in mm."""
    sizes = []

    for part in text(item, 'SPTABSIZE').split('/'):
        part = part.strip()

        if not part or part == '-':
            continue

        if re.fullmatch(r'\d+', part):
            part = '.' + part

        if re.fullmatch(r'0\.\d+', part):
            part = part[1:]

        if part in TAB_MM:
            sizes.append(TAB_MM[part])
        elif re.fullmatch(r'\.\d+', part):
            sizes.append(round(float(part) * 25.4, 2))

    return sizes


def temperatures(item: dict) -> tuple[str | None, str | None]:
    """``"-40℃ ~ 105℃"``, ``"-40~105"``, ``"-40˚c~+105˚c"`` -> ``("-40°C", "+105°C")``."""
    for key in ('SPOPTIMUMTEMP', 'SPOPERTEMP'):
        values = SIGNED.findall(text(item, key))

        if len(values) >= 2:
            return common.temperature(int(values[0])), common.temperature(abs(int(values[1])))

    return None, None


def weight(item: dict) -> float:
    for key in ('SPNETWEIGHT', 'SPTOTALWEIGHT'):
        value = numeric(item, key)

        if value:
            return value

    return 0.0


def wire_sizes(item: dict) -> dict:
    """The AWG range of ``SPWIRERANGEAWG`` (``"ul1015 awg 18-12"``) with the conductor sizes it stands for."""
    sizes = dict(wire_size_awg_min=None, wire_size_awg_max=None, wire_size_dia_min=None, wire_size_dia_max=None,
                 wire_size_cross_min=None, wire_size_cross_max=None)

    match = AWG.search(text(item, 'SPWIRERANGEAWG'))
    if match is None:
        return sizes

    thin, thick = sorted([int(match.group(1)), int(match.group(2))], reverse=True)

    sizes.update(wire_size_awg_min=thin, wire_size_awg_max=thick, wire_size_dia_min=common.awg_dia(thin),
                 wire_size_dia_max=common.awg_dia(thick), wire_size_cross_min=common.awg_cross(thin),
                 wire_size_cross_max=common.awg_cross(thick))

    return sizes


def common_fields(item: dict, files: dict) -> dict:
    part_number = item['PARTNUMBER']

    image = None
    if item.get('ATTCFILSN'):
        image = hinted(f'https://www.ket.com/cm/fileDownMan.ket?attcFilSn={item["ATTCFILSN"]}', part_number, 'jpg')

    series = text(item, 'SPSERIES')
    low, high = temperatures(item)

    return dict(
        part_number=part_number, description=text(item, 'PARTNAME') or part_number, mfg=MFG, family=series or None,
        color=catalog.color(text(item, 'SPCOLOR'), COLORS), image=image, cad=files.get('pdf2d'),
        min_temp=low, max_temp=high,
    )


def is_sealed(item: dict) -> int:
    return int(text(item, 'SPWATERPROOF').lower() in ('yes', 'waterproof'))


def gender(item: dict) -> str | None:
    name = text(item, 'SPPARTSTYLE')

    if not name:
        # FAKRA: a jack takes the plug's centre pin, so it is the female side
        name = {'Jack': 'Female', 'Plug': 'Male'}.get(text(item, 'SPINTERFACE'), '')

    return catalog.choose('genders', name)


def housing(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)

    cavity_lock = None
    if text(item, 'SPLANCETYPE') == 'HSG Lance':
        cavity_lock = catalog.choose('cavity_locks', 'Locking Lance')

    pins = numeric(item, 'SPNOOFPOLE')

    return common.new_row(
        'housings', **common_fields(item, files), model3d=files.get('step'), gender=gender(item),
        cavity_lock=cavity_lock, sealing=is_sealed(item), num_pins=int(pins or 0), terminal_sizes=tab_sizes(item),
        centerline=numeric(item, 'SPPITCH') or 0.0, length=length, width=width, height=height, weight=weight(item),
    )


def terminal(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)

    tabs = tab_sizes(item)
    blade_size = 0.0
    if tabs:
        blade_size = tabs[0]

    amps = numeric(item, 'SPPERMITVOLT')
    max_current_ma = 0
    if amps:
        max_current_ma = int(round(amps * 1000))

    return common.new_row(
        'terminals', **common_fields(item, files), model3d=files.get('step'),
        plating=catalog.plating(text(item, 'SPPLATING'), PLATINGS), gender=gender(item), sealing=is_sealed(item),
        blade_size=blade_size, max_current_ma=max_current_ma, **wire_sizes(item),
        length=length, width=width, height=height, weight=weight(item),
    )


def splice(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)

    return common.new_row(
        'splices', **common_fields(item, files), model3d=files.get('step'), material=text(item, 'SPMATERTYPE') or None,
        plating=catalog.plating(text(item, 'SPPLATING'), PLATINGS), **wire_sizes(item), length=length,
        weight=weight(item),
    )


def cover(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)
    pins = numeric(item, 'SPNOOFPOLE')

    return common.new_row(
        'covers', **common_fields(item, files), model3d=files.get('step'), pins=int(pins or 0), length=length,
        width=width, height=height, weight=weight(item),
    )


def seal(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)

    return common.new_row(
        'seals', **common_fields(item, files), model3d=files.get('step'),
        type=catalog.choose('seal_types', 'Single Wire Seal'), length=length, width=width, height=height,
        weight=weight(item),
    )


def accessory(item: dict, files: dict) -> dict:
    length, width, height = dimensions(item)

    fields = common_fields(item, files)

    # add_accessory has no temperature columns
    del fields['min_temp']
    del fields['max_temp']

    return common.new_row(
        'accessories', **fields, model3d=files.get('step'), material=text(item, 'SPMATERTYPE') or None,
        length=length, width=width, height=height, weight=weight(item),
    )


def table_of(item: dict) -> str:
    """The table a KET record belongs to."""
    code = item['_code']
    name = text(item, 'CATEGORYCODENM')

    if code == 'CA04':
        if name == 'Splice':
            return 'splices'

        return 'terminals'

    if code == 'CG05':
        return 'terminals'

    if name == 'Connector Cover':
        return 'covers'

    if name in ACCESSORY_NAMES:
        return 'accessories'

    if code == 'CD01':
        kind = text(item, 'SPSUBSUPPLIY')

        if kind in ("Outer Contact Ass'y", 'Terminal'):
            return 'terminals'

        if kind == 'Seal':
            return 'seals'

        if kind == 'Sleeve':
            return 'accessories'

    return 'housings'


BUILDERS = {
    'housings': housing, 'terminals': terminal, 'splices': splice, 'covers': cover, 'seals': seal,
    'accessories': accessory,
}


def main() -> None:
    items = []
    for path in sorted(glob.glob(os.path.join(RAW_DIR, 'lists', '*.json'))):
        code = os.path.basename(path)[:-5]

        for item in common.load_json(path):
            item['_code'] = code
            items.append(item)

    files_path = os.path.join(RAW_DIR, 'files.json')
    files = {}
    if os.path.exists(files_path):
        files = common.load_json(files_path)
    else:
        print('no raw/files.json -- no 2D / 3D links (run collect.py without --lists)')

    for part_number, links in files.items():
        for key, extension in (('step', 'stp'), ('igs', 'igs')):
            if key in links:
                links[key] = hinted(links[key], part_number, extension)

    rows = {table: {} for table in common.OUTPUT_FILES}
    for item in items:
        table = table_of(item)
        part_number = item['PARTNUMBER']

        if part_number in rows[table]:
            continue

        rows[table][part_number] = BUILDERS[table](item, files.get(part_number, {}))

    # the part numbers of the related parts are written in any case; match them without regard to case
    folded = {}
    for entries in rows.values():
        for part_number in entries:
            folded[part_number.lower()] = part_number

    links = []
    for item in items:
        for key in LINK_FIELDS:
            for other in re.split(r'[,\s]+', text(item, key)):
                other = folded.get(other.lower())

                if other:
                    links.append((item['PARTNUMBER'], other))

    common.fill_compat(rows, links)
    common.write_rows(OUT_DIR, rows)
    common.report(catalog)


if __name__ == '__main__':
    main()
