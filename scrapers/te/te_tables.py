# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""One row builder per output table. Every feature is optional: a part that does not have one keeps the column's default."""

import math
import os
import re

import common
from te_product import Product


MFG = 'TE Connectivity'

# TE owns Raychem, AMP, Deutsch, Simel ... but they were companies of their own, so each brand is its own manufacturer (user,
# 2026-11-04) and the manufacturers table's description says it is a TE Connectivity company. This maps TE's spelling of a brand
# to the manufacturer's name; any other brand is used as TE writes it.
BRAND_NAMES = {'te connectivity': MFG, 'te': MFG, 'deutsch': 'Deutsch'}


def manufacturer(brand: str | None) -> str:
    if not brand or not brand.strip():
        return MFG

    brand = brand.strip()
    return BRAND_NAMES.get(brand.lower(), brand)

# TE's colour names that are not in colors.json (the patch list of scripts/correct_json.py, plus the names found since)
COLORS = {
    'Blue - Transluscent': 'Blue', 'Red - Green': 'Red', 'Blue - Green': 'Blue Green', 'Yellow - Green': 'Yellow Green',
    'Brown - Green': 'Brown', 'Violet - Green': 'Violet', 'Black - Orange': 'Black', 'Clear': 'Light Gray',
    'Yellow - Translucent': 'Yellow', 'Rust Red': 'Rust', 'Red-Orange': 'Red Orange', 'Green & Yellow': 'Green Yellow',
    'Black Matte': 'Black Shadows', 'Beige White': 'Beige', 'Emerald Green': 'Emerald', 'Ivory': 'Vanilla',
    'Cream Yellow': 'Arylide Yellow', 'Metalized Silver': 'Silver', 'Gray & Dark Gray': 'Gray', 'None': None,
    'Violet': 'Violet', 'Purple': 'Violet', 'Natural': None, 'Bright': None,
}

MIL_COLORS = ('Black', 'Brown', 'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Violet', 'Gray', 'White')

_ip_ratings = {entry['name'] for entry in common.load_json(os.path.join(common.UNIVERSAL, 'ip_ratings.json'))}
_cpa_types = {entry['name'] for entry in common.load_json(os.path.join(common.UNIVERSAL, 'cpa_lock_types.json'))}
_protections = {entry['name'] for entry in common.load_json(os.path.join(common.UNIVERSAL, 'protections.json'))}


# ---------------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------------

def identity(p: Product, catalog: common.Catalog, color_labels: tuple[str, ...] = ('Primary Product Color',)) -> dict:
    """The columns every table has."""
    family = p.family
    brand = p.brand

    if family is None and brand and 'TE' not in brand:
        family = brand

    min_temp, max_temp = p.temperatures()
    name = p.first(*color_labels)

    return dict(part_number=p.part_number, description=p.description, mfg=manufacturer(brand), family=family, series=p.series,
                color=catalog.color(name, COLORS) if name else None, image=p.image, datasheet=p.datasheet, cad=p.cad,
                min_temp=min_temp, max_temp=max_temp)


def size(p: Product) -> dict:
    """length, width, height in mm and weight in g."""
    width = p.number('Connector Width', 'Product Width', to='mm') or 0.0
    height = p.number('Connector Height', 'Product Height', to='mm') or 0.0
    diameter = p.number('Product Diameter', to='mm')

    if diameter:
        width = height = diameter

    return dict(length=p.number('Connector Length', 'Assembly Length', 'Product Length', to='mm') or 0.0, width=width,
                height=height, weight=p.number('Product Weight', 'Terminal & Contact Weight', to='g') or 0.0)


def awg_of_cross(cross: float) -> int:
    d_in = 2 * math.sqrt(cross / math.pi) / 25.4
    return int(round(36 - 39 * math.log(d_in / 0.005, 92)))


