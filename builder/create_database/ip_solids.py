# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging
import os

from .. import sql_table as _con
from .. import seed_json as _seed_json

_log = logging.getLogger('builder.ip_solids')

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def add_records(con, data_path):
    """Seed ip_solids from ip_solids.json; its "id": 0 entry ('0' (No Protection)) is the nil UUID default row."""

    _seed_json.seed(con, data_path, 'ip_solids.json', 'ip_solids', ('name', 'short_desc', 'description'))


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'ip_solids',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    _con.TextField('short_desc', no_null=True),
    _con.TextField('description', no_null=True)
)
