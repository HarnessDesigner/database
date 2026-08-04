# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import json
import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.manufacturers')


def inspect_mfg_fam_series(mfg_name, family_name, series_name):
    """Normalize a (manufacturer, family, series) name triple, folding
    manufacturer-name prefixes out of family/series and special-casing the
    Raychem/TE Connectivity relationship.
    """

    if family_name is None:
        family_name = ''
    if series_name is None:
        series_name = ''

    if family_name.lower().startswith(mfg_name.lower()):
        family_name = family_name[len(mfg_name):]

    if series_name.lower().startswith(family_name.lower()):
        series_name = series_name[len(family_name):]

    if mfg_name in ('RAYCHEM', 'Raychem'):
        if not family_name.strip():
            family_name = 'Raychem'
        elif not series_name.strip():
            series_name = family_name.strip()
            family_name = 'Raychem'
        else:
            family_name = 'Raychem ' + family_name.strip()

        mfg_name = 'TE Connectivity'

    mfg_name = mfg_name.strip()
    family_name = family_name.strip()
    series_name = series_name.strip()

    if not family_name:
        family_name = None

    if not series_name:
        series_name = None

    return mfg_name, family_name, series_name


def add_records(con, data_path):
    """Seed the manufacturers table from manufacturers.json, if present."""

    con.execute('SELECT 1 FROM manufacturers LIMIT 1;')
    if con.fetchall():
        return

    json_path = os.path.join(data_path, 'manufacturers.json')

    if os.path.exists(json_path):
        _log.debug(json_path)

        with open(json_path, 'r') as f:
            data = json.loads(f.read())

        if isinstance(data, dict):
            data = [value for value in data.values()]

        data_len = len(data)

        for i, item in enumerate(data):
            _log.info('Adding manufacturer to db [%d | %d]...', i + 1, data_len)

            # manufacturers.json is a pre-UUID-migration seed file and still
            # carries a leftover integer "id" per entry -- discard it so
            # every row gets a freshly generated UUID id instead of
            # colliding integers.
            item.pop('id', None)
            add_manufacturer(con, commit=False, **item)

    con.commit()


def add_manufacturer(con, name, description='', address='', contact_person='', phone='',
                     ext='', email='', website='', commit=True):  # NOQA
    """Insert a single manufacturer row with a freshly generated id."""

    id = _id_generator.generate_global_row_id().bytes

    con.execute(
        'INSERT INTO manufacturers (id, name, description, address, contact_person, phone, ext, email, website) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);',
        (id, name, description, address, contact_person, phone, ext, email, website)
        )

    _log.debug('manufacturer added %r', name)

    if commit:
        con.commit()
        return id


mfg_cache = {}


def get_mfg_id(con, name):
    """Return the id of the manufacturer named ``name``, creating it if needed."""

    if not name:
        return _id_generator.NIL_UUID.bytes

    try:
        return mfg_cache[name]
    except KeyError:
        pass

    con.execute('SELECT id FROM manufacturers WHERE name=?;', (name,))
    res = con.fetchall()

    if not res:
        new_id = _id_generator.generate_global_row_id().bytes
        con.execute('INSERT INTO manufacturers (id, name, phone, address, email, website) '
                    'VALUES (?, ?, ?, ?, ?, ?);', (new_id, name, '', '', '', ''))

        _log.debug('manufacturer added %r -> %s', name, new_id.hex())

        mfg_cache[name] = new_id
        return new_id

    else:
        mfg_cache[name] = res[0][0]
        return res[0][0]


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'manufacturers',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True),
    _con.TextField('address', default='""', no_null=True),
    _con.TextField('contact_person', default='""', no_null=True),
    _con.TextField('phone', default='""', no_null=True),
    _con.TextField('ext', default='""', no_null=True),
    _con.TextField('email', default='""', no_null=True),
    _con.TextField('website', default='""', no_null=True)
)
