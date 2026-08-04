# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.protections')


def add_records(con, _):
    """Seed the sentinel 'No Protection' row."""

    con.execute('SELECT 1 FROM protections LIMIT 1;')
    if con.fetchall():
        return

    data = (dict(name='No Protection'),)

    for item in data:
        add_protection(con, commit=False, **item)

    con.commit()


def add_protection(con, name, commit=True):  # NOQA
    """Insert a single protection row with a freshly generated id."""

    id = _id_generator.generate_global_row_id().bytes

    con.execute(
        'INSERT INTO protections (id, name) '
        'VALUES (?, ?);', (id, name)
        )

    _log.debug('protection added %r', name)

    if commit:
        con.commit()
        return id


protection_cache = {}


def get_protection_id(con, name):
    """Return the id of the protection named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return protection_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM protections WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO protections (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('protection added %r -> %s', name, new_id.hex())

        protection_cache[name] = new_id
        return new_id
    else:
        protection_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'protections',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
