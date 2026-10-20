# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Turn the raw Molex data downloaded by ``collect.py`` into ``Molex/<table>.json``.

Every row written has the keys of the matching ``add_<part>()`` function in ``builder/create_database`` (and in the
application's ``database/create_database``), so the builder's generic loaders pick the files up exactly like the Aptiv,
Bosch and TE ones.

Where each Molex category goes
------------------------------
=========================================================  ==============================================
Molex                                                      JSON file
=========================================================  ==============================================
Connector Housings, PCB Headers and Receptacles            housings.json
Crimp Terminals, Ring and Spade Terminals,                 terminals.json
Quick Disconnects
Splices                                                    splices.json
Connector Accessories (see ``ACCESSORY_TABLES``)           tpa_locks / cpa_locks / covers / boots / seals /
                                                           housings / accessories
Heat Shrink Tubing                                         bundles.json  (the bundle_covers table)
Flat-Flexible Cable, Industrial Cable, Coaxial Cable ...   wires.json  (``wire_type`` says which)
=========================================================  ==============================================

Molex has no transitions (breakouts) or wire markers in these part lists.

Run ``collect.py`` first (``--details`` as well, for the compatibility lists), then::

    python convert.py
"""

import collections
import json
import math
import os
import re
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RAW_DIR = os.path.join(HERE, 'raw')
DETAIL_DIR = os.path.join(RAW_DIR, 'details')
UNIVERSAL = os.path.join(REPO, 'Universal')
OUT_DIR = os.path.join(REPO, 'Molex')

MFG = 'Molex'

# raw category -> (table when the component type does not decide, extra per-category settings)
CATEGORY_TABLES = {
    'connector_housings': 'housings',
    'pcb_headers': 'housings',
    'crimp_terminals': 'terminals',
    'ring_spade_terminals': 'terminals',
    'quick_disconnects': 'terminals',
    'splices': 'splices',
    'connector_accessories': 'accessories',
    'wire_and_cable': 'wires',
}

# Connector Accessories are sorted by their ``general.componentType``; anything not listed is a plain accessory.
ACCESSORY_TABLES = {
    'Terminal Position Assurance (TPA)': 'tpa_locks',
    'Independent Secondary Lock (ISL)': 'tpa_locks',
    'Connector Position Assurance (CPA)': 'cpa_locks',
    'Cover': 'covers',
    'Dust Cover': 'covers',
    'Backshell': 'covers',
    'Boot': 'boots',
    'Wire Seal': 'seals',
    'Seal': 'seals',
    'Gasket': 'seals',
    'Cavity Plug': 'seals',
    'Wire Plug': 'seals',
    'Housing': 'housings',
}

# the seal_types.json names
SEAL_TYPES = {
    'Wire Seal': 'Single Wire Seal',
    'Seal': 'Single Cavity Plug Seal',
    'Gasket': 'Gasket',
    'Cavity Plug': 'Cavity Plug',
    'Wire Plug': 'Cavity Plug',
}

# the splice_types.json names
SPLICE_TYPES = {
    'Butt Splice': 'Butt',
    'Parallel Splice': 'Parallel',
    'Closed-end Connector': 'Closed End',
    'Wire Tap': 'Tap',
}

# wire_types.json names, decided by the wire-and-cable category and ``physical.wireCableType``
WIRE_TYPES = {
    'Flat-Flexible Cable (FFC)': 'Ribbon',
    'Coaxial Cable': 'Coaxial',
    'Specialty Wire and Cable': 'Coaxial',
    'Industrial Cable': 'Wire',
}

# Molex colour names that are not in colors.json -> the name that is
COLORS = {
    'Natural (White)': 'Natural White',
    'Natural (Translucent)': 'Natural',
    'Natural (Beige)': 'Beige',
    'Gray (Dark)': 'Dark Gray',
    'Gray (Light)': 'Light Gray',
    'Stone Gray': 'Gray',
    'Blue (Light)': 'Light Blue',
    'Green (Light)': 'Light Green',
    'Purple (Light)': 'Light Purple',
    'Purple (Dark)': 'Dark Purple',
    'Brown (Light)': 'Light Brown',
    'Brown (Carmel)': 'Brown',
    'Yellow (Dark)': 'Yellow',
    'Yellow-Green': 'Yellow Green',
    'Red (Rust)': 'Rust',
    'Ivory': 'Cream White',
}

# physical.gender -> genders (Molex calls the female-terminal housing a "receptacle" and the male one a "plug")
GENDERS = {
    'Male': 'Male',
    'Female': 'Female',
    'Plug': 'Male',
    'Receptacle': 'Female',
}

# physical.orientation (PCB headers) -> directions
DIRECTIONS = {
    'Right Angle': '90°',
    'Vertical': 'Straight',
    'Straight': 'Straight',
}

# physical.materialPlatingMating -> the platings.json description (anything else is passed through as it is)
PLATINGS = {
    'Matte Tin': 'Tin',
    'Tin-Bismuth': 'Tin',
    'Tin-Lead': 'Tin',
    'Zinc Chromate': 'Zinc',
    'Gold over Palladium Nickel': 'Gold',
    'Gold over Nickel Phosphorus': 'Gold',
    'Unplated': None,
    'N/A': None,
}

# which compatibility column a related part goes in, by the table of the part that lists it
COMPAT_COLUMNS = {
    'housings': {'terminals': 'compat_terminals', 'seals': 'compat_seals', 'tpa_locks': 'compat_tpas',
                 'cpa_locks': 'compat_cpas', 'covers': 'compat_covers', 'boots': 'compat_boots',
                 'housings': 'compat_housings'},
    'terminals': {'housings': 'compat_housings', 'seals': 'compat_seals'},
    'seals': {'housings': 'compat_housings', 'terminals': 'compat_terminals'},
    'covers': {'housings': 'compat_housings'},
    'boots': {'housings': 'compat_housings'},
    'tpa_locks': {'housings': 'compat_housings'},
    'cpa_locks': {'housings': 'compat_housings'},
}

OUTPUT_FILES = {
    'housings': 'housings.json',
    'terminals': 'terminals.json',
    'seals': 'seals.json',
    'covers': 'covers.json',
    'boots': 'boots.json',
    'tpa_locks': 'tpa_locks.json',
    'cpa_locks': 'cpa_locks.json',
    'splices': 'splices.json',
    'bundles': 'bundles.json',
    'wires': 'wires.json',
    'accessories': 'accessories.json',
}

NUMBER = re.compile(r'[-+]?\d*\.?\d+')
UNSIGNED = re.compile(r'\d*\.?\d+')
TEMPERATURE = re.compile(r'^\s*([-+]?\d+)\s*°?\s*C?\s*to\s*([-+]?\d+)\s*°?\s*C')

CATALOG: dict = {}

warnings = collections.Counter()


def warn(message: str) -> None:
    warnings[message] += 1


# ---------------------------------------------------------------------------------------------------------------------
# small readers for the raw fields
# ---------------------------------------------------------------------------------------------------------------------

def first(value: list | str | float | None) -> str | float | None:
    """The first item of a list field (Molex wraps most values in a list), or the value itself."""
    if isinstance(value, list):
        if value:
            return value[0]

        return None

    return value


def number(value: list | str | float | None) -> float | None:
    """The first number in a field such as ``"3.00mm"`` or ``["0.635"]``."""
    value = first(value)

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    match = NUMBER.search(value)
    if match is None:
        return None

    return float(match.group())


def integer(value: list | str | float | None) -> int | None:
    result = number(value)

    if result is None:
        return None

    return int(result)


def text(value: list | str | None) -> str | None:
    """A cleaned text field, ``None`` when it is blank or "N/A"."""
    value = first(value)

    if not isinstance(value, str):
        return None

    value = value.strip()
    if value in ('', 'N/A', 'None'):
        return None

    return value


def part_number(doc: dict) -> str:
    return doc['materialMaster.productNumberDisplay']


def component_type(doc: dict) -> str | None:
    return text(doc.get('general.componentType'))


def description(doc: dict) -> str:
    result = (doc.get('general.webDescription') or '').strip().rstrip(',').strip()

    if result:
        return result

    return f'{MFG} {doc.get("general.productName", "")} {part_number(doc)}'.strip()


def family(doc: dict) -> str | None:
    return text(doc.get('general.productName'))


def series(doc: dict) -> str | None:
    return text(doc.get('materialMaster.productSeries.seriesId'))


def image(doc: dict) -> str | None:
    for key in ('digitalAssets.hiresImage', 'digitalAssets.isoImage', 'digitalAssets.topRightImageURL',
                'digitalAssets.topFrontImageURL', 'digitalAssets.topLeftImageURL'):
        url = text(doc.get(key))
        if url:
            return url

    return None


def pick_url(urls: list | str | None) -> str | None:
    """A link out of a list of them, preferring the English edition of a document."""
    if isinstance(urls, str):
        urls = [urls]

    if not urls:
        return None

    for url in urls:
        if '/en-us/' in url:
            return url

    return urls[0]


def datasheet(doc: dict) -> str | None:
    """The English product specification, else the datasheet Molex generates for every part."""
    url = pick_url(doc.get('engineeringDocs.productSpecificationPdf'))
    if url and '/en-us/' in url:
        return url

    return f'https://www.molex.com/en-us/products/part-detail/{part_number(doc)}?display=pdf'


def cad(doc: dict) -> str | None:
    """The sales drawing (the 2D drawing of the part)."""
    return pick_url(doc.get('engineeringDocs.salesDrawingPdf'))


def model3d(doc: dict) -> str | None:
    """The 3D model. Molex publishes it as a zip file holding the STEP file."""
    return pick_url(doc.get('engineeringDocs._3DCadModels'))


def weight(doc: dict) -> float:
    """``physical.netWeight`` (``"1.048/g"``, ``"20.6/mg"``, ``"0.5/kg"``) in grams."""
    value = text(doc.get('physical.netWeight'))
    if not value or '/' not in value:
        return 0.0

    amount, unit = value.rsplit('/', 1)

    try:
        amount = float(amount)
    except ValueError:
        return 0.0

    if unit == 'mg':
        amount /= 1000.0
    elif unit == 'kg':
        amount *= 1000.0

    return round(amount, 6)


def temperatures(doc: dict) -> tuple[str | None, str | None]:
    """``physical.temperatureRangeOperating`` (``"-40° to +105°C"``) as the names the temperatures table uses."""
    value = text(doc.get('physical.temperatureRangeOperating'))
    if not value:
        return None, None

    match = TEMPERATURE.match(value)
    if match is None:
        return None, None

    low, high = int(match.group(1)), int(match.group(2))

    if low > 0:
        low = f'+{low}°C'
    else:
        low = f'{low}°C'

    if high > 0:
        high = f'+{high}°C'
    else:
        high = f'{high}°C'

    return low, high


def color(doc: dict, key: str = 'physical.colorResin') -> str | None:
    name = text(doc.get(key))
    if not name:
        return None

    name = COLORS.get(name, name)

    if name not in CATALOG['colors']:
        warn(f'colour not in colors.json: {name!r}')
        return None

    return name


def gender(doc: dict) -> str | None:
    name = text(doc.get('physical.gender'))
    if not name:
        return None

    return GENDERS.get(name)


def plating(doc: dict, key: str = 'physical.materialPlatingMating') -> str | None:
    name = text(doc.get(key))
    if not name:
        return None

    name = PLATINGS.get(name, name)

    # a name that is not in platings.json would make the builder add a plating row of its own
    if name is not None and name not in CATALOG['platings']:
        warn(f'plating not in platings.json: {name!r}')
        return None

    return name


def circuits(doc: dict) -> int:
    """The number of circuits a part has: how many are loaded, else the most it can have."""
    for key in ('physical.circuitsLoaded_int', 'physical.circuitsMaximum_int'):
        value = integer(doc.get(key))
        if value:
            return value

    return 0


def millimeters(value: list | str | None) -> float | None:
    """A length such as ``"4.32mm max."`` or ``".195\\" (4.95mm)"`` in millimeters (``None`` for other units)."""
    value = first(value)
    if not isinstance(value, str):
        return None

    match = re.search(r'([-+]?\d*\.?\d+)\s*mm', value)
    if match is None:
        return None

    return float(match.group(1))


# ---------------------------------------------------------------------------------------------------------------------
# wire sizes
# ---------------------------------------------------------------------------------------------------------------------

def awg_dia(awg: int) -> float:
    """Conductor diameter in mm of a solid wire of this AWG size."""
    return round(0.127 * 92 ** ((36 - awg) / 39), 4)


def awg_cross(awg: int) -> float:
    """Conductor cross section in mm² of this AWG size."""
    return round(math.pi / 4 * awg_dia(awg) ** 2, 4)


def cross_dia(cross: float) -> float:
    return round(2 * math.sqrt(cross / math.pi), 4)


def wire_sizes(doc: dict) -> dict:
    """The ``wire_size_*`` columns from ``physical.wireSizeAwg`` and ``physical.wireSizeMm`` (mm²).

    ``_min`` is the thinnest wire the part takes, ``_max`` the thickest -- so, as in the Bosch data, the minimum AWG
    number is the larger one.
    """
    sizes = dict(wire_size_awg_min=None, wire_size_awg_max=None, wire_size_dia_min=None, wire_size_dia_max=None,
                 wire_size_cross_min=None, wire_size_cross_max=None)

    awgs = []
    for value in doc.get('physical.wireSizeAwg_int') or []:
        if float(value).is_integer():
            awgs.append(int(value))

    if awgs:
        thin, thick = max(awgs), min(awgs)

        sizes.update(wire_size_awg_min=thin, wire_size_awg_max=thick,
                     wire_size_dia_min=awg_dia(thin), wire_size_dia_max=awg_dia(thick),
                     wire_size_cross_min=awg_cross(thin), wire_size_cross_max=awg_cross(thick))

    metric = text(doc.get('physical.wireSizeMm'))
    if metric:
        # a range is written "1.00-2.50": the hyphen is a separator, not a minus sign
        values = [float(v) for v in UNSIGNED.findall(metric) if float(v) > 0]

        if len(values) == 1:
            values = values * 2

        if len(values) == 2:
            low, high = sorted(values)

            sizes.update(wire_size_cross_min=low, wire_size_cross_max=high)

            if not awgs:
                sizes.update(wire_size_dia_min=cross_dia(low), wire_size_dia_max=cross_dia(high))

    return sizes


# ---------------------------------------------------------------------------------------------------------------------
# one function per table
# ---------------------------------------------------------------------------------------------------------------------

def housing(doc: dict) -> dict:
    sealed = text(doc.get('physical.sealed'))

    direction = None
    orientation = text(doc.get('physical.orientation'))
    if orientation:
        direction = DIRECTIONS.get(orientation)

    # 'Receptacle' / 'Plug' are in physical.gender for the housings and in general.componentType for some others
    gender_name = gender(doc)
    if gender_name is None:
        gender_name = GENDERS.get(component_type(doc) or '')

    low, high = temperatures(doc)

    terminal_sizes = []
    for size in doc.get('physical.terminalSize') or []:
        try:
            terminal_sizes.append(float(size))
        except ValueError:
            pass

    pins = circuits(doc)

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), gender=gender_name, direction=direction,
        image=image(doc), datasheet=datasheet(doc), cad=cad(doc), model3d=model3d(doc),
        min_temp=low, max_temp=high,
        cavity_lock=None, ip_rating=text(doc.get('general.ipRating')), seal_type=None, cpa_lock_type=None,
        sealing=int(sealed == 'Sealed'), rows=integer(doc.get('physical.numberOfRows_int')) or 0, num_pins=pins,
        terminal_sizes=terminal_sizes, terminal_size_counts=[],
        centerline=number(doc.get('physical.pitchMatingInterface_int')) or 0.0,
        compat_cpas=[], compat_tpas=[], compat_covers=[], compat_terminals=[], compat_seals=[], compat_housings=[],
        compat_boots=[],
        length=0.0, width=0.0, height=0.0, weight=weight(doc),
    )


