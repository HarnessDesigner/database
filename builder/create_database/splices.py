"""splices table -- ported from harness_designer/database/create_database/splices.py."""

import logging
import os
import json

from . import manufacturers as _manufacturers
from . import series as _series
from . import families as _families
from . import colors as _colors
from . import materials as _materials
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads
from . import platings as _platings
from . import splice_types as _splice_types
from . import temperatures as _temperatures
from . import models3d as _models3d

from . import projects as _projects
from . import points3d as _points3d
from . import points2d as _points2d
from . import points_peg as _points_peg
from . import circuits as _circuits

from .. import sql_table as _con
from .. import id_generator as _id_generator
from ..bulk_insert import insert_data as _insert_data

_log = logging.getLogger('builder.splices')


def add_records(con, data_path):
    con.execute('SELECT 1 FROM splices LIMIT 1;')
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

        json_path = os.path.join(path, 'splices.json')

        if os.path.exists(json_path):
            manufacturers = set()
            families = set()
            series_set = set()
            materials = set()
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
            _log.info('adding %d %ssplice(s) to db', data_len, name)

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
                model3d = item.get('model3d', None)
                material = item.get('material', None)
                plating = item.get('plating', None)
                type_ = item.get('type', None)
                min_dia = item.get('min_dia', 0.0)
                max_dia = item.get('max_dia', 0.0)
                resistance = item.get('resistance', 0.0)
                length = item.get('length', 0.0)
                weight = item.get('weight', 0.0)
                wire_size_awg_min = item.get('wire_size_awg_min', None)
                wire_size_awg_max = item.get('wire_size_awg_max', None)
                wire_size_dia_min = item.get('wire_size_dia_min', None)
                wire_size_dia_max = item.get('wire_size_dia_max', None)
                wire_size_cross_min = item.get('wire_size_cross_min', None)
                wire_size_cross_max = item.get('wire_size_cross_max', None)
                num_wires = item.get('num_wires', None)

                mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

                manufacturers.add(mfg)
                families.add(family)
                series_set.add(series)
                materials.add(material)
                images.add(image)
                datasheets.add(datasheet)
                cads.add(cad)
                model3ds.add(model3d)
                types.add(type_)

                color_id = _colors.get_color_id(con, color)
                min_temp_id = _temperatures.get_temperature_id(con, min_temp)
                max_temp_id = _temperatures.get_temperature_id(con, max_temp)
                plating_id = _platings.get_plating_id(con, plating)

                new_id = _id_generator.generate_global_row_id().bytes

                row = [new_id, part_number, description,
                       mfg, family, series, color_id, image, datasheet, cad,
                       min_temp_id, max_temp_id, model3d, material, plating_id, type_,
                       min_dia, max_dia, resistance, length, weight, wire_size_awg_min,
                       wire_size_awg_max, wire_size_dia_min, wire_size_dia_max,
                       wire_size_cross_min, wire_size_cross_max, num_wires]

                new_data.append(row)

            if not new_data:
                continue

            manufacturers_mapping = _insert_data(con, manufacturers, 'manufacturers', 'name')
            materials_mapping = _insert_data(con, materials, 'materials', 'name')
            images_mapping = _insert_data(con, images, 'images', 'path')
            datasheets_mapping = _insert_data(con, datasheets, 'datasheets', 'path')
            cads_mapping = _insert_data(con, cads, 'cads', 'path')
            model3ds_mapping = _insert_data(con, model3ds, 'models3d', 'path')
            types_mapping = _insert_data(con, types, 'splice_types', 'name')

            mfg_id = manufacturers_mapping[list(manufacturers_mapping.keys())[0]]
            families_mapping = _insert_data(con, families, 'families', 'name', mfg_id=mfg_id)
            series_mapping = _insert_data(con, series_set, 'series', 'name', mfg_id=mfg_id)

            for item in new_data:
                (mfg, family, series, image, datasheet, cad, model3d, material, type_) = (
                    item[3], item[4], item[5], item[7], item[8], item[9], item[12],
                    item[13], item[15])

                mfg_id = manufacturers_mapping.get(mfg, _id_generator.NIL_UUID.bytes)
                family_id = families_mapping.get(family, _id_generator.NIL_UUID.bytes)
                series_id = series_mapping.get(series, _id_generator.NIL_UUID.bytes)
                image_id = images_mapping.get(image, None)
                datasheet_id = datasheets_mapping.get(datasheet, None)
                cad_id = cads_mapping.get(cad, None)
                model3d_id = model3ds_mapping.get(model3d, None)
                material_id = materials_mapping.get(material, _id_generator.NIL_UUID.bytes)
                type_id = types_mapping.get(type_, _id_generator.NIL_UUID.bytes)

                item[3] = mfg_id
                item[4] = family_id
                item[5] = series_id
                item[7] = image_id
                item[8] = datasheet_id
                item[9] = cad_id
                item[12] = model3d_id
                item[13] = material_id
                item[15] = type_id

            con.executemany('INSERT INTO splices (id, part_number, description, mfg_id, family_id, '
                            'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                            'max_temp_id, model3d_id, material_id, plating_id, type_id, min_dia, '
                            'max_dia, resistance, length, weight, wire_size_awg_min, wire_size_awg_max, '
                            'wire_size_dia_min, wire_size_dia_max, wire_size_cross_min, '
                            'wire_size_cross_max, num_wires) '
                            'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
                            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                            new_data)

        con.commit()
    os.chdir(cwd)


