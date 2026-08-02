"""models3d table -- ported from harness_designer/database/create_database/models3d.py.

get_model3d_id keeps the original's http-URL branch (store the URL string,
no download -- this is what fires for every Aptiv/TE model3d field, and for
Bosch rows with no matching local .stp). The original's local-path branch
(move the raw file into model_path via a raw file move, no real conversion)
is dropped entirely -- this builder never has a "raw model file to just
move" case. Real Bosch STP conversion happens in a separate, parallel
pre-pass (builder.bosch_convert_all, run once before any table seeding
starts) that inserts fully-converted models3d rows directly -- by the time
housings.py/covers.py/cpa_locks.py call get_model3d_id() for a Bosch part,
the row already exists and is found by its `path` string.
"""

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator
from . import file_types as _file_types

_log = logging.getLogger('builder.models3d')


model_cache = {}

def get_model3d_id(con, path: str):
    # model3d_id is a nullable FK -- absence means "no model", SQL NULL.
    if not path:
        return None

    try:
        return model_cache[path]
    except KeyError:
        pass

    con.execute('SELECT id FROM models3d WHERE path=?;', (path,))
    res = con.fetchall()
    if res:
        model_cache[path] = res[0][0]
        return res[0][0]

    if not path.startswith('http'):
        _log.warning('model3d path is local and unconverted, skipping: %r', path)
        return None

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO models3d (id, path) VALUES (?, ?);', (new_id, path))
    _log.debug('model3d added %r -> %s', path, new_id.hex())

    model_cache[path] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'models3d',
    id_field,
    _con.TextField('uuid', default="NULL"),
    _con.UUIDField('file_type_id', default="NULL",
                  references=_con.SQLFieldReference(_file_types.table,
                                                    _file_types.id_field)),
    _con.IntField('target_count', default='25000', no_null=True),
    _con.FloatField('aggressiveness', default='"5.0"', no_null=True),
    _con.IntField('update_rate', default='150', no_null=True),
    _con.IntField('iterations', default='1', no_null=True),
    _con.TextField('quat3d', default='NULL'),
    _con.TextField('angle3d', default='NULL'),
    _con.TextField('point3d', default='NULL'),
    _con.TextField('scale', default='"[1.0, 1.0, 1.0]"', no_null=True),
    _con.IntField('simplify', default='0', no_null=True),
    _con.IntField('vertex_count', default="NULL"),
    _con.TextField('aabb', default='NULL'),
    _con.TextField('obb', default='NULL'),
    _con.TextField('forward_up', default='"-1, -1"', no_null=True),
    _con.TextField('path', no_null=True)
)
