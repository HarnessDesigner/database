from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import DescriptionMixin


class TransitionAdhesivesTable(TableBase):
    __table_name__ = 'transition_adhesives'

    def __iter__(self) -> _Iterable["TransitionAdhesive"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionAdhesive(self, db_id)

    def insert(self, code: str, description: str) -> "TransitionAdhesive":
        db_id = TableBase.insert(self, code=code, description=description)
        return TransitionAdhesive(self, db_id)


class TransitionAdhesive(EntryBase, DescriptionMixin):
    _table: TransitionAdhesivesTable = None

    @property
    def code(self) -> str:
        return self._table.select('code', id=self._db_id)[0][0]

    @code.setter
    def code(self, value: str):
        self._table.update(self._db_id, code=value)

