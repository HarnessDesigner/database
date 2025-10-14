from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin, DescriptionMixin, ManufacturerMixin


class SeriesTable(TableBase):
    __table_name__ = 'series'

    def __iter__(self) -> _Iterable["Series"]:
        for db_id in TableBase.__iter__(self):
            yield Series(self, db_id)

    def insert(self, name: str, mfg_id: int, description: str, ) -> "Series":
        db_id = TableBase.insert(self, name=name, mfg_id=mfg_id, description=description)
        return Series(self, db_id)


class Series(EntryBase, NameMixin, DescriptionMixin, ManufacturerMixin):
    _table: SeriesTable = None