def awg_values(p: Product) -> list[int]:
    """The plain AWG sizes (a ``2/0`` is skipped: it is not a number of the series this column holds)."""
    return [int(float(v)) for v in p.values('Wire Size', 'AWG') if re.fullmatch(r'\d+(\.0+)?', v.strip())]


def wire_size_range(p: Product) -> dict:
    """The ``wire_size_*_min`` / ``_max`` columns of a terminal, splice or seal (the range of wire it takes)."""
    cross = p.numbers('Wire Size', 'mm²')
    awg = awg_values(p)
    sizes = dict(wire_size_awg_min=None, wire_size_awg_max=None, wire_size_dia_min=None, wire_size_dia_max=None,
                 wire_size_cross_min=None, wire_size_cross_max=None)

    if not cross and not awg:
        # power cable parts give the conductor range as a cross section ("95 - 240", mm2); AWG is only filled where the
        # series has a number for it (a 240 mm2 conductor is past 4/0)
        text = ' '.join(p.values('Compatible Conductor Cross-Section Range', 'mm²'))
        cross = [float(v) for v in re.findall(r'\d*\.?\d+', text)]

        if cross:
            sizes.update(common.cross_sizes(min(cross), max(cross)))
            awgs = [awg_of_cross(v) for v in (min(cross), max(cross)) if v > 0]

            if awgs and min(awgs) >= 0:
                sizes.update(wire_size_awg_min=min(awgs), wire_size_awg_max=max(awgs))

        return sizes

    if cross:
        sizes.update(common.cross_sizes(min(cross), max(cross)))
        awgs = awg or [awg_of_cross(min(cross)), awg_of_cross(max(cross))]
    elif awg:
        crosses = [common.awg_cross(a) for a in awg]
        sizes.update(common.cross_sizes(min(crosses), max(crosses)))
        awgs = awg
    else:
        return sizes

    sizes.update(wire_size_awg_min=min(awgs), wire_size_awg_max=max(awgs))
    return sizes


def plating_name(text: str | None) -> str | None:
    """A plating (``Gold (Au)``, ``Pre-Tin``, ``Tin over Nickel``) as one of the platings table's metals."""
    if not text:
        return None

    low = text.lower()

    if 'unplated' in low or low in ('none', 'non-plating'):
        return None

    for word, name in (('gold', 'Gold'), ('silver', 'Silver'), ('tin', 'Tin'), ('nickel', 'Nickel'), ('zinc', 'Zinc'),
                       ('copper', 'Copper'), ('aluminum', 'Aluminum'), ('titanium', 'Titanium')):
        if word in low:
            return name

    return text


def core_plating(text: str | None) -> str | None:
    """A conductor material (``Tin-Coated Copper``, ``Silver-Plated Copper Alloy``) as a platings table description."""
    if not text:
        return None

    low = text.lower()
    base = 'Aluminum' if 'alum' in low else 'Copper' if 'copper' in low else None

    if base is None:
        return None

    for word, plating in (('silver', 'Silver'), ('tin', 'Tin'), ('nickel', 'Nickel'), ('gold', 'Gold')):
        if word in low:
            return f'{plating}-plated {base}'

    return base


def gender_of(text: str | None) -> str | None:
    """Plug / receptacle / housing for ... as the genders table names it."""
    if not text:
        return None

    low = text.lower()

    if low in ('plug', 'housing for male terminals', 'tab housing', 'connector with male terminals', 'circular connector plug',
               'pin', 'tab', 'blade', 'solder cup pin', 'pc tail pin', 'tongue'):
        return 'Male'

    if low in ('receptacle', 'jack', 'housing for female terminals', 'circular connector receptacle', 'socket',
               'solder cup socket', 'pc tail socket'):
        return 'Female'

    return 'Unknown'


def direction_of(text: str | None) -> str | None:
    if not text:
        return None

    low = text.strip().lower()

    if low in ('straight', '180', '180°'):
        return 'Straight'

    if low in ('right angle', '90', '90°'):
        return '90°'

    return None


