"""images table -- ported from harness_designer/database/create_database/images.py.

Only the http(s) branch is reachable in this builder: every manufacturer's
image field in Aptiv/Bosch/TE/Universal source data is a remote URL, so we
only ever store the URL string, never download/embed image bytes. A local
(non-http) path would only appear during app *runtime* resource collection
(_resources.collect_resource), which this standalone builder does not port --
if a local path shows up here it's unexpected source data, not something
this builder is designed to embed.
"""

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator
from . import file_types as _file_types

_log = logging.getLogger('builder.images')

image_cache = {}


def get_image_id(con, path: str):
    # image_id is a nullable FK (schema default NULL, not the nil-UUID
    # sentinel) -- absence means "no image", stored as SQL NULL, matching
    # the original get_image_id's `return None` on a falsy path.
    if not path:
        return None

    try:
        return image_cache[path]
    except KeyError:
        pass

    con.execute('SELECT id FROM images WHERE path=?;', (path,))
    res = con.fetchall()
    if res:
        image_cache[path] = res[0][0]
        return res[0][0]

    if not path.startswith('http'):
        _log.warning('image path is not a URL, skipping (not embedded by this builder): %r', path)
        return None

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO images (id, path) VALUES (?, ?);', (new_id, path))
    _log.debug('image added %r -> %s', path, new_id.hex())

    image_cache[path] = new_id

    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'images',
    id_field,
    _con.TextField('uuid', default="NULL"),
    _con.UUIDField('file_type_id', default="NULL",
                  references=_con.SQLFieldReference(_file_types.table,
                                                    _file_types.id_field)),
    _con.BlobField('data', default='NULL'),
    _con.TextField('path', no_null=True)
)
