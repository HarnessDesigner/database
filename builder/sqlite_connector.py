"""Minimal standalone SQLite connector for the database builder.

Not a port of harness_designer/database/db_connectors/sqlite_connector/connector.py
(that file is saturated with credential-manager/process-manager/download/dialog
coupling that doesn't apply to a batch build script). This exposes just the
execute/fetch/commit surface the ported create_database/*.py seed-loaders and
sql_table.py actually call, plus the app's own 256-hex-subfolder output-tree
scaffolding, ported verbatim from that connector's connect() method
(lines 233-250 of the original).
"""

import os
import sqlite3


class Connector:

    """Thin wrapper around a single sqlite3 connection."""

    def __init__(self, db_path: str):
        self.db_name = db_path
        self._connection = sqlite3.connect(db_path)
        self._cursor = self._connection.cursor()

    def execute(self, operation: str, params=None):
        if params is None:
            return self._cursor.execute(operation)
        return self._cursor.execute(operation, params)

    def executemany(self, operation: str, seq_params):
        return self._cursor.executemany(operation, seq_params)

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchmany(self, size=None):
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        self._connection.commit()

    def close(self):
        self.commit()
        self._cursor.close()
        self._connection.close()
        self._cursor = None
        self._connection = None

    def get_tables(self) -> list[str]:
        self.execute('SELECT name FROM sqlite_master WHERE type="table";')
        return [row[0] for row in self.fetchall()]

    def get_table_column_names(self, table_name: str) -> list[str]:
        self.execute(f'SELECT "(\'" || group_concat(name, "\', \'") || "\')" from '
                    f'pragma_table_info("{table_name}");')
        return list(eval(self.fetchall()[0][0]))


def scaffold_output_tree(build_dir: str) -> dict[str, str]:
    """Create build_dir and its models/images/cads/datasheets subtrees.

    Each of the four subdirectories gets 256 subfolders named as 2-digit
    zero-padded lowercase hex (00-ff), matching the app's own
    ``<uuid[:2]>`` runtime lookup convention.

    :returns: mapping of {'models': path, 'images': path, 'cads': path, 'datasheets': path}
    """
    os.makedirs(build_dir, exist_ok=True)

    paths = {}
    for sub in ('models', 'images', 'cads', 'datasheets'):
        base = os.path.join(build_dir, sub)
        os.makedirs(base, exist_ok=True)
        for i in range(0x00, 0x100):
            os.makedirs(os.path.join(base, f'{i:02x}'), exist_ok=True)
        paths[sub] = base

    return paths
