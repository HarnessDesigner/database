"""SQLite-flavored SQL table and field definition helpers.

Ported from
harness_designer/database/db_connectors/sqlite_connector/sql_table.py,
dropping the check_types decorator and the app's shared logger (replaced
with the stdlib logging module). The class/field API is otherwise
unchanged so create_database/*.py's `table = SQLTable(...)` definitions
port over verbatim.

Adjusted for this builder's single-database, no-ATTACH context: the
original `is_in_db`/`is_ok`/`update_fields`/`add_to_db` addressed the
connector wrapper via `db_cursor._con` and multi-database-qualified
`sqlite_master` lookups (`{db_cursor.database_name}.sqlite_master`). This
builder always has exactly one open database, so those methods here call
`db_cursor.execute(...)`/`db_cursor.fetchall()` directly against the plain
`sqlite_master` table.
"""

import logging

_log = logging.getLogger('builder.sql_table')

FIELD_TYPE_REAL = 'REAL'
FIELD_TYPE_TEXT = 'TEXT'
FIELD_TYPE_INT = 'INTEGER'
FIELD_TYPE_BLOB = 'BLOB'
FIELD_TYPE_UUID = 'BLOB'

REFERENCE_CASCADE = 'CASCADE'
REFERENCE_DEFAULT = 'SET DEFAULT'


class SQLTable:

    """Describe a SQL table definition for the SQLite connector."""

    def __init__(self, name: str, *fields: "SQLField"):
        self.name = name
        self.fields = fields

    def is_in_db(self, db_cursor) -> bool:
        """Return whether the table already exists in the database."""
        db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        rows = db_cursor.fetchall()

        table_names = [row[0] for row in rows]

        return self.name in table_names

    def is_ok(self, db_cursor) -> bool:
        """Return whether the existing table still needs field updates."""
        db_cursor.execute(f'SELECT "(\'" || group_concat(name, "\', \'") || "\')" from '
                          f'pragma_table_info("{self.name}");')

        column_names = eval(db_cursor.fetchall()[0][0])

        for field in self.fields:
            if field.name not in column_names:
                return True

        return False

    def update_fields(self, db_cursor):
        """Add any missing fields to an existing table."""
        db_cursor.execute(f'SELECT "(\'" || group_concat(name, "\', \'") || "\')" from '
                          f'pragma_table_info("{self.name}");')

        column_names = eval(db_cursor.fetchall()[0][0])

        for field in self.fields:
            if field.name not in column_names:
                field.add_to_table(db_cursor, self.name)

    def add_to_db(self, db_cursor):
        """Create the table in the database."""
        fields = [str(field) for field in self.fields]

        for i, field in enumerate(fields[:]):
            if 'FOREIGN KEY' in field:
                field, foreign_key = field.rsplit(',', 1)
                fields[i] = field
                fields.append(foreign_key)

        fields = ', '.join(fields)

        _log.debug('CREATE TABLE %s (%s);', self.name, fields)

        db_cursor.execute(f'CREATE TABLE {self.name} ({fields});')
        db_cursor.commit()


class SQLFieldReference:

    """Represent a foreign-key reference for a SQL field."""

    def __init__(self, table: SQLTable, field: "SQLField", on_delete=REFERENCE_DEFAULT, on_update=REFERENCE_DEFAULT):
        self.table = table
        self.field = field
        self.on_delete = on_delete
        self.on_update = on_update

    def __str__(self):
        return (f' REFERENCES {self.table.name}({self.field.name}) '
                f'ON DELETE {self.on_delete} '
                f'ON UPDATE {self.on_update}')

    def format(self, field_name):
        """Return the SQL fragment for the foreign-key constraint."""
        return (f'REFERENCES {self.table.name}({self.field.name}) '
                f'ON DELETE {self.on_delete} '
                f'ON UPDATE {self.on_update}')


