# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import seed_json as _seed_json

_log = logging.getLogger('builder.ip_supps')


def add_records(con, data_path):
    """Seed ip_supps from ip_supps.json."""

    _seed_json.seed(con, data_path, 'ip_supps.json', 'ip_supps', ('name', 'description'))


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'ip_supps',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('description', no_null=True)
)
