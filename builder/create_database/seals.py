"""seals table -- ported from harness_designer/database/create_database/seals.py.

Fixes a copy-paste bug in the original DDL: `family_id`'s SQLFieldReference
pointed at `_series.table`/`_series.id_field` instead of `_families.table`/
`_families.id_field`. Corrected here.

Fully generic -- no Bosch STP matches for this table.
"""

import logging
import os
import json

from . import temperatures as _temperatures
from . import manufacturers as _manufacturers
from . import series as _series
from . import colors as _colors
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads
from . import models3d as _models3d
from . import seal_types as _seal_types
from . import families as _families

from . import projects as _projects
from . import points3d as _points3d
from . import housings as _housings
from . import cavities as _cavities
from . import terminals as _terminals

from .. import sql_table as _con
from .. import id_generator as _id_generator
from ..bulk_insert import insert_data as _insert_data

_log = logging.getLogger('builder.seals')


def add_seal(con, part_number, description, mfg=None, family=None, series=None,
             color=None, image=None, datasheet=None, cad=None, min_temp=None,
             max_temp=None, model3d=None, type=None, hardness=-1, lubricant='',  # NOQA
             length=0.0, width=0.0, height=0.0, weight=0.0, o_dia=0.0, i_dia=0.0,
             wire_size_dia_min=None, wire_size_dia_max=None, wire_size_cross_min=None,
             wire_size_cross_max=None, wire_size_awg_min=None, wire_size_awg_max=None,
             compat_housings=None, compat_terminals=None, commit=True):
    if compat_housings is None:
        compat_housings = []
    if compat_terminals is None:
        compat_terminals = []
    if color is None:
        color = 'Dark Gray'

    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    series_id = _series.get_series_id(con, series, mfg_id)
    family_id = _families.get_family_id(con, family, mfg_id)
    color_id = _colors.get_color_id(con, color)
    image_id = _images.get_image_id(con, image)
    cad_id = _cads.get_cad_id(con, cad)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)
    model3d_id = _models3d.get_model3d_id(con, model3d)
    type_id = _seal_types.get_seal_type_id(con, type)
    min_temp_id = _temperatures.get_temperature_id(con, min_temp)
    max_temp_id = _temperatures.get_temperature_id(con, max_temp)

    if not description:
        description = mfg
        if series:
            description += f' {series}'
        if color:
            description += f' {color}'
        if wire_size_dia_min:
            description += f' {wire_size_dia_min}mm'
        if wire_size_dia_max:
            if wire_size_dia_min:
                description += ' -'
            description += f' {wire_size_dia_max}mm'
        if type:
            description += f' {type}'
        description += ' Seal'

    compat_housings = ', '.join(compat_housings)
    compat_terminals = ', '.join(compat_terminals)

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO seals (id, part_number, description, mfg_id, family_id, '
                'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                'max_temp_id, model3d_id, type_id, hardness, lubricant, length, '
                'width, height, weight, o_dia, i_dia, wire_size_dia_min, wire_size_dia_max, '
                'wire_size_cross_min, wire_size_cross_max, wire_size_awg_min, wire_size_awg_max, '
                'compat_housings, compat_terminals) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
                '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id,
                 image_id, datasheet_id, cad_id, min_temp_id, max_temp_id, model3d_id,
                 type_id, hardness, lubricant, length, width, height, weight, o_dia,
                 i_dia, wire_size_dia_min, wire_size_dia_max, wire_size_cross_min, wire_size_cross_max,
                 wire_size_awg_min, wire_size_awg_max, compat_housings, compat_terminals))

    _log.debug('seal added %r -> %s', part_number, new_id.hex())

    if commit:
        con.commit()
        return new_id


def add_seals(con, data: tuple[dict] | list[dict]):
    for line in data:
        add_seal(con, **line)