class SQLField:

    """Represent a single SQL field definition."""

    def __init__(self, name: str, data_type: str, no_null: bool = False,
                 is_unique: bool = False, default: str | None = None,
                 references: SQLFieldReference | None = None, is_primary: bool = False,
                 autoincrement: bool = True):
        self.name = name

        self.type = data_type
        self.default = default
        self.is_unique = is_unique
        self.no_null = no_null
        self.references = references
        self.is_primary = is_primary
        self.autoincrement = autoincrement

        self.parent: SQLTable = None

    def __str__(self):
        """Return the SQL definition fragment for the field."""
        if self.is_primary:
            primary = ' PRIMARY KEY AUTOINCREMENT' if self.autoincrement else ' PRIMARY KEY'
        else:
            primary = ''
        if self.is_unique:
            unique = ' UNIQUE'
        else:
            unique = ''

        if self.no_null:
            null = ' NOT NULL'
        else:
            null = ''

        if self.default is None:
            default = ''
        else:
            default = f' DEFAULT {self.default}'

        res = f'{self.name} {self.type}{primary}{unique}{default}{null}'

        if self.references is not None:
            res += str(self.references)

        return res

    def is_field_in_table(self, db_cursor, table_name: str):
        """Return whether this field exists in the named table."""
        db_cursor.execute(f'SELECT "(\'" || group_concat(name, "\', \'") || "\')" from '
                          f'pragma_table_info("{table_name}");')

        column_names = eval(db_cursor.fetchall()[0][0])

        return self.name in column_names

    def add_to_table(self, db_cursor, table_name: str):
        """Add this field definition to an existing table."""
        field = str(self)

        db_cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {field}')
        db_cursor.commit()


class PrimaryKeyField(SQLField):

    """Represent an auto-incrementing integer primary-key field."""

    def __init__(self, name: str):
        super().__init__(name, FIELD_TYPE_INT, is_primary=True)


class UUIDField(SQLField):

    """Represent a 128-bit, client-generated UUID-style field (16 raw bytes).

    Never engine-generated (no AUTOINCREMENT) -- the value is always
    supplied explicitly on INSERT, whether this field is a primary key or a
    foreign key pointing at one.

    Primary-key usage should leave ``default`` unset (``None``) -- inserts
    always supply an explicit generated id (see id_generator.py). Foreign-key
    usage may set ``default="X'00000000000000000000000000000000'"`` (the
    nil UUID -- 16 zero bytes) as the not-yet-assigned sentinel. The real
    generation mechanism never produces the nil UUID, since a genuine
    timestamp component is always > 0.
    """

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None,
                 references: SQLFieldReference | None = None, is_primary: bool = False):
        super().__init__(name, FIELD_TYPE_UUID, no_null, is_unique,
                         default, references, is_primary, autoincrement=False)


class GeneratedField(SQLField):

    """Represent a virtual generated column, derived from an expression over
    other columns in the same row -- never stored/written directly and never
    supplied on INSERT.
    """

    def __init__(self, name: str, data_type: str, expression: str):
        super().__init__(name, data_type)
        self.expression = expression

    def __str__(self):
        """Return the SQL definition fragment for the generated column."""
        return f'{self.name} {self.type} GENERATED ALWAYS AS ({self.expression}) VIRTUAL'


class ProjectIdField(GeneratedField):

    """Represent the derived ``project_id`` column on a migrated ``pjt_*`` table.

    Zero-config wrapper around GeneratedField so create_database/*.py schema
    files never need to know the raw SQL type literal. This builder never
    creates any pjt_* table (project-scoped, out of scope for a prebuilt
    catalog seed database) -- kept only so ported files whose module-level
    pjt_table definitions reference it still import cleanly.
    """

    def __init__(self):
        super().__init__('project_id', FIELD_TYPE_BLOB, 'substr(id, 1, 3)')


class TextField(SQLField):

    """Represent a text field definition."""

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None, references: SQLField | None = None):
        super().__init__(name, FIELD_TYPE_TEXT, no_null, is_unique,
                         default, references, False)


class FloatField(SQLField):

    """Represent a floating-point field definition."""

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None, references: SQLField | None = None):
        super().__init__(name, FIELD_TYPE_REAL, no_null, is_unique,
                         default, references, False)


class BytesField(SQLField):

    """Represent a bytes/blob field definition."""

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None, references: SQLField | None = None):
        super().__init__(name, FIELD_TYPE_BLOB, no_null, is_unique,
                         default, references, False)


class IntField(SQLField):

    """Represent an integer field definition."""

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None, references: SQLField | None = None):
        super().__init__(name, FIELD_TYPE_INT, no_null, is_unique,
                         default, references, False)


class BlobField(SQLField):

    """Represent a blob field definition."""

    def __init__(self, name: str, no_null: bool = False, is_unique: bool = False,
                 default: str | None = None, references: SQLField | None = None):
        super().__init__(name, FIELD_TYPE_BLOB, no_null, is_unique,
                         default, references, False)