def terminal(doc: dict, slug: str) -> dict:
    low, high = temperatures(doc)

    blade_size = number(doc.get('physical.terminalSize')) or 0.0
    if slug == 'quick_disconnects':
        blade_size = millimeters(doc.get('physical.tabWidth')) or 0.0

    length = 0.0
    match = re.search(r'Length\s+([\d.]+)\s*mm', description(doc))
    if match:
        length = float(match.group(1))

    amps = number(doc.get('electrical.currentMaximumPerContact_int'))
    max_current_ma = 0
    if amps:
        max_current_ma = int(round(amps * 1000))

    row = dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), image=image(doc), datasheet=datasheet(doc), cad=cad(doc), model3d=model3d(doc),
        min_temp=low, max_temp=high, plating=plating(doc), gender=gender(doc), cavity_lock=None, sealing=0,
        blade_size=blade_size, resistance=0.0, mating_cycles=integer(doc.get('physical.durabilityMatingCyclesMax_int')) or 0,
        max_vibration_g=0, max_current_ma=max_current_ma,
    )
    row.update(wire_sizes(doc))
    row.update(length=length, width=0.0, height=0.0, weight=weight(doc), compat_housings=[], compat_seals=[])

    return row


def seal(doc: dict) -> dict:
    low, high = temperatures(doc)
    kind = component_type(doc)

    sizes = dict(wire_size_dia_min=None, wire_size_dia_max=None, wire_size_cross_min=None, wire_size_cross_max=None,
                 wire_size_awg_min=None, wire_size_awg_max=None)

    # "... for 1.40-1.70 Insulation Diameter ..." is the range of wire the seal closes around
    match = re.search(r'([\d.]+)\s*-\s*([\d.]+)\s*(?:mm\s*)?Insulation Diameter', description(doc))
    if match:
        sizes.update(wire_size_dia_min=float(match.group(1)), wire_size_dia_max=float(match.group(2)))

    row = dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high,
        model3d=model3d(doc), type=SEAL_TYPES.get(kind), hardness=-1, lubricant='',
        length=0.0, width=0.0, height=0.0, weight=weight(doc), o_dia=0.0, i_dia=0.0,
    )
    row.update(sizes)
    row.update(compat_housings=[], compat_terminals=[])

    return row


