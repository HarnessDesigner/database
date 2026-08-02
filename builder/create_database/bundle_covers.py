"""bundle_covers table -- ported from harness_designer/database/create_database/bundle_covers.py.

TE/bundles.json is this table's data source (the JSON filename doesn't match
the table name -- confirmed by reading the original add_records, which reads
'bundles.json' while defining/seeding the 'bundle_covers' table).
"""

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
from . import protections as _protections
from . import temperatures as _temperatures

from . import projects as _projects
from . import points3d as _points3d

from .. import sql_table as _con
from .. import id_generator as _id_generator
from ..bulk_insert import insert_data as _insert_data

_log = logging.getLogger('builder.bundle_covers')


def add_bundle_covers(con, data: tuple[dict] | list[dict]):
    for line in data:
        add_bundle_cover(con, **line)


def add_records(con, data_path):
    con.execute('SELECT 1 FROM bundle_covers LIMIT 1;')
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

        json_path = os.path.join(path, 'bundles.json')

        if os.path.exists(json_path):
            manufacturers = set()
            families = set()
            series_set = set()
            materials = set()
            images = set()
            datasheets = set()
            cads = set()
            protections = set()

            _log.info('loading %s', json_path)

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            if isinstance(data, dict):
                data = [value for value in data.values()]

            data_len = len(data)
            _log.info('adding %d %sbundle cover(s) to db', data_len, name)

            new_data = []

            for item in data:
                item.pop('id', None)

                mfg = item.get('mfg', None)
                family = item.get('family', None)
                series = item.get('series', None)
                part_number = item.get('part_number')
                description = item.get('description', None)
                color = item.get('color', None)
                material = item.get('material', None)
                image = item.get('image', None)
                datasheet = item.get('datasheet', None)
                cad = item.get('cad', None)
                shrink_temp = item.get('shrink_temp', None)
                min_temp = item.get('min_temp', None)
                max_temp = item.get('max_temp', None)
                protection = item.get('protection', None)
                rigidity = item.get('rigidity', '')
                shrink_ratio = item.get('shrink_ratio', '')
                wall = item.get('wall', '')
                min_dia = item.get('min_dia', 0.0)
                max_dia = item.get('max_dia', 0.0)
                adhesive_ids = item.get('adhesive_ids', None)
                weight = item.get('weight', 0.0)

                if adhesive_ids is None:
                    adhesive_ids = []

                mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

                manufacturers.add(mfg)
                families.add(family)
                series_set.add(series)
                materials.add(material)
                images.add(image)
                datasheets.add(datasheet)
                cads.add(cad)
                protections.add(protection)

                color_id = _colors.get_color_id(con, color)
                shrink_temp_id = _temperatures.get_temperature_id(con, shrink_temp)
                min_temp_id = _temperatures.get_temperature_id(con, min_temp)
                max_temp_id = _temperatures.get_temperature_id(con, max_temp)

                adhesive_ids = ', '.join(adhesive_ids)

                new_id = _id_generator.generate_global_row_id().bytes

                row = [new_id, part_number, description,
                       mfg, family, series, color_id, material, image, datasheet, cad,
                       shrink_temp_id, min_temp_id, max_temp_id, protection,
                       rigidity, shrink_ratio, wall, min_dia, max_dia, adhesive_ids, weight]

                new_data.append(row)

            if not new_data:
                continue

            manufacturers_mapping = _insert_data(con, manufacturers, 'manufacturers', 'name')
            materials_mapping = _insert_data(con, materials, 'materials', 'name')
            images_mapping = _insert_data(con, images, 'images', 'path')
            datasheets_mapping = _insert_data(con, datasheets, 'datasheets', 'path')
            cads_mapping = _insert_data(con, cads, 'cads', 'path')
            protections_mapping = _insert_data(con, protections, 'protections', 'name')

            mfg_id = manufacturers_mapping[list(manufacturers_mapping.keys())[0]]
            families_mapping = _insert_data(con, families, 'families', 'name', mfg_id=mfg_id)
            series_mapping = _insert_data(con, series_set, 'series', 'name', mfg_id=mfg_id)

            for item in new_data:
                (mfg, family, series, material, image, datasheet, cad, protection) = (
                    item[3], item[4], item[5], item[7], item[8], item[9], item[10], item[14])

                mfg_id = manufacturers_mapping.get(mfg, _id_generator.NIL_UUID.bytes)
                family_id = families_mapping.get(family, _id_generator.NIL_UUID.bytes)
                series_id = series_mapping.get(series, _id_generator.NIL_UUID.bytes)
                material_id = materials_mapping.get(material, _id_generator.NIL_UUID.bytes)
                image_id = images_mapping.get(image, None)
                datasheet_id = datasheets_mapping.get(datasheet, None)
                cad_id = cads_mapping.get(cad, None)
                protection_id = protections_mapping.get(protection, _id_generator.NIL_UUID.bytes)

                item[3] = mfg_id
                item[4] = family_id
                item[5] = series_id
                item[7] = material_id
                item[8] = image_id
                item[9] = datasheet_id
                item[10] = cad_id
                item[14] = protection_id

            con.executemany('INSERT INTO bundle_covers (id, part_number, description, mfg_id, family_id, '
                            'series_id, color_id, material_id, image_id, datasheet_id, cad_id, '
                            'shrink_temp_id, min_temp_id, max_temp_id, protection_id, rigidity, '
                            'shrink_ratio, wall, min_dia, max_dia, adhesive_ids, weight) '
                            'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                            new_data)

        con.commit()

    os.chdir(cwd)


def add_bundle_cover(con, part_number, description, mfg=None, family=None, series=None,
                     color=None, material=None, image=None, datasheet=None, cad=None,
                     shrink_temp=None, min_temp=None, max_temp=None, protection=None,
                     rigidity='', shrink_ratio='', wall='', min_dia=0.0, max_dia=0.0,
                     adhesive_ids=None, weight=0.0, commit=True):
    if adhesive_ids is None:
        adhesive_ids = []

    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    family_id = _families.get_family_id(con, family, mfg_id)
    series_id = _series.get_series_id(con, series, mfg_id)
    color_id = _colors.get_color_id(con, color)
    material_id = _materials.get_material_id(con, material)
    image_id = _images.get_image_id(con, image)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)
    cad_id = _cads.get_cad_id(con, cad)
    shrink_temp_id = _temperatures.get_temperature_id(con, shrink_temp)
    min_temp_id = _temperatures.get_temperature_id(con, min_temp)
    max_temp_id = _temperatures.get_temperature_id(con, max_temp)
    protection_id = _protections.get_protection_id(con, protection)

    adhesive_ids = ', '.join(adhesive_ids)

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO bundle_covers (id, part_number, description, mfg_id, family_id, '
                'series_id, color_id, material_id, image_id, datasheet_id, cad_id, '
                'shrink_temp_id, min_temp_id, max_temp_id, protection_id, rigidity, '
                'shrink_ratio, wall, min_dia, max_dia, adhesive_ids, weight) '
                'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id, material_id,
                 image_id, datasheet_id, cad_id, shrink_temp_id, min_temp_id, max_temp_id,
                 protection_id, rigidity, shrink_ratio, wall, min_dia, max_dia, adhesive_ids,
                 weight))

    _log.debug('bundle cover added %r -> %s', part_number, new_id.hex())

    if commit:
        con.commit()
        return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'bundle_covers',
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
    _con.UUIDField('material_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_materials.table,
                                                    _materials.id_field,
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
    _con.UUIDField('shrink_temp_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_temperatures.table,
                                                    _temperatures.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),

    _con.UUIDField('min_temp_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_temperatures.table,
                                                    _temperatures.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('max_temp_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_temperatures.table,
                                                    _temperatures.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('protection_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_protections.table,
                                                    _protections.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('rigidity', default='""', no_null=True),
    _con.IntField('shrink_ratio', default='""', no_null=True),
    _con.IntField('wall', default='""', no_null=True),
    _con.FloatField('min_dia', default='"0.0"', no_null=True),
    _con.FloatField('max_dia', default='"0.0"', no_null=True),
    _con.IntField('adhesive_ids', default='""', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True)
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_bundles',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('start_point3d_id', no_null=True,
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('stop_point3d_id', no_null=True,
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL'),
    _con.UUIDField('table_point_peg_id', default="NULL"),
    _con.IntField('table_hidden', default='0', no_null=True)
)