def cavity_lock_of(text: str | None) -> str | None:
    return {'locking lance': 'Locking Lance', 'clean body': 'Clean Body', 'integrated in housing': 'Cavity Lock',
            'contact retainer': 'Cavity Lock', 'on the terminal': 'Clean Body', 'press-fit': 'Press Fit',
            'overmolded': 'Molded On'}.get((text or '').lower())


def seal_type_of(text: str | None, catalog: common.Catalog, required: bool = False) -> str | None:
    """The seal type name. A name that is not in seal_types.json is passed on as TE writes it: the builder adds it as a new type
    (an accessory seal, which the placement code leaves alone) and the report lists it so it can be given a proper category.

    A seal's type is required by the table, so ``required`` gives a seal without one the generic ``Seal``.
    """
    if not text:
        if required:
            catalog.warn('seal without a type, called "Seal"')
            return 'Seal'

        return None

    name = re.sub(r'\s*\(.*?\)', '', text).strip()

    for known in catalog.seal_types:
        if known.lower() == name.lower():
            return known

    catalog.warn(f'seal type not in seal_types.json, the builder adds it as an accessory seal: {name!r}')
    return name


def ip_rating_of(p: Product, catalog: common.Catalog) -> str | None:
    value = p.first('IP Rating')

    if not value:
        return None

    value = value.strip().upper().replace(' ', '')

    if value in _ip_ratings:
        return value

    catalog.warn(f'IP rating not in ip_ratings.json: {value!r}')
    return None


def contact_sizes(p: Product) -> list[float]:
    sizes = []

    for value in p.values('Contact Size'):
        match = re.fullmatch(r'Size\s+(\d+)', value.strip(), re.I)

        if match:
            sizes.append(common.awg_cross(int(match.group(1))))
        elif 'K' not in value:
            number = common.number(value)

            if number is not None:
                sizes.append(number)

    return sizes


# ---------------------------------------------------------------------------------------------------------------------
# the tables
# ---------------------------------------------------------------------------------------------------------------------

def housing(p: Product, catalog: common.Catalog) -> dict:
    kind = p.first('Connector & Housing Type', 'Circular Connector Type', 'Data Bus Connector Type', 'Docking Connector Style',
                   'Solar Connector Style', 'RF Connector Style')
    gender = gender_of(kind)

    if gender in (None, 'Unknown'):
        gender = gender_of(p.first('Circular Connector Contact Type', 'Contact Type')) or gender

    pins = p.number('Number of Positions', 'Number of Coaxial Contacts', 'Number of Cores')
    rows = p.number('Number of Rows')

    return common.new_row(
        'housings', **identity(p, catalog, ('Primary Product Color', 'Housing Color')), **size(p), model3d=p.model3d,
        gender=catalog.choose('genders', gender), direction=catalog.choose('directions', direction_of(
            p.first('Body Orientation', 'Receptacle Style', 'Header Orientation'))),
        cavity_lock=cavity_lock_of(p.first('Primary Locking Feature')), ip_rating=ip_rating_of(p, catalog),
        seal_type=seal_type_of(p.first('Seal Type', 'Connector Seal & Plug Type'), catalog),
        cpa_lock_type=(p.first('Mating Retention Type') if p.first('Mating Retention Type') in _cpa_types else None),
        sealing=int(bool(p.yes('Sealable'))), rows=int(rows) if rows else 0, num_pins=int(pins) if pins else 0,
        terminal_sizes=contact_sizes(p), centerline=p.number('Centerline (Pitch)', to='mm') or 0.0)


