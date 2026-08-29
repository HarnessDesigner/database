# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.cavity_locks')


def add_records(con, _):
    """Seed the fixed set of cavity lock rows."""

    con.execute('SELECT 1 FROM cavity_locks LIMIT 1;')
    if con.fetchall():
        return

    data = (('No Lock',),)
    rows = [(_id_generator.NIL_UUID.bytes, *row) for row in data]

    con.executemany('INSERT INTO cavity_locks (id, name) VALUES (?, ?);', rows)

    con.commit()

    data = (
        ('Cavity Lock',),
        ('Clean Body',),
        ('Locking Lance',),
        ('Clean Body and Lance',),
        ('Flex Arm',),
        ('Insert Molded',),
        ('Molded On',),
        ('Nose Piece',),
        ('Press Fit',)
    )
    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO cavity_locks (id, name) VALUES (?, ?);', rows)

    con.commit()


cavity_lock_cache = {}


def get_cavity_lock_id(con, name):
    """Return the id of the cavity lock named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return cavity_lock_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM cavity_locks WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO cavity_locks (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('cavity lock added %r -> %s', name, new_id.hex())

        cavity_lock_cache[name] = new_id
        return new_id
    else:
        cavity_lock_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'cavity_locks',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True)
)
