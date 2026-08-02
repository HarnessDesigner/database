# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from . import manufacturers as _manufacturers
from . import families as _families
from . import series as _series
from . import colors as _colors
from . import materials as _materials
from . import models3d as _models3d
from . import images as _images
from . import datasheets as _datasheets
from . import cads as _cads

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.accessories')


def add_records(con, _):
    con.execute('SELECT 1 FROM accessories LIMIT 1;')
    if con.fetchall():
        return

    # part_number, description. mfg_id is intentionally omitted here (left
    # to the column's own nil-UUID default): the original seed data pointed
    # at manufacturer rows by old sequential int id (0 = "no manufacturer",
    # 1 = an actual manufacturer resolved only via manufacturers.json, which
    # isn't available to this builder), and there's no way to recover which
    # real manufacturer name that id referred to from this file alone.
    data = (
        ('None', 'No Accessories'),
        ('S1017-1.0X50', '1" x 50\' Polyamide Adhesive, -20 – 60 °C [-4 – 140 °F], Hot Melt Tape'),
        ('S1030', 'Polyolefin Adhesive, -80 – 80 °C [-112 – 176 °F], Hot Melt Tape'),
        ('S1030-TAPE-3/4X33FT', '3/4" x 33\' Polyolefin Adhesive, -80 – 80 °C [-112 – 176 °F], Hot Melt Tape'),
        ('S1048-TAPE-1X100-FT', '1" x 100\' Thermoplastic Adhesive, -55 – 120 °C [-67 – 248 °F], Hot Melt Tape'),
        ('S1048-TAPE-3/4X100-FT', '3/4" x 100\' Thermoplastic Adhesive, -55 – 120 °C [-67 – 248 °F], Hot Melt Tape'),
        ('S1125-KIT-1', 'Dual Pack, 5 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives'),
        ('S1125-KIT-4', 'Dual Pack, 5 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives'),
        ('S1125-KIT-5', 'Dual Pack, 1 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives'),
        ('S1125-KIT-8', 'Dual Pack, 1 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives'),
        ('S1125-APPLICATOR', 'Epoxy Adhesives Dispensing Gun')
    )

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO accessories (id, part_number, description) VALUES(?, ?, ?);', rows)
    con.commit()


def add_accessory(con, part_number, mfg, description=None, series=None,
                  family=None, color=None, material=None, image=None,
                  datasheet=None, cad=None, model3d=None, length=0.0,
                  width=0.0, height=0.0, weight=0.0, commit=True):
    """Add an accessory row, generating a new id."""
    if color is None:
        color = 'Dark Gray'

    mfg, family, series = _manufacturers.inspect_mfg_fam_series(mfg, family, series)

    mfg_id = _manufacturers.get_mfg_id(con, mfg)
    series_id = _series.get_series_id(con, series, mfg_id)
    family_id = _families.get_family_id(con, family, mfg_id)
    color_id = _colors.get_color_id(con, color)
    material_id = _materials.get_material_id(con, material)
    image_id = _images.get_image_id(con, image)
    cad_id = _cads.get_cad_id(con, cad)
    datasheet_id = _datasheets.get_datasheet_id(con, datasheet)
    model3d_id = _models3d.get_model3d_id(con, model3d)

    if not description:
        description = mfg
        if series:
            description += f' {series}'

        if family:
            description += f' {family}'

        if material:
            description += f' {material}'

        if color:
            description += f' {color}'

        description += ' Accessory'

    new_id = _id_generator.generate_global_row_id().bytes

    _log.debug('adding accessory %s, %s', part_number, description)
    con.execute('INSERT INTO accessories (id, part_number, description, mfg_id, '
                'family_id, series_id, color_id, material_id, image_id, '
                'datasheet_id, cad_id, model3d_id, length, width, height, weight) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, part_number, description, mfg_id, family_id, series_id, color_id,
                 material_id, image_id, datasheet_id, cad_id, model3d_id, length,
                 width, height, weight))

    _log.debug('accessory added %r', part_number)

    if commit:
        con.commit()
        return new_id


id_field = _con.UUIDField('id', is_primary=True)


table = _con.SQLTable(
    'accessories',
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
    _con.UUIDField('model3d_id', default='NULL',
                  references=_con.SQLFieldReference(_models3d.table,
                                                    _models3d.id_field,
                                                    on_update=_con.REFERENCE_CASCADE)),


    _con.FloatField('length', default='"0.0"', no_null=True),
    _con.FloatField('width', default='"0.0"', no_null=True),
    _con.FloatField('height', default='"0.0"', no_null=True),
    _con.FloatField('weight', default='"0.0"', no_null=True)
)
