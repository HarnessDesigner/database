"""Shared bulk-resolve helper for the "rich" seed-loader tables (housings,
covers, cpa_locks, tpa_locks, boots, terminals, bundle_covers, splices,
wire_markers).

Each of those add_records() implementations collects the distinct,
non-None FK-name values for a whole JSON file into a handful of sets (one
per FK column) before touching any per-row insert -- this is the one
function that turns each set into a ``{value: id_bytes}`` mapping via a
handful of chunked, parameterized lookups plus a single executemany for
whatever wasn't already in the table, instead of one round-trip per row
per FK (the dominant cost of the original harness_designer loaders, which
this builder ports from).
"""

from . import id_generator as _id_generator

_CHUNK_SIZE = 500


def insert_data(con, container, table_name, column, mfg_id=None):
    """Resolve every distinct value in ``container`` against
    ``table_name.column`` (optionally scoped by ``mfg_id``), inserting
    whatever doesn't already exist, and return a ``{value: id_bytes}``
    mapping covering every value in ``container``.

    ``container`` must already be deduplicated (a ``set``) -- duplicate
    entries would each get queued for their own INSERT and collide on the
    column's unique constraint.
    """
    container = [item for item in container if item is not None]
    if not container:
        return {}

    # Chunked, parameterized lookup -- avoids both unsafe f-string
    # interpolation (breaks on any value containing a quote, e.g. real
    # description/URL text) and SQLite's per-statement bound variable
    # limit (images/datasheets/cads/model3ds can have as many distinct
    # values as there are rows -- tens of thousands for TE -- a single
    # unchunked IN(...) risks "too many SQL variables").
    existing = {}
    for i in range(0, len(container), _CHUNK_SIZE):
        chunk = container[i:i + _CHUNK_SIZE]
        placeholders = ', '.join('?' for _ in chunk)
        if mfg_id is None:
            con.execute(
                f'SELECT id, {column} FROM {table_name} WHERE {column} IN ({placeholders});',
                chunk)
        else:
            con.execute(
                f'SELECT id, {column} FROM {table_name} WHERE {column} IN ({placeholders}) '
                f'AND mfg_id=?;', chunk + [mfg_id])
        for db_id, db_value in con.fetchall():
            existing[db_value] = db_id

    mapping = dict(existing)
    to_insert = [item for item in container if item not in existing]

    insert_rows = []
    for item in to_insert:
        new_id = _id_generator.generate_global_row_id().bytes
        if mfg_id is None:
            insert_rows.append((new_id, item))
        else:
            insert_rows.append((new_id, item, mfg_id))
        mapping[item] = new_id

    if insert_rows:
        if mfg_id is None:
            con.executemany(f'INSERT INTO {table_name} (id, {column}) VALUES (?, ?);', insert_rows)
        else:
            con.executemany(
                f'INSERT INTO {table_name} (id, {column}, mfg_id) VALUES (?, ?, ?);', insert_rows)
        con.commit()

    return mapping
