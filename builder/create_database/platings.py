# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.platings')


def add_records(con, data_path):
    """Seed the platings table from platings.json, if present."""

    con.execute('SELECT 1 FROM platings LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'platings.json')

    if os.path.exists(json_path):
        _log.debug(json_path)

        with open(json_path, 'r') as f:
            data = json.loads(f.read())

        if isinstance(data, dict):
            data = [value for value in data.values()]

        data_len = len(data)

        for i, item in enumerate(data):
            _log.info('Adding plating to db [%d | %d]...', i + 1, data_len)

            # platings.json is a pre-UUID-migration seed file and still
            # carries a leftover integer "id" per entry -- discard it so
            # every row gets a freshly generated UUID id instead of
            # colliding integers.
            item.pop('id', None)
            add_plating(con, commit=False, **item)

    con.commit()


def add_plating(con, symbol, description='', commit=True):  # NOQA
    """Insert a single plating row with a freshly generated id."""

    id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO platings (id, symbol, description) '
                'VALUES (?, ?, ?);', (id, symbol, description))

    _log.debug('plating added %r - %r', symbol, description)

    if commit:
        con.commit()
        return id


plating_cache = {}


def get_plating_id(con, symbol):
    """Return the id of the plating matching ``symbol`` (by symbol, then by
    description, then by a composite symbol built from descriptions found
    within ``symbol``), creating a new row on a full miss.
    """

    if not symbol:
        return _id_generator.NIL_UUID.bytes

    try:
        return plating_cache[symbol]
    except KeyError:
        pass

    con.execute('SELECT id FROM platings WHERE symbol=?;', (symbol,))
    rows = con.fetchall()

    if not rows:
        con.execute('SELECT id FROM platings WHERE description=?;', (symbol,))
        rows = con.fetchall()

    if not rows:
        con.execute('SELECT symbol, description FROM platings;')
        rows = con.fetchall()

        items = {}

        platings = {row[1]: row[0] for row in rows}

        for key, value in platings.items():
            if key.lower() in symbol.lower():
                items[symbol.lower().find(key.lower())] = value

        if items:
            description = symbol
            symbol = []
            for key in sorted(list(items.keys())):
                symbol.append(items[key])

            symbol = '/'.join(symbol)

            con.execute('SELECT id FROM platings WHERE symbol=?;', (symbol,))
            rows = con.fetchall()

            if rows:
                plating_cache[symbol] = rows[0][0]
                return rows[0][0]

        else:
            description = ''

        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO platings (id, symbol, description) VALUES (?, ?, ?);',
                    (new_id, symbol, description))

        _log.debug('plating added %r -> %s', symbol, new_id.hex())

        plating_cache[symbol] = new_id
        return new_id
    else:
        plating_cache[symbol] = rows[0][0]
        return rows[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'platings',
    id_field,
    _con.TextField('symbol', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True)
)
