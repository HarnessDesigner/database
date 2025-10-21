import os
import sqlite3


class ConfigTable:

    def __init__(self, con, cur, name):
        self._con = con
        self._cur = cur
        self.name = name

    def __contains__(self, item):
        self._cur.execute(f'SELECT id FROM {self.name} WHERE key = "{item}";')
        if self._cur.fetchall():
            return True
        return False

    def __getitem__(self, item):
        self._cur.execute(f'SELECT value FROM {self.name} WHERE key = "{item}";')
        value = self._cur.fetchall()[0][0]
        return eval(value)

    def __setitem__(self, key, value):
        value = str(value)

        if key not in self:
            self._cur.execute(f'INSERT INTO {self.name} (key, value) VALUES(?, ?);', (key, value))
        else:
            self._cur.execute(f'UPDATE {self.name} SET value = "{value}" WHERE key = "{key}";')

        self._con.commit()

    def __delitem__(self, key):
        self._cur.execute(f'DELETE FROM {self.name} WHERE key = "{key}"')
        self._con.commit()


class ConfigDB:

    def __init__(self, app_data):
        config_db_file = os.path.join(app_data, 'config.db')

        self._con = sqlite3.connect(config_db_file)
        self._cur = self._con.cursor()

    def __contains__(self, item):
        self._cur.execute('SELECT name FROM sqlite_master WHERE type="table";')
        tables = [row[0] for row in self._cur.fetchall()]
        return item in tables

    def __getitem__(self, item):
        if item not in self:
            self._cur.execute(f'CREATE TABLE {item}('
                              'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'key TEXT UNIQUE NOT NULL, '
                              'value TEXT NOT NULL'
                              ');')
            self._con.commit()

        return ConfigTable(self._con, self._cur, item)

    def close(self):
        self._cur.close()
        self._con.close()
