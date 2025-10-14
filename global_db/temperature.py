from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin


class TemperaturesTable(TableBase):
    __table_name__ = 'temperatures'

    def __iter__(self) -> _Iterable["Temperature"]:
        for db_id in TableBase.__iter__(self):
            yield Temperature(self, db_id)

    def insert(self, name: str) -> "Temperature":
        db_id = TableBase.insert(self, name=name)
        return Temperature(self, db_id)


class Temperature(EntryBase, NameMixin):
    _table: TemperaturesTable = None
