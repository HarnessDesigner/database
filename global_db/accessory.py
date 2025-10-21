from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import PartNumberMixin, DescriptionMixin, ManufacturerMixin, FamilyMixin, SeriesMixin, ColorMixin, MaterialMixin


class AccessoriesTable(TableBase):
    __table_name__ = 'accessories'

    def __iter__(self) -> _Iterable["Accessory"]:
        for db_id in TableBase.__iter__(self):
            yield Accessory(self, db_id)

    def __getitem__(self, item) -> "Accessory":
        if isinstance(item, int):
            if item in self:
                return Accessory(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Accessory(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, code: str, description: str) -> "Accessory":
        db_id = TableBase.insert(self, code=code, description=description)
        return Accessory(self, db_id)


class Accessory(EntryBase, PartNumberMixin, DescriptionMixin, ManufacturerMixin, FamilyMixin, SeriesMixin, ColorMixin, MaterialMixin):
    _table: AccessoriesTable = None
