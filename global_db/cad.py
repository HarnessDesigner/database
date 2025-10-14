from typing import Iterable as _Iterable

from . import EntryBase, TableBase


class CADsTable(TableBase):
    __table_name__ = 'cads'

    def __iter__(self) -> _Iterable["CAD"]:
        for db_id in TableBase.__iter__(self):
            yield CAD(self, db_id)

    def insert(self, path: str, data: bytes | None) -> "CAD":
        db_id = TableBase.insert(self, path=path, data=data)
        return CAD(self, db_id)


class CAD(EntryBase):
    _table: CADsTable = None

    @property
    def path(self) -> str:
        return self._table.select('path', id=self._db_id)[0][0]

    @path.setter
    def path(self, value: str):
        self._table.update(self._db_id, path=value)

    @property
    def data(self) -> bytes | None:
        return self._table.select('data', id=self._db_id)[0][0]

    @data.setter
    def data(self, value: bytes | None):
        self._table.update(self._db_id, data=value)