def terminal(p: Product, catalog: common.Catalog) -> dict:
    kind = p.first('Terminal Type', 'Contact Type', 'Quick Disconnect Terminal Type')
    current = p.number('Contact Current Rating (Max)')
    seal = p.first('Terminal Seal Type')
    sealing = p.yes('Sealable')

    if seal is not None and seal != 'Unsealed':
        sealing = True

    return common.new_row(
        'terminals', **identity(p, catalog, ('Primary Product Color',)), **size(p), model3d=p.model3d,
        plating=catalog.plating(plating_name(p.first('Terminal Plating Material', 'Contact Mating Area Plating Material',
                                                     'Wire Contact Termination Area Plating Material'))),
        gender=catalog.choose('genders', gender_of(kind)) if kind else None,
        cavity_lock=cavity_lock_of(p.first('Primary Locking Feature', 'Contact Retention Type Within Housing')),
        sealing=int(bool(sealing)), blade_size=p.number('Mating Tab Width', 'Mating Pin Diameter', to='mm') or 0.0,
        mating_cycles=int(p.number('Number of Mating Cycles', 'Mating Cycles') or 0),
        max_current_ma=int(round(current * 1000)) if current else 0, **wire_size_range(p))


def seal(p: Product, catalog: common.Catalog) -> dict:
    hardness = p.number('Shore A Hardness', 'Shore A Hardness Range')
    insulation = p.span('Compatible Insulation Diameter Range')
    cavity = p.number('Cavity Diameter', to='mm')

    return common.new_row(
        'seals', **identity(p, catalog), **size(p), model3d=p.model3d,
        type=seal_type_of(p.first('Connector Seal & Plug Type'), catalog, required=True),
        hardness=int(hardness) if hardness else -1,
        lubricant='Yes' if p.yes('Contains Lubricant') else '', o_dia=cavity or 0.0, i_dia=insulation[0] if insulation else 0.0,
        **wire_size_range(p))


def cover(p: Product, catalog: common.Catalog) -> dict:
    pins = p.number('Number of Positions')

    return common.new_row(
        'covers', **identity(p, catalog), **size(p), model3d=p.model3d,
        direction=catalog.choose('directions', direction_of(p.first('Cable Exit Angle', 'Body Orientation'))),
        pins=int(pins) if pins else 0)


def boot(p: Product, catalog: common.Catalog) -> dict:
    span = p.span('Compatible Cable Diameter Range', 'Compatible Cable Diameter (Max)')
    protection = p.first('Resistance Protection')

    return common.new_row(
        'boots', **identity(p, catalog), **size(p), model3d=p.model3d, material=p.first('Primary Product Material'),
        direction=catalog.choose('directions', direction_of(p.first('Body Orientation'))),
        min_dia=span[0] if span else 0.0, max_dia=span[1] if span else 0.0,
        protection=protection if protection in _protections else None)


def lock(table: str, p: Product, catalog: common.Catalog) -> dict:
    """``tpa_locks`` and ``cpa_locks``."""
    pins = p.number('Number of Positions')
    kind = p.first('Connector & Contact Retention Accessory Type')
    short = {'TPA (Terminal Position Assurance)': 'TPA', 'CPA (Connector Position Assurance)': 'CPA'}.get(kind, kind)
    fields = dict(**identity(p, catalog), **size(p), model3d=p.model3d, pins=int(pins) if pins else 0)

    if table == 'tpa_locks':
        return common.new_row('tpa_locks', **fields, lock_type=short or '')

    return common.new_row('cpa_locks', **fields, type=short if short in _cpa_types else None)