def cover(doc: dict) -> dict:
    low, high = temperatures(doc)

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), direction=None, image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low,
        max_temp=high, model3d=model3d(doc), length=0.0, width=0.0, height=0.0, weight=weight(doc), pins=circuits(doc),
        compat_housings=[],
    )


def boot(doc: dict) -> dict:
    low, high = temperatures(doc)

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), material=text(doc.get('physical.materialResin')), direction=None, image=image(doc),
        datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high, model3d=model3d(doc),
        length=0.0, width=0.0, height=0.0, weight=weight(doc), compat_housings=[], min_dia=0.0, max_dia=0.0,
        protection=None,
    )


def tpa_lock(doc: dict) -> dict:
    low, high = temperatures(doc)

    lock_type = ''
    if component_type(doc) == 'Independent Secondary Lock (ISL)':
        lock_type = 'Secondary'

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high,
        model3d=model3d(doc), lock_type=lock_type, length=0.0, width=0.0, height=0.0, weight=weight(doc),
        pins=circuits(doc), terminal_size=number(doc.get('physical.terminalSize')) or 0.0, compat_housings=[],
    )


def cpa_lock(doc: dict) -> dict:
    low, high = temperatures(doc)

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high,
        model3d=model3d(doc), type=None, length=0.0, width=0.0, height=0.0, weight=weight(doc), pins=circuits(doc),
        terminal_size=number(doc.get('physical.terminalSize')) or 0.0, compat_housings=[],
    )


