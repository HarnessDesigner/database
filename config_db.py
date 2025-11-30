import os
import sqlite3


class ConfigTable:
    """
    This class represents a table in the sqlite database.

    This class mimicks some of the features of a dictionary so the saved
    entries are able to be accessed by using the attaribute name as a key.
    """

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
        try:
            return eval(value)
        except:  # NOQA
            return value

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
    """
    This class handles the actual connection to the sqlite database.

    Handles what table in the database is to be accessed. The tables are
    not cached because most of the information that is stored only gets loaded
    when the application starts and data gets saved to the database if a value
    gets modified and also when the application exits.
    """

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