def splice(p: Product, catalog: common.Catalog) -> dict:
    kind = p.first('Splice Type', 'Interconnect Device Splice Type', 'Joints & Splice Product Type',
                   'Compression Connector Product Type')
    name = {'Butt Splice': 'Butt', 'Pigtail Splice': 'Pigtail', 'Parallel Splice': 'Parallel', 'Thru Splice': 'Thru',
            'Closed End Splice': 'Closed End', 'Tap Splice': 'Tap', 'Cable Splice': 'Cable', 'SolderSleeve': 'Solder Sleeve',
            'Splice': 'Butt', 'Sleeve': 'Butt', 'Branch Connector': 'Tap'}.get(kind)

    if name is None:
        if p.category == 'Wedge Connectors' or 'branch' in (kind or '').lower():
            name = 'Tap'
        elif p.category == 'Joints & Splices':
            name = 'Cable'
    span = p.span('Compatible Insulation Diameter Range')

    return common.new_row(
        'splices', **identity(p, catalog), length=p.number('Product Length', to='mm') or 0.0,
        weight=p.number('Terminal & Contact Weight', 'Product Weight', to='g') or 0.0, model3d=p.model3d,
        material=p.first('Contact Base Material'),
        plating=catalog.plating(plating_name(p.first('Terminal Plating Material'))), type=catalog.choose('splice_types', name),
        min_dia=span[0] if span else 0.0, max_dia=span[1] if span else 0.0, **wire_size_range(p))


def bundle(p: Product, catalog: common.Catalog) -> dict:
    recovery = p.number('Recovery Temperature')
    recovered = p.number('Recovered Inside Diameter (Max)', to='mm')
    expanded = p.number('Expanded Inside Diameter (Min)', to='mm')

    return common.new_row(
        'bundles', **identity(p, catalog), material=p.first('Primary Product Material'),
        shrink_temp=common.temperature(recovery) if recovery is not None else None,
        rigidity=p.first('Flexibility') or '', shrink_ratio=p.first('Shrink Ratio') or '', wall=p.first('Wall Type') or '',
        min_dia=recovered or 0.0, max_dia=expanded or 0.0)


def accessory(p: Product, catalog: common.Catalog) -> dict:
    return common.new_row(
        'accessories', **{k: v for k, v in identity(p, catalog).items() if k not in ('min_temp', 'max_temp')}, **size(p),
        material=p.first('Primary Product Material'), model3d=p.model3d)


# ---------------------------------------------------------------------------------------------------------------------
# wires
# ---------------------------------------------------------------------------------------------------------------------

_RESISTANCE = re.compile(r'([-+]?\d*\.?\d+)\s*(m?)Ω\s*/\s*(1000\s*ft|1000\s*m|km|ft|m)\b', re.I)
_PER_KM = {'1000 ft': 3.28084, '1000 m': 1.0, 'km': 1.0, 'ft': 3280.84, 'm': 1000.0}


def resistance_1km(p: Product) -> float:
    """Ohms per km from ``9.19 Ω/1000 ft @ 20°C`` (the first value that is a metric or imperial length basis)."""
    for value in p.values('Resistance Rating Conditions (Max)'):
        match = _RESISTANCE.search(value)

        if match:
            factor = _PER_KM[re.sub(r'\s+', ' ', match.group(3).lower())]
            return round(float(match.group(1)) * (0.001 if match.group(2) else 1.0) * factor, 4)

    return 0.0


def colour_code(part_number: str) -> list[str] | None:
    """``44A3151-20-0/2/5/6/9`` -> the MIL-STD-681 colours of its conductors, in order."""
    match = re.search(r'-(\d(?:/\d)+)(?:-|$)', part_number)

    if match is None:
        return None

    return [MIL_COLORS[int(digit)] for digit in match.group(1).split('/')]


def conductor_colors(p: Product, count: int) -> tuple[list[str], str]:
    """The base colour of each conductor of a multi-conductor cable and where the order came from."""
    values = p.values('Wire Color (Base)')
    names = [name.strip() for value in values for name in re.split(r'\s*&\s*', value) if name.strip()]

    if len(values) == 1 and len(names) == count:
        return names, 'listed in order'

    code = colour_code(p.part_number)

    if code and sorted(code) == sorted(names) and len(code) == count:
        return code, 'part number colour code'

    if len(names) == count:
        return names, 'list order (may not be the conductor order)'

    return names, 'colour count differs from the conductor count'


