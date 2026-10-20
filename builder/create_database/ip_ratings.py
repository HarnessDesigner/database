# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import seed_json as _seed_json
from .. import id_generator as _id_generator

from . import ip_supps as _ip_supps
from . import ip_fluids as _ip_fluids
from . import ip_solids as _ip_solids

_log = logging.getLogger('builder.ip_ratings')

# ip_solids.py/ip_fluids.py used to be seeded with sequential int ids and this
# file's own seed data referenced solid/fluid rows positionally by those fake
# ints (solid_id/fluid_id columns). Both tables now generate real UUID ids,
# so those old positional ints no longer name anything -- these tuples record
# the *name* each old positional index used to point at (matching the order
# ip_solids.py/ip_fluids.py seed their own rows in), so the real id can be
# resolved by a lookup instead of replayed as a fake int.


def add_records(con, data_path):
    """Seed every IP rating from ip_ratings.json. The "id": 0 entry, IP00 (solid 0, fluid 0), is the nil UUID row.

    Each entry names its solid and fluid code, so ip_solids and ip_fluids must be seeded first.
    """
    con.execute('SELECT 1 FROM ip_ratings LIMIT 1;')
    if con.fetchall():
        return

    solid_ids = _ids_by_name(con, 'ip_solids')
    fluid_ids = _ids_by_name(con, 'ip_fluids')

    rows = []
    for entry in _seed_json.load_entries(data_path, 'ip_ratings.json'):
        try:
            solid_id = solid_ids[entry['solid']]
            fluid_id = fluid_ids[entry['fluid']]
        except KeyError as error:
            raise RuntimeError(f'ip_ratings.json: {entry["name"]!r} uses {error}, which is not in ip_solids / '
                               f'ip_fluids -- seed those before ip_ratings') from None

        rows.append((_seed_json.row_id(entry), entry['name'], solid_id, fluid_id))

    con.executemany('INSERT INTO ip_ratings (id, name, solid_id, fluid_id) VALUES (?, ?, ?, ?);', rows)
    con.commit()


def _ids_by_name(con, table_name):
    con.execute(f'SELECT name, id FROM {table_name};')
    return {name: row_id for name, row_id in con.fetchall()}


ip_rating_cache = {}


def get_ip_rating_id(con, ip_rating):  # NOQA
    """Return the ip rating id for ``ip_rating``."""
    if ip_rating is None:
        return _id_generator.NIL_UUID.bytes

    ip_rating = ip_rating.upper().replace('-', '').replace(' ', '')

    try:
        return ip_rating_cache[ip_rating]
    except KeyError:
        pass

    con.execute('SELECT id FROM ip_ratings WHERE name=?;', (ip_rating,))
    rows = con.fetchall()
    if rows:
        ip_rating_cache[ip_rating] = rows[0][0]
        return rows[0][0]

    return _id_generator.NIL_UUID.bytes


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'ip_ratings',
    id_field,
    _con.TextField('name', is_unique=True, no_null=True),
    # No schema-level default: previously defaulted to the seeded "Unknown"
    # row (id 7/12 under the old sequential scheme), but a fixed integer
    # can't name a dynamically-generated UUID. Callers that relied on the
    # implicit default now need to resolve the Unknown row's real id
    # explicitly before inserting.
    _con.UUIDField('solid_id', no_null=True,
                  references=_con.SQLFieldReference(_ip_solids.table, _ip_solids.id_field)),
    _con.UUIDField('fluid_id', no_null=True,
                  references=_con.SQLFieldReference(_ip_fluids.table, _ip_fluids.id_field)),
    _con.UUIDField('supp_id', default='NULL',
                  references=_con.SQLFieldReference(_ip_supps.table, _ip_supps.id_field))
)
