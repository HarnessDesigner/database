# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.materials')


def add_records(con, _):
    """Seed the sentinel 'Unknown Material' row."""

    con.execute('SELECT 1 FROM materials LIMIT 1;')
    if con.fetchall():
        return

    data = (('Unknown Material',),)
    rows = [(_id_generator.NIL_UUID.bytes, *row) for row in data]

    try:
        con.executemany('INSERT INTO materials (id, name) VALUES(?, ?);', rows)
        con.commit()
    except:  # NOQA
        res = con.execute('SELECT * FROM materials;').fetchall()
        _log.error(res)
        raise


material_cache = {}


def get_material_id(con, name):
    """Return the id of the material named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return material_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM materials WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO materials (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('material added %r -> %s', name, new_id.hex())

        material_cache[name] = new_id
        return new_id
    else:
        material_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'materials',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True)
)