def wire(p: Product, catalog: common.Catalog) -> tuple[dict, dict | None, list[str]]:
    """``(wire row, wire_conductors entry or None, notes)``."""
    notes = []

    count = p.number('Number of Conductors')
    pairs = p.number('Number of Pairs')
    style = ' '.join(p.values('Cable Style'))

    if count:
        count = int(count)
    elif pairs:
        count = int(pairs) * 2
    elif 'Twisted Pair' in style or 'Twisted Pair' in p.category:
        count = 2
    elif 'Twisted Triple' in style:
        count = 3
    else:
        count = 1

    shield_material = p.first('Shield Material', 'Shield Type')
    shielded = p.yes('Shielded')

    if shielded is None:
        shielded = bool(shield_material)
        notes.append('no Shielded feature' if shield_material else '')

    mm2 = p.numbers('Wire Size', 'mm²')
    awgs = awg_values(p)
    cross = None
    awg = None
    dia = None

    if mm2:
        cross = mm2[0]
        awg = awg_of_cross(cross) if cross else None
        dia = common.cross_dia(cross) if cross else None

        if awgs and awg is not None and abs(awgs[0] - awg) > 1:
            notes.append(f'TE says {awgs[0]} AWG for {cross} mm2; used {awg}')
    elif awgs:
        awg = awgs[0]
        cross = common.awg_cross(awg)
        dia = common.awg_dia(awg)

    od = p.span('Outside Cable Diameter')
    weight = p.number('Weight (Nominal)')
    volts = p.number('Operating Voltage')
    base_colors = p.values('Wire Color (Base)')
    cable_colors = p.values('Cable Color')
    stripes = [v for v in p.values('Wire Color (Stripe)') if v.lower() not in ('no stripe', 'none')]

    if count == 1:
        color = base_colors[0] if base_colors else (cable_colors[0] if cable_colors else None)
        stripe = stripes[0] if stripes else None
    else:
        color = cable_colors[0] if cable_colors else None  # the jacket; no colour means no jacket
        stripe = None

    kind = ' '.join(p.values('Cable Type') + p.values('Cable Style')).lower()
    wire_type = 'Ribbon' if p.category == 'Ribbon & Flat Cable' else 'Coaxial' if 'coax' in kind else None

    row = common.new_row(
        'wires', **identity(p, catalog), material=p.first('Jacket Material', 'Wire & Cable Insulation Material'),
        stripe_color=catalog.color(stripe, COLORS) if stripe else None,
        core_material=catalog.plating(core_plating(p.first('Conductor Material'))), num_conductors=count,
        shielded=int(bool(shielded)), tpi=0.0, wire_size_dia=dia, wire_size_cross=cross, wire_size_awg=awg,
        od_mm=round(sum(od) / 2, 4) if od else 0.0, weight_1km=round(weight * 1000, 3) if weight else 0.0,
        resistance_1km=resistance_1km(p), volts=volts or 0.0, strands=int(p.number('Number of Strands') or 1),
        wire_type=catalog.choose('wire_types', wire_type))

    # a single wire's colour is the wire's own; a cable's is its jacket (no colour: no jacket)
    row['color'] = catalog.color(color, COLORS) if color else None

    if count == 1 or not base_colors:
        return row, None, [n for n in notes if n]

    colors, source = conductor_colors(p, count)

    if len(colors) != count:
        notes.append(source)
        return row, None, [n for n in notes if n]

    if source.startswith('list order'):
        notes.append(source)

    entry = dict(wire=row['part_number'], common=dict(core_material=row['core_material'], material=None,
                                                      wire_size_dia=dia, wire_size_cross=cross, wire_size_awg=awg,
                                                      strands=row['strands'], od_mm=0.0, resistance_1km=row['resistance_1km']),
                 conductors=[dict(color=catalog.color(name, COLORS), stripe_color=None) for name in colors])
    return row, entry, [n for n in notes if n]
