from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import DescriptionMixin


class PlatingsTable(TableBase):
    __table_name__ = 'platings'

    def __iter__(self) -> _Iterable["Plating"]:

        for db_id in TableBase.__iter__(self):
            yield Plating(self, db_id)

    def insert(self, symbol: str, description: str) -> "Plating":
        db_id = TableBase.insert(self, symbol=symbol, description=description)
        return Plating(self, db_id)


class Plating(EntryBase, DescriptionMixin):
    _table: PlatingsTable = None

    @property
    def symbol(self) -> str:
        return self._table.select('symbol', id=self._db_id)[0][0]

    @symbol.setter
    def symbol(self, value: str):
        self._table.update(self._db_id, symbol=value)
