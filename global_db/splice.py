

from typing import Iterable as _Iterable

from .import EntryBase, TableBase
from .mixins import PartNumberMixin, ManufacturerMixin, ResourceMixin, DescriptionMixin, Model3DMixin
from ...wrappers.decimal import Decimal as _decimal


class SplicesTable(TableBase):
    __table_name__ = 'splices'

    def __iter__(self) -> _Iterable["Splice"]:
        for db_id in TableBase.__iter__(self):
            yield Splice(self, db_id)

    def __getitem__(self, item) -> "Splice":
        if isinstance(item, int):
            if item in self:
                return Splice(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', name=item)
        if db_id:
            return Splice(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, name: str) -> "Splice":
        db_id = TableBase.insert(self, name=name)
        return Splice(self, db_id)


class Splice(EntryBase, PartNumberMixin, ManufacturerMixin, ResourceMixin,
             DescriptionMixin, ResourceMixin, Model3DMixin):
    _table: SplicesTable = None

    @property
    def diameter(self) -> _decimal:
        return _decimal(self._table.select('diameter', id=self._db_id)[0][0])

    @diameter.setter
    def diameter(self, value: _decimal):
        self._table.update(self._db_id, diameter=float(value))
