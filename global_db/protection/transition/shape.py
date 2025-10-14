
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class TransitionShapesTable(TableBase):
    __table_name__ = 'transition_shapes'

    def __iter__(self) -> _Iterable["TransitionShape"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionShape(self, db_id)

    def insert(self, name: str) -> "TransitionShape":
        db_id = TableBase.insert(self, name=name)
        return TransitionShape(self, db_id)


class TransitionShape(EntryBase, NameMixin):
    _table: TransitionShapesTable = None
