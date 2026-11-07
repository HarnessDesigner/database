"""wire_conductors table: one row per individual conductor inside a multi-conductor wire.

The ``wires`` table describes the OUTSIDE of a multi-conductor wire (its jacket colour, overall size, shielding, tpi ...);
this one describes each conductor INSIDE it. Nothing here is unique except the row id: ``wire_id`` is the row id of
the cable in ``wires``, ``idx`` is the conductor's place in the cable, and the rest are the things that can differ from
conductor to conductor. A conductor's ``stripe_color_id`` is the "no color" row (``id_generator.NO_COLOR_UUID``) when it
has no stripe, and a cable's ``wires.color_id`` is that same row when it has no outer jacket.

Seeded from the files in ``Universal/wire_conductors/`` (one per wire model, named like the matching file in
``Universal/wires/``), written by ``scripts/wire_builder.py``. Each file has one entry per CABLE, not per conductor, because the conductors of a cable are usually the same component wire in different colours::

    {"wire": "<the part number of the cable>",
     "common": {core_material, material, wire_size_dia, wire_size_cross, wire_size_awg, strands, od_mm, resistance_1km},
     "conductors": [{"color": "White", "stripe_color": null}, {"color": "Blue", "stripe_color": null}, ...]}

``conductors`` is in order (the position in the list is ``idx``), and an item may name any field of ``common`` to
override it for that conductor, so a cable of unlike conductors is described the same way. Mirrored in the app repo's
``database/create_database/wire_conductors.py``; keep the two aligned.

EVERY CABLE HAS CONDUCTORS (user, 2026-11-05). A cable is a wire with more than one conductor (``num_conductors``) or with
shielding (``shielded``). The files only describe the cables a maker gives per-conductor data for (TE's twisted pairs and
triples). Every other cable gets default rows, made by ``add_records`` from its own ``wires`` row: ``num_conductors`` rows
(one for a shielded single-conductor cable such as coax), each with the cable's size, strands, core material, insulation
material and resistance, the colour WHITE and no stripe. The real colours are set by the user on the placed cable (the
object editor). The shielding is NOT a row here: it is a flag on the app's ``pjt_cable_conductors`` row. ``od_mm`` stays
0.0 for these rows because the cable's outside diameter is not a conductor's.
"""

import json
import logging
import os

from . import colors as _colors
from . import materials as _materials
from . import platings as _platings
from . import wires as _wires
from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.wire_conductors')

_NO_COLOR_DEFAULT = f"X'{_id_generator.NO_COLOR_UUID.hex}'"
_NIL_DEFAULT = "X'00000000000000000000000000000000'"


