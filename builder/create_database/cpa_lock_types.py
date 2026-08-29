# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.cpa_lock_types')


def add_records(con, _):
    con.execute('SELECT 1 FROM cpa_lock_types LIMIT 1;')
    if con.fetchall():
        return

    data = (('No Lock',),)

    rows = [(_id_generator.NIL_UUID.bytes, *row) for row in data]

    con.executemany('INSERT INTO cpa_lock_types (id, name) VALUES (?, ?);', rows)

    con.commit()

    data = (
        ('Lever',),
        ('Steel Lever',),
        ('Lever at Cover',),
        ('Locking Lever',),
        ('Lever Claw',),
        ('Locking Slide',),
        ('Slide',),
        ('Lever and Locking Slide',),
        ('Locking Lever and Locking Slide',),
        ('External CPA Lock',),
        ('Plastic Clip or Metal Holder',),
        ('Plastic Lever or Metal Lever',),
        ('Plastic Clip',),
        ('Groove',)
    )

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO cpa_lock_types (id, name) VALUES (?, ?);', rows)

    con.commit()


cpa_lock_type_cache = {}


def get_cpa_lock_type_id(con, name):
    """Return the CPA lock type id for ``name``, auto-vivifying if missing."""
    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return cpa_lock_type_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM cpa_lock_types WHERE name=?;', (name,))
    res = con.fetchall()

    if res:
        cpa_lock_type_cache[name] = res[0][0]
        return res[0][0]

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO cpa_lock_types (id, name) VALUES (?, ?);', (new_id, name))

    _log.debug('cpa lock type added %r -> %s', name, new_id.hex())
    cpa_lock_type_cache[name] = new_id

    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'cpa_lock_types',
    id_field,
    _con.TextField('name', no_null=True)
)
