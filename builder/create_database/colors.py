# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.colors')


def add_records(con, data_path):
    """Seed the colors table from colors.json."""

    con.execute('SELECT 1 FROM colors WHERE name=? LIMIT 1;', ('Black',))
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'colors.json')

    _log.debug(json_path)

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    if isinstance(data, dict):
        data = [value for value in data.values()]

    data_len = len(data)

    for i, item in enumerate(data):
        _log.info('Adding color to db [%d | %d]...', i + 1, data_len)

        # colors.json is a pre-UUID-migration seed file and still carries a
        # leftover integer "id" per entry -- discard it so every row gets a
        # freshly generated UUID id instead of colliding integers.
        id = item.pop('id', None)
        if id == 0:
            add_color(con, id=id, commit=False, **item)
        else:
            add_color(con, commit=False, **item)

    con.commit()


def add_color(con, name, rgb, id=None, commit=True):  # NOQA
    """Insert a single color row with a freshly generated id."""

    if id is None:
        id = _id_generator.generate_global_row_id().bytes
    else:
        id = _id_generator.NIL_UUID.bytes

    con.execute('INSERT INTO colors (id, name, rgb) '
                'VALUES (?, ?, ?);', (id, name, rgb))

    _log.debug('color added %r', name)

    if commit:
        con.commit()
        return id


color_cache = {}


def get_color_id(con, name):
    """Return the id of the color named ``name`` (case-insensitive title fallback)."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return color_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM colors WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        con.execute('SELECT id FROM colors WHERE name=?;', (name.title(),))
        res = con.fetchall()

    if not res:
        _log.warning('MISSING COLOR: %r', name)
        return _id_generator.NIL_UUID.bytes
        # raise RuntimeError(name)

    color_cache[name] = res[0][0]
    return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'colors',
    id_field,
    _con.TextField('name', no_null=True),
    _con.IntField('rgb', default='""', no_null=True)
)
