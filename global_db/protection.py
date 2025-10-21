from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin


class ProtectionsTable(TableBase):
    __table_name__ = 'protections'

    def __iter__(self) -> _Iterable["Protection"]:
        for db_id in TableBase.__iter__(self):
            yield Protection(self, db_id)

    def insert(self, name: str) -> "Protection":
        db_id = TableBase.insert(self, name=name)
        return Protection(self, db_id)


class Protection(EntryBase, NameMixin):
    _table: ProtectionsTable = None