def add_records(con, data_path, repo_root=None):
    """Expand the wire_conductors files into one row per conductor. Run after the wires are loaded.

    ``data_path`` is the ``Universal`` folder; with ``repo_root`` the ``wire_conductors.json`` of every manufacturer folder
    (``TE/wire_conductors.json``, written by ``scrapers/te/convert.py``) is read as well.
    """
    con.execute('SELECT 1 FROM wire_conductors LIMIT 1;')
    if con.fetchall():
        return

    # one wire_conductors.json, and/or a `wire_conductors` folder with one file per wire model, named like the files in
    # the `wires` folder (M22759-32.json ...)
    json_paths = []

    json_path = os.path.join(data_path, 'wire_conductors.json')
    if os.path.exists(json_path):
        json_paths.append(json_path)

    conductors_dir = os.path.join(data_path, 'wire_conductors')
    if os.path.isdir(conductors_dir):
        json_paths.extend(os.path.join(conductors_dir, file_name) for file_name in sorted(os.listdir(conductors_dir))
                          if file_name.endswith('.json'))

    if repo_root:
        for folder in sorted(os.listdir(repo_root)):
            path = os.path.join(repo_root, folder, 'wire_conductors.json')

            if os.path.isfile(path) and path not in json_paths:
                json_paths.append(path)

    data = []
    for json_path in json_paths:
        _log.info('loading %s', json_path)

        with open(json_path, 'r', encoding='utf-8') as f:
            data.extend(json.loads(f.read()))

    con.execute('SELECT part_number, id FROM wires;')
    wire_ids = {part_number: db_id for part_number, db_id in con.fetchall()}
    no_color = _id_generator.NO_COLOR_UUID.bytes

    rows = []
    for entry in data:
        part_number = entry['wire']
        wire_id = wire_ids[part_number]  # a conductor entry for a wire that does not exist is bad data: raise
        common = entry.get('common', {})

        for idx, conductor in enumerate(entry['conductors']):
            fields = {**common, **conductor}

            rows.append((
                _id_generator.static_row_id('wire_conductors', part_number, idx).bytes, wire_id, idx,
                _colors.get_color_id(con, fields.get('color'), no_color),
                _colors.get_color_id(con, fields.get('stripe_color'), no_color),
                _platings.get_plating_id(con, fields.get('core_material')),
                _materials.get_material_id(con, fields.get('material')),
                fields.get('wire_size_dia'), fields.get('wire_size_cross'), fields.get('wire_size_awg'),
                fields.get('strands', 1), fields.get('od_mm', 0.0), fields.get('resistance_1km', 0.0)))

    described = {entry['wire'] for entry in data}
    described_rows = len(rows)

    # every other cable gets default conductors (see the module docstring)
    white = _colors.get_color_id(con, 'White', no_color)

    con.execute('SELECT id, part_number, num_conductors, core_material_id, material_id, wire_size_dia, wire_size_cross, '
                'wire_size_awg, strands, resistance_1km FROM wires WHERE num_conductors > 1 OR shielded = 1;')

    default_cables = 0
    for (wire_id, part_number, num_conductors, core_material_id, material_id, wire_size_dia, wire_size_cross,
         wire_size_awg, strands, resistance_1km) in con.fetchall():
        if part_number in described:
            continue

        default_cables += 1

        for idx in range(max(1, num_conductors)):
            rows.append((
                _id_generator.static_row_id('wire_conductors', part_number, idx).bytes, wire_id, idx,
                white, no_color, core_material_id, material_id,
                wire_size_dia, wire_size_cross, wire_size_awg, strands, 0.0, resistance_1km))

    _log.info('adding %d conductor(s) of %d described cable(s) and %d default conductor(s) of %d cable(s) to db',
              described_rows, len(data), len(rows) - described_rows, default_cables)

    con.executemany('INSERT INTO wire_conductors (id, wire_id, idx, color_id, stripe_color_id, core_material_id, '
                    'material_id, wire_size_dia, wire_size_cross, wire_size_awg, strands, od_mm, resistance_1km) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', rows)
    con.commit()


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'wire_conductors',
    id_field,
    _con.UUIDField('wire_id', no_null=True,
                   references=_con.SQLFieldReference(_wires.table,
                                                     _wires.id_field,
                                                     on_delete=_con.REFERENCE_NO_ACTION,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.IntField('idx', no_null=True),
    _con.UUIDField('color_id', default=_NO_COLOR_DEFAULT, no_null=True,
                   references=_con.SQLFieldReference(_colors.table,
                                                     _colors.id_field,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.UUIDField('stripe_color_id', default=_NO_COLOR_DEFAULT, no_null=True,
                   references=_con.SQLFieldReference(_colors.table,
                                                     _colors.id_field,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.UUIDField('core_material_id', default=_NIL_DEFAULT, no_null=True,
                   references=_con.SQLFieldReference(_platings.table,
                                                     _platings.id_field,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.UUIDField('material_id', default=_NIL_DEFAULT, no_null=True,
                   references=_con.SQLFieldReference(_materials.table,
                                                     _materials.id_field,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.FloatField('wire_size_dia', default='NULL'),
    _con.FloatField('wire_size_cross', default='NULL'),
    _con.IntField('wire_size_awg', default='NULL'),
    _con.IntField('strands', default='1'),
    _con.FloatField('od_mm', default='"0.0"', no_null=True),
    _con.FloatField('resistance_1km', default='"0.0"', no_null=True),
)


def add_indexes(con):
    """Index ``wire_id`` so a cable's conductors are found without reading every row (SQLite does not index a
    foreign key's column)."""
    con.execute('CREATE INDEX IF NOT EXISTS wire_conductors_wire_id_index ON wire_conductors (wire_id);')
    con.commit()
