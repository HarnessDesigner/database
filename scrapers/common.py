# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Helpers shared by the manufacturer scrapers (``scrapers/<name>/collect.py`` and ``convert.py``).

The scrapers write ``<Manufacturer>/<table>.json`` files that the builder's folder-walking loaders read, so every row
has exactly the keys of the matching ``add_<part>()`` function. :func:`new_row` hands out a row with all of those keys
set to the function's defaults and refuses a key that does not exist, which keeps a typo from silently dropping a field.

A scraper imports this module with::

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import common
"""

import collections
import copy
import json
import math
import os
import re
import time

import requests


SCRAPERS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(SCRAPERS_DIR)
UNIVERSAL = os.path.join(REPO, 'Universal')

USER_AGENT = 'Mozilla/5.0 (HarnessDesigner part collector)'

# table -> JSON file name the builder reads
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

_COMMON = dict(part_number=None, description='', mfg=None, family=None, series=None, color=None, image=None,
               datasheet=None, cad=None, min_temp=None, max_temp=None)
_WIRE_SIZES = dict(wire_size_awg_min=None, wire_size_awg_max=None, wire_size_dia_min=None, wire_size_dia_max=None,
                   wire_size_cross_min=None, wire_size_cross_max=None)

# the keys and defaults of the add_<part>() functions (see builder/create_database and the application's
# database/create_database)
DEFAULTS = {
    'housings': {
        **_COMMON, 'gender': None, 'direction': None, 'model3d': None, 'cavity_lock': None, 'ip_rating': None,
        'seal_type': None, 'cpa_lock_type': None, 'sealing': 0, 'rows': 0, 'num_pins': 0, 'terminal_sizes': [],
        'terminal_size_counts': [], 'centerline': 0.0, 'compat_cpas': [], 'compat_tpas': [], 'compat_covers': [],
        'compat_terminals': [], 'compat_seals': [], 'compat_housings': [], 'compat_boots': [],
        'length': 0.0, 'width': 0.0, 'height': 0.0, 'weight': 0.0,
    },
    'terminals': {
        **_COMMON, 'model3d': None, 'plating': None, 'gender': None, 'cavity_lock': None, 'sealing': 0,
        'blade_size': 0.0, 'resistance': 0.0, 'mating_cycles': 0, 'max_vibration_g': 0, 'max_current_ma': 0,
        **_WIRE_SIZES, 'length': 0.0, 'width': 0.0, 'height': 0.0, 'weight': 0.0, 'compat_housings': [],
        'compat_seals': [],
    },
    'seals': {
        **_COMMON, 'model3d': None, 'type': None, 'hardness': -1, 'lubricant': '', 'length': 0.0, 'width': 0.0,
        'height': 0.0, 'weight': 0.0, 'o_dia': 0.0, 'i_dia': 0.0, **_WIRE_SIZES, 'compat_housings': [],
        'compat_terminals': [],
    },
    'covers': {
        **_COMMON, 'direction': None, 'model3d': None, 'length': 0.0, 'width': 0.0, 'height': 0.0, 'weight': 0.0,
        'pins': 0, 'compat_housings': [],
    },
    'boots': {
        **_COMMON, 'material': None, 'direction': None, 'model3d': None, 'length': 0.0, 'width': 0.0, 'height': 0.0,
        'weight': 0.0, 'compat_housings': [], 'min_dia': 0.0, 'max_dia': 0.0, 'protection': None,
    },
    'tpa_locks': {
        **_COMMON, 'model3d': None, 'lock_type': '', 'length': 0.0, 'width': 0.0, 'height': 0.0, 'weight': 0.0,
        'pins': 0, 'terminal_size': 0.0, 'compat_housings': [],
    },
    'cpa_locks': {
        **_COMMON, 'model3d': None, 'type': None, 'length': 0.0, 'width': 0.0, 'height': 0.0, 'weight': 0.0,
        'pins': 0, 'terminal_size': 0.0, 'compat_housings': [],
    },
    'splices': {
        **_COMMON, 'model3d': None, 'material': None, 'plating': None, 'type': None, 'min_dia': 0.0, 'max_dia': 0.0,
        'resistance': 0.0, 'length': 0.0, 'weight': 0.0, **_WIRE_SIZES, 'num_wires': None,
    },
    'bundles': {
        **_COMMON, 'material': None, 'shrink_temp': None, 'protection': None, 'rigidity': '', 'shrink_ratio': '',
        'wall': '', 'min_dia': 0.0, 'max_dia': 0.0, 'adhesive_ids': [], 'weight': 0.0,
    },
    'wires': {
        **_COMMON, 'material': None, 'stripe_color': None, 'core_material': None, 'num_conductors': 1,
        'shielded': 0, 'tpi': 0.0, 'wire_size_dia': None, 'wire_size_cross': None, 'wire_size_awg': None,
        'od_mm': 0.0, 'weight_1km': 0.0, 'resistance_1km': 0.0, 'volts': 0.0, 'strands': 1, 'wire_type': None,
    },
    'accessories': {
        'part_number': None, 'mfg': None, 'description': '', 'series': None, 'family': None, 'color': None,
        'material': None, 'image': None, 'datasheet': None, 'cad': None, 'model3d': None, 'length': 0.0,
        'width': 0.0, 'height': 0.0, 'weight': 0.0,
    },
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


def new_row(table: str, **values) -> dict:
    """A row for ``table`` with every key at its default, then ``values`` applied.

    :raises KeyError: ``values`` has a key the table's ``add_*`` function does not take.
    """
    row = copy.deepcopy(DEFAULTS[table])

    for key, value in values.items():
        if key not in row:
            raise KeyError(f'{table} has no field {key!r}')

        row[key] = value

    return row


# ---------------------------------------------------------------------------------------------------------------------
# downloading
# ---------------------------------------------------------------------------------------------------------------------

def make_session(user_agent: str = USER_AGENT) -> requests.Session:
    session = requests.Session()
    session.headers.update({'User-Agent': user_agent, 'Accept-Language': 'en-US,en;q=0.9'})
    return session


def fetch(session: requests.Session, url: str, method: str = 'GET', retries: int = 5, timeout: int = 60,
          **kwargs) -> requests.Response:
    """Request ``url``, retrying with a growing pause on network errors and 5xx answers.

    A 403 / 429 is not retried: that is the site refusing us, and it is reported instead of being worked around.
    """
    last_error = None

    for attempt in range(retries):
        try:
            response = session.request(method, url, timeout=timeout, **kwargs)

            if response.status_code in (403, 429):
                raise PermissionError(f'{url}: the site answered {response.status_code}')

            if response.status_code >= 500:
                raise requests.HTTPError(f'{response.status_code}')

            response.raise_for_status()
            return response
        except PermissionError:
            raise
        except requests.RequestException as err:
            last_error = err
            time.sleep(2 ** attempt)

    raise RuntimeError(f'{url}: {last_error}')


def write_json(path: str, data: list | dict) -> None:
    """Write a raw download cache file (atomically, so an interrupted run never leaves half a file)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    os.replace(path + '.tmp', path)


