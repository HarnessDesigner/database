"""wire_markers table -- ported from harness_designer/database/create_database/wire_markers.py."""

import json
import logging
import os

from . import manufacturers as _manufacturers
from . import colors as _colors
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads
from . import series as _series
from . import families as _families
from . import temperatures as _temperatures

from . import projects as _projects
from . import points3d as _points3d
from . import points2d as _points2d
from . import wires as _wires

from .. import sql_table as _con
from .. import id_generator as _id_generator
from ..bulk_insert import insert_data as _insert_data

_log = logging.getLogger('builder.wire_markers')


def add_wire_markers(con, data: tuple[dict] | list[dict]):
    for line in data:
        add_wire_marker(con, **line)


def add_records(con, data_path):
    con.execute('SELECT 1 FROM wire_markers LIMIT 1;')
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

        json_path = os.path.join(path, 'wire_markers.json')

        if os.path.exists(json_path):
            manufacturers = set()
            families = set()
            series_set = set()
            images = set()
            datasheets = set()
            cads = set()

            _log.info('loading %s', json_path)

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            if isinstance(data, dict):
                data = [value for value in data.values()]

            data_len = len(data)
            _log.info('adding %d %swire marker(s) to db', data_len, name)

            new_data = []

            for item in data:
                item.pop('id', None)

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
                min_diameter = item.get('min_diameter', 0.0)
                max_diameter = item.get('max_diameter', 0.0)
                wire_size_awg_min = item.get('wire_size_awg_min', None)
                wire_size_awg_max = item.get('wire_size_awg_max', None)
                wire_size_dia_min = item.get('wire_size_dia_min', None)
                wire_size_dia_max = item.get('wire_size_dia_max', None)
                wire_size_cross_min = item.get('wire_size_cross_min', None)
                wire_size_cross_max = item.get('wire_size_cross_max', None)
                length = item.get('length', 0.0)
                weight = item.get('weight', 0.0)
                has_label = item.get('has_label', 0)

                mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

                manufacturers.add(mfg)
                families.add(family)
                series_set.add(series)
                images.add(image)
                datasheets.add(datasheet)
                cads.add(cad)

                color_id = _colors.get_color_id(con, color)
                min_temp_id = _temperatures.get_temperature_id(con, min_temp)
                max_temp_id = _temperatures.get_temperature_id(con, max_temp)

                new_id = _id_generator.generate_global_row_id().bytes

                row = [new_id, part_number, description,
                       mfg, family, series, color_id, image, datasheet, cad,
                       min_temp_id, max_temp_id, min_diameter, max_diameter,
                       wire_size_awg_min, wire_size_awg_max, wire_size_dia_min,
                       wire_size_dia_max, wire_size_cross_min, wire_size_cross_max,
                       length, weight, has_label]

                new_data.append(row)

            if not new_data:
                continue

            manufacturers_mapping = _insert_data(con, manufacturers, 'manufacturers', 'name')
            images_mapping = _insert_data(con, images, 'images', 'path')
            datasheets_mapping = _insert_data(con, datasheets, 'datasheets', 'path')
            cads_mapping = _insert_data(con, cads, 'cads', 'path')

            mfg_id = manufacturers_mapping[list(manufacturers_mapping.keys())[0]]
            families_mapping = _insert_data(con, families, 'families', 'name', mfg_id=mfg_id)
            series_mapping = _insert_data(con, series_set, 'series', 'name', mfg_id=mfg_id)

            for item in new_data:
                (mfg, family, series, image, datasheet, cad) = (
                    item[3], item[4], item[5], item[7], item[8], item[9])

                mfg_id = manufacturers_mapping.get(mfg, _id_generator.NIL_UUID.bytes)
                family_id = families_mapping.get(family, _id_generator.NIL_UUID.bytes)
                series_id = series_mapping.get(series, _id_generator.NIL_UUID.bytes)
                image_id = images_mapping.get(image, None)
                datasheet_id = datasheets_mapping.get(datasheet, None)
                cad_id = cads_mapping.get(cad, None)

                item[3] = mfg_id
                item[4] = family_id
                item[5] = series_id
                item[7] = image_id
                item[8] = datasheet_id
                item[9] = cad_id

            con.executemany('INSERT INTO wire_markers (id, part_number, description, mfg_id, family_id, '
                            'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                            'max_temp_id, min_diameter, max_diameter, wire_size_awg_min, wire_size_awg_max, '
                            'wire_size_dia_min, wire_size_dia_max, wire_size_cross_min, wire_size_cross_max, '
                            'length, weight, has_label) '
                            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                            new_data)

            con.commit()

    os.chdir(cwd)


def add_wire_marker(con, part_number, description, mfg=None, family=None, series=None,
                    color=None, image=None, datasheet=None, cad=None, min_temp=None,
                    max_temp=None, min_diameter=0.0, max_diameter=0.0, wire_size_awg_min=None,
                    wire_size_awg_max=None, wire_size_dia_min=None, wire_size_dia_max=None,
                    wire_size_cross_min=None, wire_size_cross_max=None, length=0.0,
                    weight=0.0, has_label=0, commit=True):
    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    series_id = _series.get_series_id(con, series, mfg_id)
    family_id = _families.get_family_id(con, family, mfg_id)
    color_id = _colors.get_color_id(con, color)
    min_temp_id = _temperatures.get_temperature_id(con, min_temp)
    max_temp_id = _temperatures.get_temperature_id(con, max_temp)
    image_id = _images.get_image_id(con, image)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)
    cad_id = _cads.get_cad_id(con, cad)

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO wire_markers (id, part_number, description, mfg_id, family_id, '
                'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                'max_temp_id, min_diameter, max_diameter, wire_size_awg_min, wire_size_awg_max, '
                'wire_size_dia_min, wire_size_dia_max, wire_size_cross_min, wire_size_cross_max, '
                'length, weight, has_label) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id,
                 image_id, datasheet_id, cad_id, min_temp_id, max_temp_id, min_diameter,
                 max_diameter, wire_size_awg_min, wire_size_awg_max, wire_size_dia_min,
                 wire_size_dia_max, wire_size_cross_min, wire_size_cross_max, length,
                 weight, has_label))

    _log.debug('wire marker added %r -> %s', part_number, new_id.hex())

    if commit:
        con.commit()
        return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'wire_markers',
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
    _con.FloatField('min_diameter', default='"0.0"', no_null=True),
    _con.FloatField('max_diameter', default='"0.0"', no_null=True),
    _con.IntField('wire_size_awg_min', default='NULL'),
    _con.IntField('wire_size_awg_max', default='NULL'),
    _con.FloatField('wire_size_dia_min', default='NULL'),
    _con.FloatField('wire_size_dia_max', default='NULL'),
    _con.FloatField('wire_size_cross_min', default='NULL'),
    _con.FloatField('wire_size_cross_max', default='NULL'),
    _con.FloatField('length', default='"0.0"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True),
    _con.IntField('has_label', default='0', no_null=True)
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_wire_markers',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),

    _con.UUIDField('point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point2d_id', default='NULL',
                  references=_con.SQLFieldReference(_points2d.pjt_table,
                                                    _points2d.pjt_id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('wire_id', default='NULL',
                  references=_con.SQLFieldReference(_wires.pjt_table,
                                                    _wires.pjt_id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.TextField('label', default='""', no_null=True),
    _con.IntField('is_visible2d', default='1', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL')
)
