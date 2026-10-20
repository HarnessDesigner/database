"""Seed a lookup table from a JSON file in Universal/.

A file is a list of entries, "id" first, like colors.json. The entry with "id": 0 is the table's default row
("No Family", "No Series", "Unknown", IP00 ...) and is stored with the nil UUID -- the value an unassigned foreign
key defaults to -- so every foreign key in the database points at a row that exists. Every other entry gets a
generated id; the "id" in the file is only a label and is never stored.
"""

import json
import os

from . import id_generator as _id_generator


def load_entries(data_path, file_name):
    """The entries of ``data_path/file_name`` (a list, or a dict whose values are the entries)."""
    with open(os.path.join(data_path, file_name), 'r', encoding='utf-8') as f:
        entries = json.loads(f.read())

    if isinstance(entries, dict):
        entries = list(entries.values())

    zeros = [entry for entry in entries if entry.get('id') == 0]
    if len(zeros) > 1:
        raise ValueError(f'{file_name}: more than one entry has "id": 0 -- only the default row may')

    return entries


def row_id(entry):
    """The nil UUID for the default ("id": 0) entry, a generated id for every other one."""
    if entry.get('id') == 0:
        return _id_generator.NIL_UUID.bytes

    return _id_generator.generate_global_row_id().bytes


def seed(con, data_path, file_name, table_name, columns, constants=None):
    """Insert every entry of ``file_name`` into ``table_name``.

    ``columns`` are the entry keys that are also column names; ``constants`` maps extra column names to a value
    every row gets. Does nothing if the table already has rows.
    """
    con.execute(f'SELECT 1 FROM {table_name} LIMIT 1;')
    if con.fetchall():
        return

    constants = constants or {}
    names = list(columns) + list(constants)
    values = list(constants.values())

    rows = []
    for entry in load_entries(data_path, file_name):
        rows.append((row_id(entry), *[entry[column] for column in columns], *values))

    placeholders = ', '.join('?' for _ in range(len(names) + 1))
    con.executemany(f'INSERT INTO {table_name} (id, {", ".join(names)}) VALUES ({placeholders});', rows)
    con.commit()
