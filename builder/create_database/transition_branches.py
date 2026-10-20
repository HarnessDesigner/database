# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from . import transitions as _transitions

from . import projects as _projects
from . import points3d as _points3d
from . import points_peg as _points_peg

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.transition_branches')


def add_transition_branch(con, idx, transition_id, bulb_offset=None, bulb_length=None,
                          min_dia=0.0, max_dia=0.0, length=0.0, offset=None, angle=None,
                          flange_height=None, flange_width=None, commit=True):
    """Add a transition branch row, generating a new id.

    `offset` and `angle` are 3-axis: a ``[x, y, z]`` list (offset in mm,
    angle in euler degrees about X, Y, Z -- see TRANSITION_DESIGN.md in the
    harness_designer app repo for the composition order and why euler,
    not quaternions, is the permanent on-disk form). Both columns are
    NOT NULL in the schema, so ``None`` here is stored as the neutral
    ``[0.0, 0.0, 0.0]`` rather than left unset. `bulb_offset` stays
    nullable/optional -- ``None`` means "no bulb offset", not "at the
    origin", so it is only ever stringified when actually given.
    """
    if offset is None:
        offset = [0.0, 0.0, 0.0]
    offset = str([float(v) for v in offset])

    if angle is None:
        angle = [0.0, 0.0, 0.0]
    angle = str([float(v) for v in angle])

    if bulb_offset is not None:
        bulb_offset = str([float(v) for v in bulb_offset])

    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO transition_branches (id, transition_id, idx, bulb_offset, '
                'bulb_length, min_dia, max_dia, length, offset, angle, flange_height, '
                'flange_width) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (new_id, transition_id, idx, bulb_offset, bulb_length, min_dia, max_dia,
                 length, offset, angle, flange_height, flange_width))

    _log.debug('transition branch added %s - %s', idx, transition_id)

    if commit:
        con.commit()
        return new_id


def add_pjt_transition_branch(con, project_id, part_id, transition_id,
                              point3d_id=None, diameter=0.0, branch_id=0):
    """Add a pjt_transition_branches row, generating a new id."""
    new_id = _id_generator.generate_global_row_id().bytes

    con.execute('INSERT INTO pjt_transition_branches (id, project_id, part_id, transition_id, '
                'point3d_id, diameter, branch_id) VALUES (?, ?, ?, ?, ?, ?, ?);',
                (new_id, project_id, part_id, transition_id, point3d_id, diameter, branch_id))

    con.commit()

    return new_id


id_field = _con.UUIDField('id', is_primary=True)


table = _con.SQLTable(
    'transition_branches',
    id_field,
    _con.UUIDField('transition_id', no_null=True,
                  references=_con.SQLFieldReference(_transitions.table,
                                                    _transitions.id_field,
                                                    on_delete=_con.REFERENCE_NO_ACTION,
                                                    on_update=_con.REFERENCE_NO_ACTION)),
    _con.IntField('idx', no_null=True),
    _con.TextField('bulb_offset', default='NULL'),
    _con.FloatField('bulb_length', default='NULL'),
    _con.FloatField('min_dia', no_null=True),
    _con.FloatField('max_dia', no_null=True),
    _con.FloatField('length', no_null=True),
    # 3-axis text columns ("[x, y, z]"), NOT NULL -- offset/angle are always
    # a concrete point/euler-triple now, never "unset" (that distinction
    # used to be carried by NULL under the old 1-axis angle/2-axis offset
    # scheme; see add_transition_branch's docstring).
    _con.TextField('offset', default="'[0.0, 0.0, 0.0]'", no_null=True),
    _con.TextField('angle', default="'[0.0, 0.0, 0.0]'", no_null=True),
    _con.FloatField('flange_height', default='NULL'),
    _con.FloatField('flange_width', default='NULL')
)


pjt_id_field = _con.UUIDField('id', is_primary=True)

pjt_table = _con.SQLTable(
    'pjt_transition_branches',
    pjt_id_field,
    _con.ProjectIdField(),
    _con.UUIDField('part_id', no_null=True,
                  references=_con.SQLFieldReference(table,
                                                    id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('transition_id', no_null=True,
                  references=_con.SQLFieldReference(_transitions.pjt_table,
                                                    _transitions.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.UUIDField('point3d_id', no_null=True,
                  references=_con.SQLFieldReference(_points3d.pjt_table,
                                                    _points3d.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.FloatField('diameter', no_null=True),
    _con.IntField('branch_id', no_null=True),
    _con.UUIDField('table_point_peg_id', default="NULL",
                  references=_con.SQLFieldReference(_points_peg.pjt_table,
                                                    _points_peg.pjt_id_field,
                                                    on_delete=_con.REFERENCE_CASCADE,
                                                    on_update=_con.REFERENCE_CASCADE)),
    _con.IntField('table_hidden', default='0', no_null=True)
)