def add_splices(con, data: tuple[dict] | list[dict]):
    for line in data:
        add_splice(con, **line)


def add_splice(con, part_number, description, mfg=None, family=None, series=None,
               color=None, image=None, datasheet=None, cad=None, min_temp=None,
               max_temp=None, model3d=None, material=None, plating=None, type=None,  # NOQA
               min_dia=0.0, max_dia=0.0, resistance=0.0, length=0.0, weight=0.0,
               wire_size_awg_min=None, wire_size_awg_max=None, wire_size_dia_min=None,
               wire_size_dia_max=None, wire_size_cross_min=None, wire_size_cross_max=None,
               num_wires=None, commit=True):
    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    family_id = _families.get_family_id(con, family, mfg_id)
    series_id = _series.get_series_id(con, series, mfg_id)
    color_id = _colors.get_color_id(con, color)
    material_id = _materials.get_material_id(con, material)
    image_id = _images.get_image_id(con, image)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)
    cad_id = _cads.get_cad_id(con, cad)
    min_temp_id = _temperatures.get_temperature_id(con, min_temp)
    max_temp_id = _temperatures.get_temperature_id(con, max_temp)
    plating_id = _platings.get_plating_id(con, plating)
    type_id = _splice_types.get_splice_type_id(con, type)
    model3d_id = _models3d.get_model3d_id(con, model3d)

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO splices (id, part_number, description, mfg_id, family_id, '
                'series_id, color_id, image_id, datasheet_id, cad_id, min_temp_id, '
                'max_temp_id, model3d_id, material_id, plating_id, type_id, min_dia, '
                'max_dia, resistance, length, weight, wire_size_awg_min, wire_size_awg_max, '
                'wire_size_dia_min, wire_size_dia_max, wire_size_cross_min, '
                'wire_size_cross_max, num_wires) '
                'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
                '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id,
                 image_id, datasheet_id, cad_id, min_temp_id, max_temp_id, model3d_id,
                 material_id, plating_id, type_id, min_dia, max_dia, resistance,
                 length, weight, wire_size_awg_min, wire_size_awg_max, wire_size_dia_min,
                 wire_size_dia_max, wire_size_cross_min, wire_size_cross_max, num_wires))

    _log.debug('splice added %r -> %s', part_number, new_id.hex())

    if commit:
        con.commit()
        return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'splices',
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
    _con.UUIDField('material_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_materials.table,
                                                    _materials.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('plating_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_platings.table,
                                                    _platings.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('type_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_splice_types.table,
                                                    _splice_types.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.FloatField('min_dia', default='"0.0"', no_null=True),
    _con.FloatField('max_dia', default='"0.0"', no_null=True),
    _con.FloatField('resistance', default='"0.0"', no_null=True),
    _con.FloatField('length', default='"0.0"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True),
    _con.IntField('wire_size_awg_min', default='NULL'),
    _con.IntField('wire_size_awg_max', default='NULL'),
    _con.FloatField('wire_size_dia_min', default='NULL'),
    _con.FloatField('wire_size_dia_max', default='NULL'),
    _con.FloatField('wire_size_cross_min', default='NULL'),
    _con.FloatField('wire_size_cross_max', default='NULL'),
    _con.IntField('num_wires', default='NULL'),
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_splices',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),

    _con.UUIDField('start_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('stop_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),

    _con.UUIDField('branch_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point2d_id', default="NULL",
                  references=_con.SQLFieldReference(_points2d.pjt_table,
                                                    _points2d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point_peg_id', default="NULL",
                  references=_con.SQLFieldReference(_points_peg.pjt_table,
                                                    _points_peg.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('quatpeg', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('anglepeg', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.UUIDField('circuit_id', default='NULL',
                  references=_con.SQLFieldReference(_circuits.pjt_table,
                                                    _circuits.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('scale3d_id', default='NULL',
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_DEFAULT,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.IntField('is_visible2d', default='1', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL')
)
