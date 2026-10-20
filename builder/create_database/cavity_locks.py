# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import seed_json as _seed_json
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.cavity_locks')


def add_records(con, data_path):
    """Seed cavity_locks from cavity_locks.json; its "id": 0 entry ('No Lock') is the nil UUID default row."""

    _seed_json.seed(con, data_path, 'cavity_locks.json', 'cavity_locks', ('name',))


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