def splice(doc: dict) -> dict:
    low, high = temperatures(doc)

    kinds = doc.get('general.type') or []
    kind = None
    if kinds:
        kind = SPLICE_TYPES.get(kinds[0])

    num_wires = None
    if kind == 'Butt':
        num_wires = 2

    insulation = text(doc.get('physical.insulation'))
    if not insulation:
        insulation = text(doc.get('physical.materialResin'))

    insulation_dia = millimeters(doc.get('physical.wireInsulationDiameter')) or 0.0

    length = 0.0
    match = re.search(r'Length\s+([\d.]+)\s*mm', description(doc))
    if match:
        length = float(match.group(1))

    row = dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high,
        model3d=model3d(doc), material=insulation, plating=plating(doc), type=kind, min_dia=0.0,
        max_dia=insulation_dia, resistance=0.0, length=length, weight=weight(doc),
    )
    row.update(wire_sizes(doc))
    row.update(num_wires=num_wires)

    return row


def bundle(doc: dict) -> dict:
    """Heat shrink tubing; the tubing is described by its inside diameter as supplied, the part's largest size."""
    low, high = temperatures(doc)

    wall = ''
    name = description(doc)
    if 'Thin-Wall' in name or 'Thin Wall' in name:
        wall = 'Thin Wall'
    elif 'Thick-Wall' in name or 'Thick Wall' in name:
        wall = 'Thick Wall'

    return dict(
        part_number=part_number(doc), description=name, mfg=MFG, family=family(doc), series=series(doc),
        color=color(doc), material=text(doc.get('physical.materialResin')), image=image(doc), datasheet=datasheet(doc),
        cad=cad(doc), shrink_temp=None, min_temp=low, max_temp=high, protection=None, rigidity='', shrink_ratio='',
        wall=wall, min_dia=0.0, max_dia=millimeters(doc.get('physical.internalDiameter')) or 0.0,
        adhesive_ids=[], weight=weight(doc),
    )


