
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase


class TransitionSizesTable(TableBase):
    __table_name__ = 'transition_sizes'

    def __iter__(self) -> _Iterable["TransitionSize"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionSize(self, db_id)

    def insert(self, min: float, max: float) -> "TransitionSize":  # NOQA
        db_id = TableBase.insert(self, min=min, max=max)
        return TransitionSize(self, db_id)


class TransitionSize(EntryBase):
    _table_name: TransitionSizesTable = None

    @property
    def min(self) -> float:
        return self._table.select('min', id=self._db_id)[0][0]

    @min.setter
    def min(self, value: float):
        self._table.update(self._db_id, min=value)

    @property
    def max(self) -> float:
        return self._table.select('max', id=self._db_id)[0][0]

    @max.setter
    def max(self, value: float):
        self._table.update(self._db_id, max=value)
