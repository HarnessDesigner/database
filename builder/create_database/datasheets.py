"""datasheets table -- ported from harness_designer/database/create_database/datasheets.py.

Same treatment as cads.py: Bosch's `datasheet` field (where present) points
at a local, login-gated file -- never embedded. Only the http(s) branch is
reachable/desired; a local path is refused defensively even if the caller
forgot to null it out.
"""

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator
from . import file_types as _file_types

_log = logging.getLogger('builder.datasheets')


datasheet_cache = {}

def get_datasheet_id(con, path: str):
    if not path:
        return None

    try:
        return datasheet_cache[path]
    except KeyError:
        pass

    con.execute('SELECT id FROM datasheets WHERE path=?;', (path,))
    res = con.fetchall()
    if res:
        datasheet_cache[path] = res[0][0]
        return res[0][0]

    if not path.startswith('http'):
        _log.warning('datasheet path is local, refusing to embed (copyright): %r', path)
        return None

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO datasheets (id, path) VALUES (?, ?);', (new_id, path))
    _log.debug('datasheet added %r -> %s', path, new_id.hex())

    datasheet_cache[path] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'datasheets',
    id_field,
    _con.TextField('uuid', default="NULL"),
    _con.UUIDField('file_type_id', default="NULL",
                  references=_con.SQLFieldReference(_file_types.table,
                                                    _file_types.id_field)),
    _con.BlobField('data', default='NULL'),
    _con.TextField('path', no_null=True)
)
