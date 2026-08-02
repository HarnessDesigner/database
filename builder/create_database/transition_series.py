# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.transition_series')


def add_records(con, _):
    con.execute('SELECT 1 FROM transition_series LIMIT 1;')
    if con.fetchall():
        return

    data = (('Internal Use DO NOT DELETE',),)

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO transition_series (id, name) VALUES (?, ?);', rows)
    con.commit()


transition_series_cache = {}


def get_transition_series_id(con, name):
    """Return the transition series id for ``name``, auto-vivifying if missing."""
    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return transition_series_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM transition_series WHERE name=?;', (name,))
    res = con.fetchall()

    if res:
        transition_series_cache[name] = res[0][0]
        return res[0][0]

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO transition_series (id, name) VALUES (?, ?);', (new_id, name))

    _log.debug('transition series added %r -> %s', name, new_id.hex())

    transition_series_cache[name] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'transition_series',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
