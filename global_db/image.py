from typing import Iterable as _Iterable

from . import EntryBase, TableBase


class ImagesTable(TableBase):
    __table_name__ = 'images'

    def __iter__(self) -> _Iterable["Image"]:

        for db_id in TableBase.__iter__(self):
            yield Image(self, db_id)

    def insert(self, path: str, data: bytes | None) -> "Image":
        db_id = TableBase.insert(self, path=path, data=data)

        return Image(self, db_id)


class Image(EntryBase):
    _table: ImagesTable = None

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
