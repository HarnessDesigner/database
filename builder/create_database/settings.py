"""settings table -- ported from harness_designer/database/create_database/settings.py.

The original add_records() also created the models/images/cads/datasheets
folder tree (including the 256 hex subfolders) -- that's now handled once,
up front, by builder.sqlite_connector.scaffold_output_tree(), so this port
only inserts the path rows. Values are build-time paths; the app overwrites
them with real local paths after downloading/extracting this database (see
db_connectors/sqlite_connector/connector.py's connect(), which does
`UPDATE settings SET value=... WHERE name="model_path"` etc. after unpacking)
-- these rows just need to exist so that UPDATE has something to find.
"""

import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.settings')


def get_setting(con, name):
    con.execute('SELECT value FROM settings WHERE name=?;', (name,))
    res = con.fetchall()
    return res[0][0]


def add_setting(con, key, value, commit=True):
    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO settings (id, name, value) VALUES (?, ?, ?);', (new_id, key, value))
    _log.debug('setting added %r', key)

    if commit:
        con.commit()
        return new_id


def add_records(con, appdata):
    con.execute('SELECT 1 FROM settings LIMIT 1;')
    if con.fetchall():
        return

    model_path = os.path.join(appdata, 'models')
    image_path = os.path.join(appdata, 'images')
    cad_path = os.path.join(appdata, 'cads')
    datasheet_path = os.path.join(appdata, 'datasheets')

    add_setting(con, 'model_path', model_path, commit=False)
    add_setting(con, 'image_path', image_path, commit=False)
    add_setting(con, 'cad_path', cad_path, commit=False)
    add_setting(con, 'datasheet_path', datasheet_path, commit=False)

    con.commit()
    _log.info('settings seeded (model_path=%r)', model_path)


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'settings',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('value', no_null=True)
)