def conductor_plating(doc: dict) -> str | None:
    """The platings.json description of ``physical.signalConductor`` ("Solid Copper", "Tinned Copper" ...)."""
    value = text(doc.get('physical.signalConductor'))
    if not value:
        return None

    value = value.lower()
    if 'copper' not in value:
        return None

    if 'silver' in value:
        return 'Silver-plated Copper'

    if 'tin' in value:
        return 'Tin-plated Copper'

    return 'Copper'


def wire(doc: dict, slug: str) -> dict:
    low, high = temperatures(doc)

    category = doc['taxonomyPathValueLast']
    wire_type = WIRE_TYPES.get(category)

    awg = integer(doc.get('physical.wireSizeAwg_int'))
    if awg is None:
        awg = integer(doc.get('physical.signalConductorAWG'))

    wire_size_dia = None
    wire_size_cross = None
    if awg is not None:
        wire_size_dia = awg_dia(awg)
        wire_size_cross = awg_cross(awg)

    shields = [text(doc.get('physical.firstShield')), text(doc.get('physical.secondShield'))]
    shielded = int(any(shields) or 'shield' in description(doc).lower())

    jacket = color(doc, 'physical.colorCableJacket')
    if jacket is None:
        jacket = color(doc)

    conductors = circuits(doc)
    if not conductors:
        conductors = 1

    return dict(
        part_number=part_number(doc), description=description(doc), mfg=MFG, family=family(doc), series=series(doc),
        color=jacket, image=image(doc), datasheet=datasheet(doc), cad=cad(doc), min_temp=low, max_temp=high,
        material=text(doc.get('physical.materialOuterJacket')), stripe_color=None, core_material=conductor_plating(doc),
        num_conductors=conductors, shielded=shielded, tpi=0.0, wire_size_dia=wire_size_dia,
        wire_size_cross=wire_size_cross, wire_size_awg=awg, od_mm=millimeters(doc.get('physical.outerDiameter')) or 0.0,
        weight_1km=0.0, resistance_1km=0.0, volts=number(doc.get('electrical.voltageMaximum_int')) or 0.0, strands=1,
        wire_type=wire_type,
    )


