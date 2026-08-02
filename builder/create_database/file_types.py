# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.file_types')


def add_records(con, data_path):
    """Load ``file_types.json`` and seed the file_types table."""
    con.execute('SELECT 1 FROM file_types LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'file_types.json')

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    if isinstance(data, dict):
        data = [value for value in data.values()]

    for item in data:
        add_file_type(con, commit=False, **item)

    con.commit()


def add_file_type(con, name, extension, is_model: bool | int = 0,
                  is_image: bool | int = 0, is_datasheet: bool | int = 0,
                  is_cad: bool | int = 0, mimetype: str = '', commit: bool = True):
    """Add a file type row, generating a new id."""
    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO file_types (id, mimetype, extension, name, is_model, is_image, is_datasheet, is_cad) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, mimetype, extension, name, int(is_model), int(is_image), int(is_datasheet), int(is_cad)))

    _log.debug('file type added %r', extension)

    if commit:
        con.commit()
        return new_id


file_type_cache = {}


def get_file_type(con, extension=None, mimetype=None):
    """Return the file type id, auto-vivifying by extension/mimetype if missing."""
    if extension is None and mimetype is None:
        return None

    if extension is not None and mimetype is not None:
        try:
            return file_type_cache[(extension, mimetype)]
        except KeyError:
            pass

        con.execute('SELECT id FROM file_types WHERE extension=? AND mimetype=?;', (extension, mimetype))
        res = con.fetchall()

        if res:
            file_type_cache[(extension, mimetype)] = res[0][0]
            return res[0][0]

        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO file_types (id, extension, mimetype) VALUES (?, ?, ?);', (new_id, extension, mimetype))

        _log.debug('file type added %r -> %s', extension, new_id.hex())

        file_type_cache[(extension, mimetype)] = new_id
        return new_id

    elif extension is not None:
        try:
            return file_type_cache[(extension, None)]
        except KeyError:
            pass

        con.execute('SELECT id FROM file_types WHERE extension=?;', (extension,))
        res = con.fetchall()

        if res:
            file_type_cache[(extension, None)] = res[0][0]
            return res[0][0]

        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO file_types (id, extension) VALUES (?, ?);', (new_id, extension))

        _log.debug('file type added %r -> %s', extension, new_id.hex())
        file_type_cache[(extension, None)] = new_id
        return new_id

    elif mimetype is not None:
        try:
            return file_type_cache[(None, mimetype)]
        except KeyError:
            pass

        con.execute('SELECT id FROM file_types WHERE mimetype=?;', (mimetype,))
        res = con.fetchall()

        if res:
            file_type_cache[(None, mimetype)] = res[0][0]
            return res[0][0]

        return None


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'file_types',
    id_field,
    _con.TextField('extension', no_null=True),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('mimetype', default='""', no_null=True),
    _con.IntField('is_model', default='0', no_null=True),
    _con.IntField('is_image', default='0', no_null=True),
    _con.IntField('is_datasheet', default='0', no_null=True),
    _con.IntField('is_cad', default='0', no_null=True)
)
