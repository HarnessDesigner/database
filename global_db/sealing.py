from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin


class SealingsTable(TableBase):
    __table_name__: str = 'sealings'

    def __iter__(self) -> _Iterable["Sealing"]:
        for db_id in TableBase.__iter__(self):
            yield Sealing(self, db_id)

    def insert(self, name: str) -> "Sealing":

        db_id = TableBase.insert(self, name=name)
        return Sealing(self, db_id)


class Sealing(EntryBase, NameMixin):
    _table: SealingsTable = None
