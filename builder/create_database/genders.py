# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.genders')


def add_records(con, _):
    """Seed the fixed set of gender rows."""

    con.execute('SELECT 1 FROM genders LIMIT 1;')
    if con.fetchall():
        return

    data = (('Unknown',),)
    rows = [(_id_generator.NIL_UUID.bytes, *row) for row in data]

    con.executemany('INSERT INTO genders (id, name) VALUES(?, ?);', rows)
    con.commit()

    data = (('Male',), ('Female',))
    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO genders (id, name) VALUES(?, ?);', rows)
    con.commit()


gender_cache = {}


def get_gender_id(con, name):
    """Return the id of the gender named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return gender_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM genders WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO genders (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('gender added %r -> %s', name, new_id.hex())

        gender_cache[name] = new_id
        return new_id
    else:
        gender_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'genders',
    id_field,
    _con.TextField('name', no_null=True)
)