def add_records(con, data_path):
    con.execute('SELECT 1 FROM seals LIMIT 1;')
    if con.fetchall():
        return

    dirs = [('', data_path)]

    for file_name in os.listdir(data_path):
        file = os.path.join(data_path, file_name)
        if os.path.isdir(file):
            dirs.append((file_name + ' ', file))

    cwd = os.getcwd()
    for name, path in dirs:
        os.chdir(path)

        json_path = os.path.join(path, 'seals.json')
        if os.path.exists(json_path):
            manufacturers = set()
            families = set()
            series_set = set()
            images = set()
            datasheets = set()
            cads = set()
            model3ds = set()
            types = set()

            _log.info('loading %s', json_path)

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            if isinstance(data, dict):
                data = [value for value in data.values()]

            data_len = len(data)
            _log.info('adding %d %sseal(s) to db', data_len, name)

            new_data = []

            for item in data:
                item.pop('id', None)

                if 'shared_cad' in item:
                    del item['shared_cad']
                if 'shared_model3d' in item:
                    del item['shared_model3d']

                mfg = item.get('mfg', None)
                family = item.get('family', None)
                series = item.get('series', None)
                part_number = item.get('part_number')
                description = item.get('description', None)
                color = item.get('color', None)
                image = item.get('image', None)
                datasheet = item.get('datasheet', None)
                cad = item.get('cad', None)
                min_temp = item.get('min_temp', None)
                max_temp = item.get('max_temp', None)
                model3d = item.get('model3d', None)
                type_ = item.get('type', None)
                hardness = item.get('hardness', -1)
                lubricant = item.get('lubricant', '')
                length = item.get('length', 0.0)
                width = item.get('width', 0.0)
                height = item.get('height', 0.0)
                weight = item.get('weight', 0.0)
                o_dia = item.get('o_dia', 0.0)
                i_dia = item.get('i_dia', 0.0)
                wire_size_dia_min = item.get('wire_size_dia_min', None)
                wire_size_dia_max = item.get('wire_size_dia_max', None)
                wire_size_cross_min = item.get('wire_size_cross_min', None)
                wire_size_cross_max = item.get('wire_size_cross_max', None)
                wire_size_awg_min = item.get('wire_size_awg_min', None)
                wire_size_awg_max = item.get('wire_size_awg_max', None)
                compat_housings = item.get('compat_housings', None)
                compat_terminals = item.get('compat_terminals', None)

                if compat_housings is None:
                    compat_housings = []
                if compat_terminals is None:
                    compat_terminals = []
                if color is None:
                    color = 'Dark Gray'

                mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

                manufacturers.add(mfg)
                families.add(family)
                series_set.add(series)
                images.add(image)
                datasheets.add(datasheet)
                cads.add(cad)
                model3ds.add(model3d)
                types.add(type_)

                color_id = _colors.get_color_id(con, color)
                min_temp_id = _temperatures.get_temperature_id(con, min_temp)
                max_temp_id = _temperatures.get_temperature_id(con, max_temp)

                if not description:
                    description = mfg
                    if series:
                        description += f' {series}'
                    if color:
                        description += f' {color}'
                    if wire_size_dia_min:
                        description += f' {wire_size_dia_min}mm'
                    if wire_size_dia_max:
                        if wire_size_dia_min:
                            description += ' -'
                        description += f' {wire_size_dia_max}mm'
                    if type_:
                        description += f' {type_}'
                    description += ' Seal'

                compat_housings = ', '.join(compat_housings)
                compat_terminals = ', '.join(compat_terminals)

                new_id = _id_generator.generate_global_row_id().bytes

                row = [new_id, part_number, description,
                       mfg, family, series, color_id, image, datasheet, cad,
                       min_temp_id, max_temp_id, model3d, type_,
                       hardness, lubricant, length, width, height, weight, o_dia, i_dia,
                       wire_size_dia_min, wire_size_dia_max, wire_size_cross_min,
                       wire_size_cross_max, wire_size_awg_min, wire_size_awg_max,
                       compat_housings, compat_terminals]

                new_data.append(row)

            if not new_data:
                continue

            manufacturers_mapping = _insert_data(con, manufacturers, 'manufacturers', 'name')
            images_mapping = _insert_data(con, images, 'images', 'path')
            datasheets_mapping = _insert_data(con, datasheets, 'datasheets', 'path')
            cads_mapping = _insert_data(con, cads, 'cads', 'path')
            model3ds_mapping = _insert_data(con, model3ds, 'models3d', 'path')
            types_mapping = _insert_data(con, types, 'seal_types', 'name')

            mfg_id = manufacturers_mapping[list(manufacturers_mapping.keys())[0]]
            families_mapping = _insert_data(con, families, 'families', 'name', mfg_id=mfg_id)
            series_mapping = _insert_data(con, series_set, 'series', 'name', mfg_id=mfg_id)

            for item in new_data:
                (mfg, family, series, image, datasheet, cad, model3d, type_) = (
                    item[3], item[4], item[5], item[7], item[8], item[9], item[12], item[13])

                mfg_id = manufacturers_mapping.get(mfg, _id_generator.NIL_UUID.bytes)
                family_id = families_mapping.get(family, _id_generator.NIL_UUID.bytes)
                series_id = series_mapping.get(series, _id_generator.NIL_UUID.bytes)
                image_id = images_mapping.get(image, None)
                datasheet_id = datasheets_mapping.get(datasheet, None)
                cad_id = cads_mapping.get(cad, None)
                model3d_id = model3ds_mapping.get(model3d, None)
                # No sentinel fallback -- a seal part's own type is
                # required (see the type_id field's own definition
                # below); an unrecognized/blank type_ here should fail
                # loudly against that NOT NULL constraint on insert,
                # not silently reference a dangling id.
                type_id = types_mapping.get(type_, None)

                item[3] = mfg_id
                item[4] = family_id
                item[5] = series_id
                item[7] = image_id
                item[8] = datasheet_id
                item[9] = cad_id
                item[12] = model3d_id
                item[13] = type_id

            con.executemany('INSERT INTO seals (id, part_number, description, mfg_id, family_id, '
                            'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                            'max_temp_id, model3d_id, type_id, hardness, lubricant, length, '
                            'width, height, weight, o_dia, i_dia, wire_size_dia_min, wire_size_dia_max, '
                            'wire_size_cross_min, wire_size_cross_max, wire_size_awg_min, wire_size_awg_max, '
                            'compat_housings, compat_terminals) '
                            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
                            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                            new_data)

        con.commit()
    os.chdir(cwd)


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'seals',
    id_field,
    _con.TextField('part_number', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True),
    _con.UUIDField('mfg_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_manufacturers.table,
                                                    _manufacturers.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('family_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_families.table,
                                                    _families.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('series_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_series.table,
                                                    _series.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('color_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_colors.table,
                                                    _colors.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('image_id', default='NULL',
                  references=_con.SQLFieldReference(_images.table,
                                                    _images.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('datasheet_id', default='NULL',
                  references=_con.SQLFieldReference(_datasheets.table,
                                                    _datasheets.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cad_id', default='NULL',
                  references=_con.SQLFieldReference(_cads.table,
                                                    _cads.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('min_temp_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_temperatures.table,
                                                    _temperatures.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('max_temp_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_temperatures.table,
                                                    _temperatures.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('model3d_id', default='NULL',
                  references=_con.SQLFieldReference(_models3d.table,
                                                    _models3d.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    # No sentinel default -- an actual seal part's own type is required,
    # so omitting it on insert must fail loudly against this NOT NULL
    # constraint rather than silently falling back to a placeholder row
    # (seal_types no longer carries one -- see create_database.
    # seal_types.get_seal_type_id's own docstring).
    _con.UUIDField('type_id', no_null=True,
                  references=_con.SQLFieldReference(_seal_types.table,
                                                    _seal_types.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('hardness', default='-1', no_null=True),
    _con.TextField('lubricant', default='""', no_null=True),
    _con.FloatField('length', default='"0.0"', no_null=True),
    _con.FloatField('width', default='"0.0"', no_null=True),
    _con.FloatField('height', default='"0.0"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True),
    _con.FloatField('o_dia', default='"0.0"', no_null=True),
    _con.FloatField('i_dia', default='"0.0"', no_null=True),
    _con.FloatField('wire_size_dia_min', default='NULL'),
    _con.FloatField('wire_size_dia_max', default='NULL'),
    _con.FloatField('wire_size_cross_min', default='NULL'),
    _con.FloatField('wire_size_cross_max', default='NULL'),
    _con.FloatField('wire_size_awg_min', default='NULL'),
    _con.FloatField('wire_size_awg_max', default='NULL'),
    _con.TextField('compat_housings', default='""', no_null=True),
    _con.TextField('compat_terminals', default='""', no_null=True)
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_seals',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point3d_id', no_null=True,
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('housing_id', default='NULL',
                  references=_con.SQLFieldReference(_housings.pjt_table,
                                                    _housings.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('terminal_id', default='NULL',
                  references=_con.SQLFieldReference(_terminals.pjt_table,
                                                    _terminals.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cavity_id', default='NULL',
                  references=_con.SQLFieldReference(_cavities.pjt_table,
                                                    _cavities.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('scale3d_id', default='NULL',
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_DEFAULT,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.TextField('quat3d', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('angle3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL')
)
