
from typing import Iterable as _Iterable

from .import EntryBase, TableBase
from .mixins import NameMixin


class ShapesTable(TableBase):
    __table_name__ = 'shapes'

    def __iter__(self) -> _Iterable["Shape"]:
        for db_id in TableBase.__iter__(self):
            yield Shape(self, db_id)

    def insert(self, name: str) -> "Shape":
        db_id = TableBase.insert(self, name=name)
        return Shape(self, db_id)


class Shape(EntryBase, NameMixin):
    _table: ShapesTable = None