def load_json(path: str) -> list | dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------------------------------------------------
# the lookup tables the rows are checked against
# ---------------------------------------------------------------------------------------------------------------------

class Catalog:
    """The names in the ``Universal`` lookup tables. A name that is not in them would make the builder add a row."""

    def __init__(self) -> None:
        self.warnings = collections.Counter()

        self.colors = self._names('colors.json', 'name')
        self.genders = self._names('genders.json', 'name')
        self.directions = self._names('directions.json', 'name')
        self.seal_types = self._names('seal_types.json', 'name')
        self.splice_types = self._names('splice_types.json', 'name')
        self.wire_types = self._names('wire_types.json', 'name')
        self.cavity_locks = self._names('cavity_locks.json', 'name')
        self.platings = self._names('platings.json', 'description')

        self._tables = {'genders': self.genders, 'directions': self.directions, 'seal_types': self.seal_types,
                        'splice_types': self.splice_types, 'wire_types': self.wire_types,
                        'cavity_locks': self.cavity_locks}
        self._colors_folded = {name.lower(): name for name in self.colors}
        self._platings_folded = {name.lower(): name for name in self.platings}

    @staticmethod
    def _names(file_name: str, key: str) -> set[str]:
        return {entry[key] for entry in load_json(os.path.join(UNIVERSAL, file_name))}

    def warn(self, message: str) -> None:
        self.warnings[message] += 1

    def color(self, name: str | None, aliases: dict[str, str | None] | None = None) -> str | None:
        """The ``colors.json`` name for ``name`` (case does not matter), ``None`` and a warning if there is none.

        ``aliases`` maps a source's own name to the catalog's, or to ``None`` for a name that means "no colour".
        """
        if not name:
            return None

        name = name.strip()
        if aliases and name in aliases:
            name = aliases[name]

            if name is None:
                return None

        if name in self.colors:
            return name

        folded = self._colors_folded.get(name.lower())
        if folded:
            return folded

        self.warn(f'colour not in colors.json: {name!r}')
        return None

    def plating(self, name: str | None, aliases: dict[str, str | None] | None = None) -> str | None:
        """The ``platings.json`` description for ``name``."""
        if not name:
            return None

        name = name.strip()
        if aliases and name in aliases:
            name = aliases[name]

            if name is None:
                return None

        if name in self.platings:
            return name

        folded = self._platings_folded.get(name.lower())
        if folded:
            return folded

        self.warn(f'plating not in platings.json: {name!r}')
        return None

    def choose(self, table: str, name: str | None) -> str | None:
        """``name`` if it is in the named lookup table (genders, directions, seal_types, splice_types, wire_types)."""
        if not name:
            return None

        if name in self._tables[table]:
            return name

        self.warn(f'{table[:-1]} not in {table}.json: {name!r}')
        return None


