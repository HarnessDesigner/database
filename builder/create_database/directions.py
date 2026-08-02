# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.directions')


def add_records(con, _):
    """Seed the fixed set of direction rows."""

    con.execute('SELECT 1 FROM directions LIMIT 1;')
    if con.fetchall():
        return

    data = (('Unknown',), ('Left',), ('Right',), ('Straight',),
            ('90°',), ('180°',), ('270°',))
    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO directions (id, name) VALUES(?, ?);', rows)
    con.commit()


direction_cache = {}

def get_direction_id(con, name):
    """Return the id of the direction named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return direction_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM directions WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO directions (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('direction added %r -> %s', name, new_id.hex())

        direction_cache[name] = new_id
        return new_id
    else:

        direction_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'directions',
    id_field,
    _con.TextField('name', no_null=True)
)
