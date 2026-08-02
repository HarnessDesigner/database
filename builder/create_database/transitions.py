"""transitions table -- ported from harness_designer/database/create_database/transitions.py.

Universal/transitions.json only (no per-manufacturer transitions.json exists
in this repo) -- the original code already unconditionally nulls image/cad/
datasheet for every transition row (not manufacturer-specific), kept as-is.
"""

import logging
import os
import json

from . import manufacturers as _manufacturers
from . import series as _series
from . import families as _families
from . import temperatures as _temperatures
from . import colors as _colors
from . import materials as _materials
from . import shapes as _shapes
from . import protections as _protections
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads
from . import transition_branches as _transition_branches

from . import projects as _projects
from . import points3d as _points3d
from . import points_peg as _points_peg

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.transitions')


def add_transition(con, part_number, description, mfg=None, family=None, series=None,
                   color=None, image=None, datasheet=None, cad=None, min_temp=None,
                   max_temp=None, material=None, shape=None, protection=None,
                   branch_count=0, adhesive_ids=None, weight=0.0, branches=None,
                   commit=True):
    if adhesive_ids is None:
        adhesive_ids = []
    if branches is None:
        branches = []

    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    series_id = _series.get_series_id(con, series, mfg_id)
    family_id = _families.get_family_id(con, family, mfg_id)
    color_id = _colors.get_color_id(con, color)
    material_id = _materials.get_material_id(con, material)
    shape_id = _shapes.get_shape_id(con, shape)
    min_temp_id = _temperatures.get_temperature_id(con, min_temp)
    max_temp_id = _temperatures.get_temperature_id(con, max_temp)
    protection_id = _protections.get_protection_id(con, protection)
    image_id = _images.get_image_id(con, image)
    cad_id = _cads.get_cad_id(con, cad)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO transitions (id, part_number, description, mfg_id, '
                'family_id, series_id, color_id, image_id, datasheet_id, cad_id, '
                'min_temp_id, max_temp_id, material_id, shape_id, protection_id, '
                'branch_count, adhesive_ids, weight) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id,
                 image_id, datasheet_id, cad_id, min_temp_id, max_temp_id, material_id,
                 shape_id, protection_id, branch_count,
                 str(adhesive_ids), weight))

    con.commit()
    _log.debug('transition added %r -> %s', part_number, new_id.hex())

    for i, branch in enumerate(branches):
        try:
            _transition_branches.add_transition_branch(con, i, new_id, commit=commit, **branch)
        except Exception:
            _log.exception('failed to add transition branch %d for %r', i, part_number)

    if commit:
        return new_id


def add_transitions(con, data: tuple[dict] | list[dict]):
    for line in data:
        add_transition(con, **line)


def add_records(con, data_path):
    con.execute('SELECT 1 FROM transitions LIMIT 1;')
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

        json_path = os.path.join(path, 'transitions.json')

        if os.path.exists(json_path):
            _log.info('loading %s', json_path)

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            data_len = len(data)
            _log.info('adding %d %stransition(s) to db', data_len, name)

            for item in data:
                item.pop('id', None)

                item['protection'] = '\n'.join(item['protection'])

                item['image'] = None
                item['datasheet'] = None
                item['cad'] = None

                try:
                    add_transition(con, commit=False, **item)
                except Exception:
                    _log.exception('failed to add transition %r', item.get('part_number'))

            con.commit()

    os.chdir(cwd)


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'transitions',
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
    _con.UUIDField('material_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_materials.table,
                                                    _materials.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('shape_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_shapes.table,
                                                    _shapes.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('protection_id', default="X'00000000000000000000000000000000'", no_null=True,
                  references=_con.SQLFieldReference(_protections.table,
                                                    _protections.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('branch_count', default='0', no_null=True),
    _con.TextField('adhesive_ids', default='"[]"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True)
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_transitions',
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
    _con.UUIDField('point_peg_id', default="NULL",
                  references=_con.SQLFieldReference(_points_peg.pjt_table,
                                                    _points_peg.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.TextField('name', default='""', no_null=True),
    _con.TextField('notes', default='""', no_null=True),
    _con.TextField('quat3d', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('angle3d', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('quatpeg', default='"[1.0, 0.0, 0.0, 0.0]"', no_null=True),
    _con.TextField('anglepeg', default='"[0.0, 0.0, 0.0]"', no_null=True),
    _con.IntField('is_visible3d', default='1', no_null=True),
    _con.IntField('smooth', default='NULL')
)
