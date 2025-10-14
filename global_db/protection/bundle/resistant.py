
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class BundleCoverResistancesTable(TableBase):
    __table_name__ = 'bundle_cover_resistances'

    def __iter__(self) -> _Iterable["BundleCoverResistant"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCoverResistant(self, db_id)

    def insert(self, name: str, value: int) -> "BundleCoverResistant":
        db_id = TableBase.insert(self, name=name, value=value)
        return BundleCoverResistant(self, db_id)


class BundleCoverResistant(EntryBase, NameMixin):
    _table: BundleCoverResistancesTable = None
    
    @property
    def value(self) -> int:
        return self._table.select('value', id=self._db_id)[0][0]

    @value.setter
    def value(self, value: int):
        self._table.update(self._db_id, value=value)
