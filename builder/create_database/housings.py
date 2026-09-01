"""housings table -- ported from harness_designer/database/create_database/housings.py.

add_records is fully generic (walks every immediate subdirectory of
data_path looking for housings.json -- feeding it the repo root picks up
Aptiv/Bosch/TE's housings.json in one call). The only manufacturer-specific
step is a single call into builder.bosch_models for Bosch rows (nulls
cad/datasheet, converts a matching local .stp to a real model3d row) -- see
that module for why. Every other manufacturer flows through add_housing()
completely unmodified from the original.
"""

import logging
import os
import json

from . import manufacturers as _manufacturers
from . import series as _series
from . import families as _families
from . import colors as _colors
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads
from . import models3d as _models3d
from . import directions as _directions
from . import temperatures as _temperatures
from . import cavity_locks as _cavity_locks
from . import genders as _genders
from . import ip_ratings as _ip_ratings
from . import cpa_lock_types as _cpa_lock_types
from . import seal_types as _seal_types

from . import projects as _projects
from . import points3d as _points3d
from . import points2d as _points2d
from . import points_peg as _points_peg

from .. import sql_table as _con
from .. import id_generator as _id_generator
from .. import bosch_models as _bosch_models
from ..bulk_insert import insert_data as _insert_data

_log = logging.getLogger('builder.housings')


