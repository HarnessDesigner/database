from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class TransitionProtectionsTable(TableBase):
    __table_name__ = 'transition_protections'

    def __iter__(self) -> _Iterable["TransitionProtection"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionProtection(self, db_id)

    def insert(self, name: str) -> "TransitionProtection":
        db_id = TableBase.insert(self, name=name)
        return TransitionProtection(self, db_id)


class TransitionProtection(EntryBase, NameMixin):
    _table: TransitionProtectionsTable = None
