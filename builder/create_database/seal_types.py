# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.seal_types')


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
            item.pop('id', None)
            add_seal_type(con, commit=False, **item)

    con.commit()


def add_seal_type(con, name, commit=True):  # NOQA
    """Insert a single seal type row with a freshly generated id."""

    id = _id_generator.generate_global_row_id().bytes

    con.execute(
        'INSERT INTO seal_types (id, name) '
        'VALUES (?, ?);', (id, name)
        )

    _log.debug('seal type added %r', name)

    if commit:
        con.commit()
        return id


seal_type_cache = {}


def get_seal_type_id(con, name):
    """Return the id of the seal type named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return seal_type_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM seal_types WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO seal_types (id, name) VALUES (?, ?);', (new_id, name))

        _log.debug('seal type added %r -> %s', name, new_id.hex())

        seal_type_cache[name] = new_id
        return new_id
    else:
        seal_type_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'seal_types',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
