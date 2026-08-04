# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.temperatures')


def add_records(con, data_path):
    """Load ``temperatures.json`` (if present) and seed the temperatures table."""
    con.execute('SELECT 1 FROM temperatures LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'temperatures.json')

    if os.path.exists(json_path):
        _log.debug(json_path)

        with open(json_path, 'r') as f:
            data = json.loads(f.read())

        if isinstance(data, dict):
            data = [value for value in data.values()]

        for item in data:
            # temperatures.json is a pre-UUID-migration seed file and still
            # carries a leftover integer "id" per entry -- discard it so
            # every row gets a freshly generated UUID id instead of
            # colliding integers.
            item.pop('id', None)
            add_temperature(con, commit=False, **item)

    con.commit()


def add_temperature(con, name, commit=True):  # NOQA
    """Add a temperature row with a freshly generated id."""
    id = _id_generator.generate_global_row_id().bytes

    con.execute(
        'INSERT INTO temperatures (id, name) '
        'VALUES (?, ?);', (id, name)
        )

    _log.debug('temperature added %r', name)

    if commit:
        con.commit()
        return id


temp_cache = {}


def get_temperature_id(con, name):
    """Return the temperature id for ``name``, auto-vivifying if missing."""
    if name in ('', None):
        return _id_generator.NIL_UUID.bytes

    if isinstance(name, str):
        if '-' in name:
            name = -int(name[1:].replace('°', '').replace('C', ''))
        else:
            name = int(name.replace('°', '').replace('C', ''))

    if name > 0:
        name = '+' + str(name) + '°C'
    else:
        name = str(name) + '°C'

    try:
        return temp_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM temperatures WHERE name=?;', (name,))
    res = con.fetchall()

    if res:
        temp_cache[name] = res[0][0]
        return res[0][0]

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO temperatures (id, name) VALUES (?, ?);', (new_id, name))

    _log.debug('temperature added %r -> %s', name, new_id.hex())
    temp_cache[name] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'temperatures',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True)
)
