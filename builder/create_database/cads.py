"""cads table -- ported from harness_designer/database/create_database/cads.py.

Only the http(s) branch is reachable/desired in this builder. Bosch's `cad`
field points at a local, login-gated PDF bundled in this repo's own
Bosch/data/ folder -- those must never be embedded in the built database
(copyright), so Bosch rows have their `cad` value forced to None before
add_housing/add_cover/add_cpa_lock are ever called (see builder/create_database
housings.py/covers.py/cpa_locks.py). As a second line of defense, this
resolver itself refuses to embed any local (non-URL) path -- it logs and
returns None rather than reading/copying the file, regardless of caller.
"""

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator
from . import file_types as _file_types

_log = logging.getLogger('builder.cads')


cad_id_cache = {}



def get_cad_id(con, path: str):
    if not path:
        return None

    try:
        return cad_id_cache[path]
    except KeyError:
        pass


    con.execute('SELECT id FROM cads WHERE path=?;', (path,))
    res = con.fetchall()
    if res:
        cad_id_cache[path] = res[0][0]
        return res[0][0]

    if not path.startswith('http'):
        _log.warning('cad path is local, refusing to embed (copyright): %r', path)
        return None

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO cads (id, path) VALUES (?, ?);', (new_id, path))
    _log.debug('cad added %r -> %s', path, new_id.hex())
    cad_id_cache[path] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'cads',
    id_field,
    _con.TextField('uuid', default="NULL"),
    _con.UUIDField('file_type_id', default="NULL",
                  references=_con.SQLFieldReference(_file_types.table,
                                                    _file_types.id_field)),
    _con.BlobField('data', default='NULL'),
    _con.TextField('path', no_null=True)
)
