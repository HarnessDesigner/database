# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging
import os

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.ip_solids')

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def add_records(con, _=None):
    con.execute('SELECT 1 FROM ip_solids LIMIT 1;')
    if con.fetchall():
        return

    data = (
        ('0', 'No Protection',
         'No protection against contact and ingress of objects.'),

        ('1', '>= 50.00mm sized objects',
         '>= 50.00mm sized objects\n'
         'Any large surface of the body, such as the back\n'
         'of a hand, but no protection against deliberate\n'
         'contact with a body part.'),

        ('2', '>= 12.50mm sized objects',
         '>= 12.50mm sized objects\n'
         'Fingers or similar objects.'),

        ('3', '>= 2.50mm sized objects',
         '>= 2.50mm sized objects\n'
         'Tools, thick wires, etc.'),

        ('4', '>= 1.00mm sized objects',
         '>= 1.00mm sized objects\n'
         'Most wires, slender screws, large ants, etc.'),

        ('5', 'Dust Protected',
         'Dust Protected\n'
         'Ingress of dust is not entirely prevented.'),

        ('6', 'Dust Tight',
         'Dust Tight\n'
         'No ingress of dust.'),

        ('X', 'Unknown',
         'No data is available to specify a protection\n'
         'rating about this criterion.')
    )

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO ip_solids (id, name, short_desc, description) VALUES (?, ?, ?, ?);', rows)

    con.commit()


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'ip_solids',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('short_desc', no_null=True),
    _con.TextField('description', no_null=True)
)
