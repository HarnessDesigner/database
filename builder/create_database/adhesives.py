# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

import logging

from .. import sql_table as _con
from .. import id_generator as _id_generator

_log = logging.getLogger('builder.adhesives')


def add_records(con, _):
    con.execute('SELECT 1 FROM adhesives LIMIT 1;')
    if con.fetchall():
        return

    data = (
        ('None', 'No Adhesive', ''),
        ('225', 'Precoated latent-curing epoxy/polyamide', ''),
        ('42', 'Hot-melt/polyamide (Thermoplastic)', ''),
        ('86', 'Hot-melt,high performance (Thermoplastic)', ''),
        ('S1006', 'Epoxy/polyamide two-part paste (Thermoset)', ''),
        ('S1017', 'Hot-melt/polyamide (Thermoplastic)', 'S1017-1.0X50'),
        ('S1030', 'Hot-melt/polyolefin (Thermoplastic)', 'S1030, S1030-TAPE-3/4X33FT'),
        ('S1048', 'Hot-melt,high performance (Thermoplastic)', 'S1048-TAPE-1X100-FT, S1048-TAPE-3/4X100-FT'),
        ('S1125', 'Epoxy/polyamide two-part paste (Thermoset)', 'S1125-KIT-1, S1125-KIT-4, S1125-KIT-5, S1125-KIT-8, S1125-APPLICATOR')
    )

    rows = [(_id_generator.generate_global_row_id().bytes, *row) for row in data]

    con.executemany('INSERT INTO adhesives (id, code, description, accessory_part_nums) VALUES (?, ?, ?, ?);', rows)

    con.commit()


adhesive_cache = {}


def get_adhesive_id(con, code):
    """Return the adhesive id for ``code``, auto-vivifying if missing."""
    if not code:
        return _id_generator.NIL_UUID.bytes

    try:
        return adhesive_cache[code]
    except KeyError:
        pass

    con.execute('SELECT id FROM adhesives WHERE code=?;', (code,))
    res = con.fetchall()

    if res:
        adhesive_cache[code] = res[0][0]
        return res[0][0]

    new_id = _id_generator.generate_global_row_id().bytes
    con.execute('INSERT INTO adhesives (id, code) VALUES (?, ?);', (new_id, code))

    _log.debug('adhesive added %r -> %s', code, new_id.hex())

    adhesive_cache[code] = new_id
    return new_id


id_field = _con.UUIDField('id', is_primary=True)

table = _con.SQLTable(
    'adhesives',
    id_field,
    _con.TextField('code', is_unique=True, no_null=True),
    _con.TextField('description', default='""', no_null=True),
    _con.TextField('accessory_part_nums', default='""', no_null=True)
)
