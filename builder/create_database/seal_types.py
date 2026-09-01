# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.seal_types')

# Seal category codes -- what harness_designer's own placement logic
# actually branches on (see add_handlers.editor_3d.seal there),
# independent of whichever free-text `name` a given manufacturer's
# catalog happens to use for the same real-world seal category.
CATEGORY_SWS = 'SWS'
CATEGORY_MAT = 'MAT'
CATEGORY_PLUG = 'PLUG'
CATEGORY_ACC = 'ACC'

CATEGORIES = (CATEGORY_SWS, CATEGORY_MAT, CATEGORY_PLUG, CATEGORY_ACC)

# Fallback for get_seal_type_id's own auto-create path when a caller
# doesn't know the category of a name it's never seen before -- ACC
# ("all other seals that don't fit into the categories above") is the
# correct default for "uncategorized" specifically because it's the
# one category harness_designer's own snap-target logic never treats
# as cavity/terminal-relevant, so a wrongly-defaulted new type fails
# safe (excluded from snapping) rather than wrongly participating.
_DEFAULT_CATEGORY = CATEGORY_ACC


def add_records(con, data_path):
    """Seed the seal_types table from seal_types.json, if present."""

    con.execute('SELECT 1 FROM seal_types LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'seal_types.json')

    if os.path.exists(json_path):
        _log.debug(json_path)

        with open(json_path, 'r') as f:
            data = json.loads(f.read())

        if isinstance(data, dict):
            data = [value for value in data.values()]

        data_len = len(data)

        for i, item in enumerate(data):
            _log.info('Adding seal type to db [%d | %d]...', i + 1, data_len)

            # seal_types.json is a pre-UUID-migration seed file and still
            # carries a leftover integer "id" per entry -- discard it so
            # every row gets a freshly generated UUID id instead of
            # colliding integers.
            id = item.pop('id', None)
            if id == 0:
                add_seal_type(con, id=id, commit=False, **item)
            else:
                add_seal_type(con, commit=False, **item)

    con.commit()


def add_seal_type(con, name, category, id=None, commit=True):  # NOQA
    """Insert a single seal type row with a freshly generated id.

    :param category: One of :data:`CATEGORIES` -- required, since this
        is what harness_designer's own placement logic actually
        branches on, independent of *name*.
    """

    if id is None:
        id = _id_generator.generate_global_row_id().bytes
    else:
        id = _id_generator.NIL_UUID.bytes

    con.execute(
        'INSERT INTO seal_types (id, name, category) '
        'VALUES (?, ?, ?);', (id, name, category)
        )

    _log.debug('seal type added %r (%s)', name, category)

    if commit:
        con.commit()
        return id


seal_type_cache = {}


def get_seal_type_id(con, name, category=None):
    """Return the id of the seal type named ``name``, creating it if
    needed.

    :param name: Type name to resolve. Falsy (unset) is a legitimate
        state for a housing's own seal type (which may genuinely have
        none) -- returns ``None`` (SQL NULL) in that case, never a
        nil-UUID sentinel row (seal_types carries no placeholder
        "None"/"Unknown" row) -- an actual seal part's own type, unlike
        a housing's, is required and never reaches this branch with a
        falsy *name*.
    :param category: Category for a newly-created row (see
        :data:`CATEGORIES`). Only consulted when *name* doesn't already
        exist; falls back to :data:`_DEFAULT_CATEGORY` (logged) when
        not given, since every name seal_types.json seeds is already
        known ahead of time and only hits this auto-create path for a
        genuinely new, not-yet-classified manufacturer string.
    """

    if not name:
        return None

    try:
        return seal_type_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM seal_types WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        if category is None:
            category = _DEFAULT_CATEGORY
            _log.warning(
                'adding seal type %r with no category given -- defaulting to %s, '
                'needs a real classification later', name, _DEFAULT_CATEGORY)

        new_id = _id_generator.generate_global_row_id().bytes
        con.execute(
            'INSERT INTO seal_types (id, name, category) VALUES (?, ?, ?);',
            (new_id, name, category))

        _log.debug('seal type added %r (%s) -> %s', name, category, new_id.hex())

        seal_type_cache[name] = new_id
        return new_id
    else:
        seal_type_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'seal_types',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('category', no_null=True, default=f"'{_DEFAULT_CATEGORY}'"),
)
