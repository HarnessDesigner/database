from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import DescriptionMixin


class MaterialsTable(TableBase):
    __table_name__ = 'materials'

    def __iter__(self) -> _Iterable["Material"]:

        for db_id in TableBase.__iter__(self):
            yield Material(self, db_id)

    def insert(self, symbol: str, description: str) -> "Material":
        db_id = TableBase.insert(self, symbol=symbol, description=description)
        return Material(self, db_id)


class Material(EntryBase, DescriptionMixin):
    _table: MaterialsTable = None

    @property
    def symbol(self) -> str:
        return self._table.select('symbol', id=self._db_id)[0][0]

    @symbol.setter
    def symbol(self, value: str):
        self._table.update(self._db_id, symbol=value)
