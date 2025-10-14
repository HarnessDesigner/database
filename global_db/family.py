from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin, DescriptionMixin, ManufacturerMixin


class FamiliesTable(TableBase):
    __table_name__ = 'families'

    def __iter__(self) -> _Iterable["Family"]:
        for db_id in TableBase.__iter__(self):
            yield Family(self, db_id)

    def insert(self, name: str, mfg_id: int, description: str) -> "Family":
        db_id = TableBase.insert(self, name=name, mfg_id=mfg_id, description=description)
        return Family(self, db_id)


class Family(EntryBase, NameMixin, DescriptionMixin, ManufacturerMixin):
    _table: FamiliesTable = None