def accessory(doc: dict) -> dict:
    return dict(
        part_number=part_number(doc), mfg=MFG, description=description(doc), series=series(doc), family=family(doc),
        color=color(doc), material=text(doc.get('physical.materialResin')), image=image(doc), datasheet=datasheet(doc),
        cad=cad(doc), model3d=model3d(doc), length=0.0, width=0.0, height=0.0, weight=weight(doc),
    )


BUILDERS = {
    'housings': lambda doc, slug: housing(doc),
    'terminals': terminal,
    'seals': lambda doc, slug: seal(doc),
    'covers': lambda doc, slug: cover(doc),
    'boots': lambda doc, slug: boot(doc),
    'tpa_locks': lambda doc, slug: tpa_lock(doc),
    'cpa_locks': lambda doc, slug: cpa_lock(doc),
    'splices': lambda doc, slug: splice(doc),
    'wires': wire,
    'accessories': lambda doc, slug: accessory(doc),
}


# ---------------------------------------------------------------------------------------------------------------------
# reading, sorting into tables, compatibility
# ---------------------------------------------------------------------------------------------------------------------

def load_json(path: str) -> list | dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_catalog() -> dict:
    """The names already in the lookup tables the rows are checked against."""
    return {
        'colors': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'colors.json'))},
        'platings': {entry['description'] for entry in load_json(os.path.join(UNIVERSAL, 'platings.json'))},
        'genders': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'genders.json'))},
        'directions': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'directions.json'))},
        'seal_types': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'seal_types.json'))},
        'splice_types': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'splice_types.json'))},
        'wire_types': {entry['name'] for entry in load_json(os.path.join(UNIVERSAL, 'wire_types.json'))},
    }


