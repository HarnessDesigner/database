# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.ip_supps')


def add_records(con, _=None):
    con.execute('SELECT 1 FROM ip_supps LIMIT 1;')
    if con.fetchall():
        return

    data = (
        ('D', 'Wire'),
        ('G', 'Oil resistant'),
        ('F', 'Oil resistant'),
        ('H', 'High voltage apparatus'),
        ('M', 'Motion during water test'),
        ('S', 'Stationary during water test'),
        ('W', 'Weather conditions')
    )

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO ip_supps (id, name, description) VALUES (?, ?, ?);', rows)
    con.commit()


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'ip_supps',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('description', no_null=True)
)
