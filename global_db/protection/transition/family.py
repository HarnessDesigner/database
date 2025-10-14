from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class TransitionFamiliesTable(TableBase):
    __table_name__ = 'transition_families'

    def __iter__(self) -> _Iterable["TransitionFamily"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionFamily(self, db_id)

    def insert(self, name: str) -> "TransitionFamily":
        db_id = TableBase.insert(self, name=name)
        return TransitionFamily(self, db_id)


class TransitionFamily(EntryBase, NameMixin):
    __table_name__ = 'transition_families'