def table_of(slug: str, doc: dict) -> str | None:
    """The table a raw row belongs to, ``None`` for the rows that are not wanted."""
    table = CATEGORY_TABLES[slug]

    if slug == 'connector_accessories':
        return ACCESSORY_TABLES.get(component_type(doc), 'accessories')

    if slug == 'wire_and_cable' and doc['taxonomyPathValueLast'] == 'Heat Shrink Tubing':
        return 'bundles'

    return table


FILTER = re.compile(r'\+([\w.]+):\("([^"]*)"\)')


def passes_filter(doc: dict, filters: str | None) -> bool:
    """Whether a part meets the ``filters`` of a series relation (``fq= +physical.circuitsMaximum:("4") ...``).

    Molex limits "mates with this series" to the parts with the same circuits and rows, so a 4 circuit housing is not
    listed as mating with every header of the series.
    """
    if not filters:
        return True

    for field, wanted in FILTER.findall(filters):
        value = doc.get(field)
        if not isinstance(value, list):
            value = [value]

        if wanted not in [str(item) for item in value]:
            return False

    return True


def compatibility(rows: dict, details: dict, docs: dict) -> None:
    """Fill the ``compat_*`` lists.

    A part is linked to the parts a ``productdetails`` answer names (``useWithProduct``, ``matesWithProduct``) and to
    every part of the series it names (``useWithSeries``, ``matesWithSeries``, the latter with its filters). A link
    found on either part is written to both.
    """
    index = {}
    by_series = collections.defaultdict(list)

    for table, entries in rows.items():
        for entry in entries.values():
            index[entry['part_number']] = (table, entry)

            if entry['series']:
                by_series[entry['series']].append(entry['part_number'])

    links = collections.defaultdict(set)

    def link(one: str, other: str) -> None:
        if other in index and other != one:
            links[one].add(other)
            links[other].add(one)

    for number_, detail in details.items():
        if number_ not in index:
            continue

        for key in ('useWithProduct', 'matesWithProduct'):
            for item in detail.get(key) or []:
                link(number_, item['productNumber'])

        for key in ('useWithSeries', 'matesWithSeries'):
            for item in detail.get(key) or []:
                for other in by_series.get(item['seriesId'], []):
                    if passes_filter(docs[other], item.get('filters')):
                        link(number_, other)

    for number_, others in links.items():
        table, entry = index[number_]
        columns = COMPAT_COLUMNS.get(table)

        if not columns:
            continue

        for other in sorted(others):
            column = columns.get(index[other][0])

            if column:
                entry[column].append(other)

    # a housing that does not state its terminal sizes takes them from the terminals it is used with
    for entry in rows.get('housings', {}).values():
        if entry['terminal_sizes']:
            continue

        sizes = set()
        for other in entry['compat_terminals']:
            blade = index[other][1]['blade_size']

            if blade:
                sizes.add(blade)

        entry['terminal_sizes'] = sorted(sizes)


