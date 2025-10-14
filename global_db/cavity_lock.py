
from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin, DescriptionMixin


class CavityLocksTable(TableBase):
    __table_name__ = 'cavity_locks'

    def __iter__(self) -> _Iterable["CavityLock"]:
        for db_id in TableBase.__iter__(self):
            yield CavityLock(self, db_id)

    def insert(self, name: str, description: str) -> "CavityLock":
        db_id = TableBase.insert(self, name=name, description=description)
        return CavityLock(self, db_id)


class CavityLock(EntryBase, NameMixin, DescriptionMixin):
    _table: CavityLocksTable = None
