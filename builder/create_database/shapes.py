# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.shapes')


def add_records(con, _):
    """Seed the sentinel 'No Shape' row."""

    con.execute('SELECT 1 FROM shapes LIMIT 1;')
    if con.fetchall():
        return

    data = (('No Shape',),)
    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO shapes (id, name) VALUES (?, ?);', rows)
    con.commit()


shape_cache = {}


def get_shape_id(con, name):
    """Return the id of the shape named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return shape_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM shapes WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO shapes (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('shape added %r -> %s', name, new_id.hex())

        shape_cache[name] = new_id
        return new_id
    else:
        shape_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'shapes',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