def write_output(table: str, entries: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    rows = [entries[key] for key in sorted(entries)]

    # the same layout as the Aptiv / Bosch / TE files: 4 space indent, \uXXXX escapes, CRLF line ends
    with open(os.path.join(OUT_DIR, OUTPUT_FILES[table]), 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(rows, f, indent=4)
        f.write('\n')


def check_mappings() -> None:
    """Stop if a name this script maps to is not in its lookup table (the builder would add a stray row for it)."""
    checks = (
        ('genders', GENDERS.values()),
        ('directions', DIRECTIONS.values()),
        ('seal_types', SEAL_TYPES.values()),
        ('splice_types', SPLICE_TYPES.values()),
        ('wire_types', WIRE_TYPES.values()),
        ('colors', COLORS.values()),
    )

    bad = []
    for table, names in checks:
        for name in names:
            if name not in CATALOG[table]:
                bad.append(f'{table}: {name!r}')

    if bad:
        sys.exit('not in the lookup tables: ' + ', '.join(bad))


def main() -> None:
    CATALOG.update(load_catalog())
    check_mappings()

    rows = collections.defaultdict(dict)
    docs = {}
    skipped = collections.Counter()

    for slug in CATEGORY_TABLES:
        path = os.path.join(RAW_DIR, slug + '.json')
        if not os.path.exists(path):
            sys.exit(f'{path} is missing -- run collect.py first')

        for doc in load_json(path):
            table = table_of(slug, doc)

            if table == 'bundles':
                row = bundle(doc)
            else:
                row = BUILDERS[table](doc, slug)

            if row['part_number'] in rows[table]:
                skipped[f'{table}: duplicate part number'] += 1
                continue

            rows[table][row['part_number']] = row
            docs[row['part_number']] = doc

    details = {}
    if os.path.isdir(DETAIL_DIR):
        for name in os.listdir(DETAIL_DIR):
            details.update(load_json(os.path.join(DETAIL_DIR, name)))
    else:
        print('no raw/details found -- the compat_* lists stay empty (run collect.py --details)')

    compatibility(rows, details, docs)

    print(f'{"file":22} {"rows":>7}   with image / datasheet / cad / 3D model')
    for table in OUTPUT_FILES:
        entries = rows.get(table, {})

        if not entries:
            continue

        write_output(table, entries)

        values = list(entries.values())
        counts = []
        for key in ('image', 'datasheet', 'cad', 'model3d'):
            counts.append(sum(1 for value in values if value.get(key)))

        print(f'{OUTPUT_FILES[table]:22} {len(entries):7}   ' + ' / '.join(f'{count}' for count in counts))

    for message, count in sorted(skipped.items()):
        print(f'skipped {count}: {message}')

    for message, count in sorted(warnings.items()):
        print(f'warning {count}x: {message}')


if __name__ == '__main__':
    main()
