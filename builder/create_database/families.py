# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from . import manufacturers as _manufacturers
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.families')


def add_records(con, _):
    """Seed the sentinel 'No Family' row."""

    con.execute('SELECT 1 FROM families LIMIT 1;')
    if con.fetchall():
        return

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO families (id, name, mfg_id) VALUES(?, ?, ?);',
                (new_id, 'No Family', _id_generator.NIL_UUID.bytes))
    con.commit()

family_cache = {}

def get_family_id(con, name, mfg_id):
    """Return the id of the family named ``name`` under ``mfg_id``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return family_cache[(name, mfg_id)]
    except KeyError:
        pass

    con.execute('SELECT id FROM families WHERE name=? AND mfg_id=?;', (name, mfg_id))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO families (id, name, mfg_id) VALUES (?, ?, ?);', (new_id, name, mfg_id))

        _log.debug('family added %r -> %s', name, new_id.hex())

        family_cache[(name, mfg_id)] = new_id
        return new_id
    else:
        family_cache[(name, mfg_id)] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'families',
    id_field,
    _con.TextField('name', no_null=True),
    _con.TextField('description', default='""', no_null=True),
    _con.UUIDField('mfg_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_manufacturers.table,
                                                    _manufacturers.id_field,
                                                    on_update=_con.REFERENCE_CASCADE))
)
