from typing import Iterable as _Iterable


from . import EntryBase, TableBase
from .mixins import NameMixin


class DirectionsTable(TableBase):
    __table_name__ = 'directions'

    def __iter__(self) -> _Iterable["Direction"]:

        for db_id in TableBase.__iter__(self):
            yield Direction(self, db_id)

    def insert(self, name: str) -> "Direction":
        db_id = TableBase.insert(self, name=name)
        return Direction(self, db_id)


class Direction(EntryBase, NameMixin):
    _table: DirectionsTable = None
