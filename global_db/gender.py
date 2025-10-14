from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin


class GendersTable(TableBase):
    __table_name__ = 'genders'

    def __iter__(self) -> _Iterable["Gender"]:
        for db_id in TableBase.__iter__(self):
            yield Gender(self, db_id)

    def insert(self, name: str) -> "Gender":
        db_id = TableBase.insert(self, name=name)
        return Gender(self, db_id)


class Gender(EntryBase, NameMixin):
    _table: GendersTable = None
