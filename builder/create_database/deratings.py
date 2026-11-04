# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Schema for the ``deratings`` table.

A manufacturer's derating table for one catalog part (a terminal, a wire or a
splice): how much current the part may carry under given conditions. One row
per row of that part's table, so a part with a four-row table has four rows
here. Static catalog data, not a per-project table.

Exactly one of ``terminal_id`` / ``wire_id`` / ``splice_id`` is set on a row
(the application enforces it when it inserts one), and ``idx`` is the row's
position within its part's table. The conditions and the limit are the
remaining columns, each NULL when the manufacturer's table does not use it:

* ``ambient_temp_c`` -- the ambient temperature the row applies at.
* ``conductor_count`` -- the number of current-carrying conductors bundled
  together; a row with one is a bundling row, not an ambient row.
* ``max_amps`` -- the most current the part may carry under those conditions.
* ``derating_factor`` -- the fraction of the part's own rated current that it
  may carry under those conditions (a row needs ``max_amps`` or
  ``derating_factor``).

This is the same schema as the application's own
``harness_designer/database/create_database/deratings.py``; keep the two
aligned. Nothing seeds the table yet: there is no source data for it, so a
freshly built database has the table and no rows.
"""

import logging

from . import splices as _splices
from . import terminals as _terminals
from . import wires as _wires
from .. import sql_table as _con

_log = logging.getLogger('builder.deratings')


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'deratings',
    id_field,
    _con.UUIDField('terminal_id', default='NULL',
                   references=_con.SQLFieldReference(_terminals.table,
                                                     _terminals.id_field,
                                                     on_delete=_con.REFERENCE_NO_ACTION,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.UUIDField('wire_id', default='NULL',
                   references=_con.SQLFieldReference(_wires.table,
                                                     _wires.id_field,
                                                     on_delete=_con.REFERENCE_NO_ACTION,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.UUIDField('splice_id', default='NULL',
                   references=_con.SQLFieldReference(_splices.table,
                                                     _splices.id_field,
                                                     on_delete=_con.REFERENCE_NO_ACTION,
                                                     on_update=_con.REFERENCE_NO_ACTION)),
    _con.IntField('idx', no_null=True),
    _con.FloatField('ambient_temp_c', default='NULL'),
    _con.IntField('conductor_count', default='NULL'),
    _con.FloatField('max_amps', default='NULL'),
    _con.FloatField('derating_factor', default='NULL')
)


def add_indexes(con):
    """Index the three part columns, so a part's table is found without reading every row.

    SQLite does not index a foreign key's column by itself. The application asks for the same indexes
    (``CREATE INDEX IF NOT EXISTS``) every time it starts, so they are an optimisation here, not a requirement; they
    are built in so a shipped database does not have to build them on first use.
    """
    for column in ('terminal_id', 'wire_id', 'splice_id'):
        con.execute(f'CREATE INDEX IF NOT EXISTS deratings_{column}_index ON deratings ({column});')

    con.commit()

    _log.debug('deratings indexed')