# ---------------------------------------------------------------------------------------------------------------------
# value helpers
# ---------------------------------------------------------------------------------------------------------------------

NUMBER = re.compile(r'[-+]?\d*\.?\d+')


def number(value: str | float | int | None) -> float | None:
    """The first number in ``value``."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    match = NUMBER.search(value)
    if match is None:
        return None

    return float(match.group())


def temperature(value: int | float | None) -> str | None:
    """A temperature in the form the temperatures table uses: ``"-40°C"``, ``"+105°C"``."""
    if value is None:
        return None

    value = int(round(value))

    if value > 0:
        return f'+{value}°C'

    return f'{value}°C'


def awg_dia(awg: int) -> float:
    """Conductor diameter in mm of a solid wire of this AWG size."""
    return round(0.127 * 92 ** ((36 - awg) / 39), 4)


def awg_cross(awg: int) -> float:
    """Conductor cross section in mm² of this AWG size."""
    return round(math.pi / 4 * awg_dia(awg) ** 2, 4)


def cross_dia(cross: float) -> float:
    """Diameter in mm of a round conductor of this cross section in mm²."""
    return round(2 * math.sqrt(cross / math.pi), 4)


def cross_sizes(low: float | None, high: float | None) -> dict:
    """The ``wire_size_cross_*`` and ``wire_size_dia_*`` columns for a range of wire cross sections (mm²)."""
    sizes = dict(wire_size_dia_min=None, wire_size_dia_max=None, wire_size_cross_min=None, wire_size_cross_max=None)

    if not low and not high:
        return sizes

    if not low:
        low = high

    if not high:
        high = low

    low, high = sorted([low, high])

    sizes.update(wire_size_cross_min=low, wire_size_cross_max=high, wire_size_dia_min=cross_dia(low),
                 wire_size_dia_max=cross_dia(high))

    return sizes


# ---------------------------------------------------------------------------------------------------------------------
# compatibility
# ---------------------------------------------------------------------------------------------------------------------

def fill_compat(rows: dict[str, dict[str, dict]], links: list[tuple[str, str]]) -> None:
    """Fill the ``compat_*`` lists from ``links``, pairs of part numbers that belong together.

    ``rows`` is ``{table: {part number: row}}``. A link is written to both parts, in the column that suits the table
    of the other part; pairs that include a part that is not in ``rows`` are ignored.
    """
    index = {}
    for table, entries in rows.items():
        for part_number, entry in entries.items():
            index[part_number] = (table, entry)

    related = collections.defaultdict(set)
    for one, other in links:
        if one in index and other in index and one != other:
            related[one].add(other)
            related[other].add(one)

    for part_number, others in related.items():
        table, entry = index[part_number]
        columns = COMPAT_COLUMNS.get(table)

        if not columns:
            continue

        for other in sorted(others):
            column = columns.get(index[other][0])

            if column and other not in entry[column]:
                entry[column].append(other)


# ---------------------------------------------------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------------------------------------------------

def write_rows(out_dir: str, rows: dict[str, dict[str, dict]]) -> None:
    """Write ``{table: {part number: row}}`` as ``out_dir/<table>.json`` in the layout of the other data files.

    4 space indent, ``\\uXXXX`` escapes and CRLF line ends, rows sorted by part number. Prints a summary with how many
    rows have an image, datasheet, CAD drawing and 3D model link.
    """
    os.makedirs(out_dir, exist_ok=True)

    print(f'{"file":22} {"rows":>7}   with image / datasheet / cad / 3D model')

    for table, file_name in OUTPUT_FILES.items():
        entries = rows.get(table)

        if not entries:
            continue

        ordered = [entries[key] for key in sorted(entries)]

        with open(os.path.join(out_dir, file_name), 'w', encoding='utf-8', newline='\r\n') as f:
            json.dump(ordered, f, indent=4)
            f.write('\n')

        counts = []
        for key in ('image', 'datasheet', 'cad', 'model3d'):
            counts.append(sum(1 for row in ordered if row.get(key)))

        print(f'{file_name:22} {len(ordered):7}   ' + ' / '.join(str(count) for count in counts))


def report(catalog: Catalog) -> None:
    for message, count in sorted(catalog.warnings.items()):
        print(f'warning {count}x: {message}')
