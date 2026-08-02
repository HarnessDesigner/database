# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.splice_types')


def add_records(con, data_path):
    """Load ``splice_types.json`` (if present) and seed the splice_types table."""
    con.execute('SELECT 1 FROM splice_types LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'splice_types.json')

    if os.path.exists(json_path):
        _log.debug(json_path)

        with open(json_path, 'r') as f:
            data = json.loads(f.read())

        if isinstance(data, dict):
            data = [value for value in data.values()]

        for item in data:
            add_splice_type(con, commit=False, **item)

    con.commit()


def add_splice_type(con, name, id=None, commit=True):  # NOQA
    """Add a splice type row, generating a new id unless one is supplied."""
    if id is None:
        id = _id_generator.generate_global_row_id().bytes

    con.execute(
        'INSERT INTO splice_types (id, name) '
        'VALUES (?, ?);', (id, name)
        )

    _log.debug('splice type added %r', name)

    if commit:
        con.commit()
        return id


splice_type_cache = {}


def get_splice_type_id(con, name):
    """Return the splice type id for ``name``, auto-vivifying if missing."""
    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return splice_type_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM splice_types WHERE name=?;', (name,))
    res = con.fetchall()

    if res:
        splice_type_cache[name] = res[0][0]
        return res[0][0]

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO splice_types (id, name) VALUES (?, ?);', (new_id, name))

    _log.debug('splice type added %r -> %s', name, new_id.hex())

    splice_type_cache[name] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'splice_types',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