def add_records(con, data_path):
    con.execute('SELECT 1 FROM housings LIMIT 1;')
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

        json_path = os.path.join(path, 'housings.json')

        if os.path.exists(json_path):
            manufacturers = set()
            families = set()
            series_set = set()
            cpa_lock_types = set()
            seal_types = set()

            images = set()
            datasheets = set()
            cads = set()
            model3ds = set()
            cavity_locks = set()
            directions = set()

            _log.info('loading %s', json_path)

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            if isinstance(data, dict):
                data = [value for value in data.values()]

            data_len = len(data)
            _log.info('adding %d %shousing(s) to db', data_len, name)

            new_data = []

            for item in data:
                item.pop('id', None)

                if 'shared_cad' in item:
                    del item['shared_cad']
                if 'shared_model3d' in item:
                    del item['shared_model3d']

                _bosch_models.maybe_handle_bosch_row(con, item, name, path)

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
                direction = item.get('direction', None)
                gender = item.get('gender', None)
                cavity_lock = item.get('cavity_lock', None)
                ip_rating = item.get('ip_rating', 'IP00')
                seal_type = item.get('seal_type', None)
                cpa_lock_type = item.get('cpa_lock_type', None)
                sealing = item.get('sealing', 0)
                rows = item.get('rows', 0)
                num_pins = item.get('num_pins', 0)
                terminal_sizes = item.get('terminal_sizes', None)
                terminal_size_counts = item.get('terminal_size_counts', None)
                centerline = item.get('centerline', 0.0)
                compat_cpas = item.get('compat_cpas', None)
                compat_tpas = item.get('compat_tpas', None)
                compat_covers = item.get('compat_covers', None)
                compat_terminals = item.get('compat_terminals', None)
                compat_seals = item.get('compat_seals', None)
                compat_housings = item.get('compat_housings', None)
                compat_boots = item.get('compat_boots', None)
                length = item.get('length', 0.0)
                width = item.get('width', 0.0)
                height = item.get('height', 0.0)
                weight = item.get('weight', 0.0)
                cover_point3d = item.get('cover_point3d', None)
                seal_point3d = item.get('seal_point3d', None)
                boot_point3d = item.get('boot_point3d', None)
                tpa_lock_1_point3d = item.get('tpa_lock_1_point3d', None)
                tpa_lock_2_point3d = item.get('tpa_lock_2_point3d', None)
                cpa_lock_point3d = item.get('cpa_lock_point3d', None)

                mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

                manufacturers.add(mfg)
                families.add(family)
                series_set.add(series)
                images.add(image)
                datasheets.add(datasheet)
                cads.add(cad)
                model3ds.add(model3d)
                directions.add(direction)
                cavity_locks.add(cavity_lock)
                seal_types.add(seal_type)
                cpa_lock_types.add(cpa_lock_type)

                if terminal_size_counts is None:
                    terminal_size_counts = []
                if terminal_sizes is None:
                    terminal_sizes = []
                if compat_cpas is None:
                    compat_cpas = []
                if compat_tpas is None:
                    compat_tpas = []
                if compat_covers is None:
                    compat_covers = []
                if compat_terminals is None:
                    compat_terminals = []
                if compat_seals is None:
                    compat_seals = []
                if compat_housings is None:
                    compat_housings = []
                if compat_boots is None:
                    compat_boots = []
                if cover_point3d is None:
                    cover_point3d = [0.0, 0.0, 0.0]
                if seal_point3d is None:
                    seal_point3d = [0.0, 0.0, 0.0]
                if boot_point3d is None:
                    boot_point3d = [0.0, 0.0, 0.0]
                if tpa_lock_1_point3d is None:
                    tpa_lock_1_point3d = [0.0, 0.0, 0.0]
                if tpa_lock_2_point3d is None:
                    tpa_lock_2_point3d = [0.0, 0.0, 0.0]
                if cpa_lock_point3d is None:
                    cpa_lock_point3d = [0.0, 0.0, 0.0]

                color_id = _colors.get_color_id(con, color)

                min_temp_id = _temperatures.get_temperature_id(con, min_temp)
                max_temp_id = _temperatures.get_temperature_id(con, max_temp)
                gender_id = _genders.get_gender_id(con, gender)
                ip_rating_id = _ip_ratings.get_ip_rating_id(con, ip_rating)

                if not description:
                    description = mfg
                    if family:
                        description += f' {family}'
                    if series:
                        description += f' {series}'
                    if num_pins:
                        description += f' {num_pins} cavity'
                    if gender:
                        description += f' {gender}'
                    if terminal_sizes:
                        for t_size in terminal_sizes:
                            description += f' {t_size}mm'
                    description += ' Housing'

                compat_cpas = ', '.join(compat_cpas)
                compat_tpas = ', '.join(compat_tpas)
                compat_covers = ', '.join(compat_covers)
                compat_terminals = ', '.join(compat_terminals)
                compat_seals = ', '.join(compat_seals)
                compat_housings = ', '.join(compat_housings)
                compat_boots = ', '.join(compat_boots)

                new_id = _id_generator.generate_global_row_id().bytes

                row = [new_id, part_number, description,
                       mfg, family, series, image, datasheet, cad, model3d, direction,
                       seal_type, cpa_lock_type, cavity_lock,
                       color_id, min_temp_id, max_temp_id, gender_id, ip_rating_id,
                       sealing, rows, num_pins, str(terminal_sizes), str(terminal_size_counts),
                       centerline, compat_cpas, compat_tpas, compat_covers, compat_terminals,
                       compat_seals, compat_housings, compat_boots, length, width, height,
                       weight, str(cover_point3d), str(seal_point3d), str(boot_point3d),
                       str(tpa_lock_1_point3d), str(tpa_lock_2_point3d), str(cpa_lock_point3d)]

                new_data.append(row)

            if not new_data:
                continue

            manufacturers_mapping = _insert_data(con, manufacturers, 'manufacturers', 'name')
            images_mapping = _insert_data(con, images, 'images', 'path')
            datasheets_mapping = _insert_data(con, datasheets, 'datasheets', 'path')
            cads_mapping = _insert_data(con, cads, 'cads', 'path')
            model3ds_mapping = _insert_data(con, model3ds, 'models3d', 'path')
            directions_mapping = _insert_data(con, directions, 'directions', 'name')
            cavity_locks_mapping = _insert_data(con, cavity_locks, 'cavity_locks', 'name')
            seal_types_mapping = _insert_data(con, seal_types, 'seal_types', 'name')
            cpa_lock_types_mapping = _insert_data(con, cpa_lock_types, 'cpa_lock_types', 'name')

            mfg_id = manufacturers_mapping[list(manufacturers_mapping.keys())[0]]
            families_mapping = _insert_data(con, families, 'families', 'name', mfg_id=mfg_id)
            series_mapping = _insert_data(con, series_set, 'series', 'name', mfg_id=mfg_id)

            for item in new_data:

                (mfg, family, series, image, datasheet, cad, model3d, direction,
                 seal_type, cpa_lock_type, cavity_lock) = item[3:14]

                mfg_id = manufacturers_mapping.get(mfg, _id_generator.NIL_UUID.bytes)
                image_id = images_mapping.get(image, None)
                datasheet_id = datasheets_mapping.get(datasheet, None)
                cad_id = cads_mapping.get(cad, None)
                model3d_id = model3ds_mapping.get(model3d, None)
                directions_id = directions_mapping.get(direction, _id_generator.NIL_UUID.bytes)
                cavity_lock_id = cavity_locks_mapping.get(cavity_lock, _id_generator.NIL_UUID.bytes)
                # No sentinel fallback -- a housing's own seal type is
                # genuinely optional (unlike this row's other lookup
                # FKs), so an unset/unrecognized seal_type here means a
                # real SQL NULL, not a dangling reference to a
                # placeholder row (seal_types no longer has one).
                seal_type_id = seal_types_mapping.get(seal_type, None)
                cpa_lock_type_id = cpa_lock_types_mapping.get(cpa_lock_type, _id_generator.NIL_UUID.bytes)
                family_id = families_mapping.get(family, _id_generator.NIL_UUID.bytes)
                series_id = series_mapping.get(series, _id_generator.NIL_UUID.bytes)

                item[3:14] = [mfg_id, family_id, series_id, image_id, datasheet_id, cad_id, model3d_id,
                              directions_id, seal_type_id, cpa_lock_type_id, cavity_lock_id]

            con.executemany('INSERT INTO housings (id, part_number, description, ' 
                            'mfg_id, family_id, series_id, image_id, datasheet_id, cad_id, ' 
                            'model3d_id, direction_id, seal_type_id, cpa_lock_type_id, cavity_lock_id, '
                            'color_id, min_temp_id, max_temp_id,  gender_id, ip_rating_id, '
                            'sealing, rows, num_pins, terminal_sizes, terminal_size_counts, ' 
                            'centerline, compat_cpas, compat_tpas, compat_covers, compat_terminals, ' 
                            'compat_seals, compat_housings, compat_boots, length, width, height, ' 
                            'weight, cover_point3d, seal_point3d, boot_point3d, ' 
                            'tpa_lock_1_point3d, tpa_lock_2_point3d, cpa_lock_point3d) '
                            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
                            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                            new_data)

            con.commit()

    os.chdir(cwd)


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'housings',
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
    _con.UUIDField('gender_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_genders.table,
                                                    _genders.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('direction_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_directions.table,
                                                    _directions.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cavity_lock_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_cavity_locks.table,
                                                    _cavity_locks.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('ip_rating_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_ip_ratings.table,
                                                    _ip_ratings.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    # Genuinely nullable (SQL NULL, no nil-UUID sentinel default) --
    # unlike this table's other lookup FKs, a housing legitimately may
    # have no seal type at all, and seal_types no longer carries a
    # placeholder "None"/"Unknown" row for a sentinel to point at (see
    # create_database.seal_types.get_seal_type_id's own docstring).
    _con.UUIDField('seal_type_id',
                  references=_con.SQLFieldReference(_seal_types.table,
                                                    _seal_types.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cpa_lock_type_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_cpa_lock_types.table,
                                                    _cpa_lock_types.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('sealing', default='0', no_null=True),
    _con.IntField('rows', default='0', no_null=True),
    _con.IntField('num_pins', default='0', no_null=True),
    _con.TextField('terminal_sizes', default='""', no_null=True),
    _con.TextField('terminal_size_counts', default='""', no_null=True),
    _con.FloatField('centerline', default='"0.0"', no_null=True),
    _con.TextField('compat_cpas', default='""', no_null=True),
    _con.TextField('compat_tpas', default='""', no_null=True),
    _con.TextField('compat_covers', default='""', no_null=True),
    _con.TextField('compat_terminals', default='""', no_null=True),
    _con.TextField('compat_seals', default='""', no_null=True),
    _con.TextField('compat_housings', default='""', no_null=True),
    _con.TextField('compat_boots', default='""', no_null=True),
    _con.FloatField('length', default='"0.0"', no_null=True),
    _con.FloatField('width', default='"0.0"', no_null=True),
    _con.FloatField('height', default='"0.0"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True),
    _con.TextField('cover_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('seal_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('boot_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('tpa_lock_1_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('tpa_lock_2_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('cpa_lock_point3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('quat3d', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('angle3d', default='"[0.0, 0.0, 0.0]"', no_null=True)
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_housings',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cover_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('seal_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('boot_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('tpa_lock_1_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('tpa_lock_2_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('cpa_lock_point3d_id', default="NULL",
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point3d_id', no_null=True,
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point2d_id', no_null=True,
                  references=_con.SQLFieldReference(_points2d.pjt_table,
                                                    _points2d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point_peg_id', default="NULL",
                  references=_con.SQLFieldReference(_points_peg.pjt_table,
                                                    _points_peg.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('table_point_peg_id', default="NULL",
                  references=_con.SQLFieldReference(_points_peg.pjt_table,
                                                    _points_peg.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('table_hidden', default='0', no_null=True),
    _con.TextField('quatpeg', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('anglepeg', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.UUIDField('scale3d_id', default='NULL',
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_DEFAULT,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.TextField('quat2d', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('angle2d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('quat3d', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('angle3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.IntField('is_visible2d', default='1', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL')
)
