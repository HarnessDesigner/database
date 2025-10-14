
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin, DescriptionMixin, ManufacturerMixin


class BundleCoverSeriesTable(TableBase):
    __table_name__ = 'bundle_cover_series'

    def __iter__(self) -> _Iterable["BundleCoverSeries"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCoverSeries(self, db_id)

    def insert(self, name: str, mfg_id: int, description: str, ) -> "BundleCoverSeries":
        db_id = TableBase.insert(self, name=name, mfg_id=mfg_id, description=description)
        return BundleCoverSeries(self, db_id)


class BundleCoverSeries(EntryBase, NameMixin, DescriptionMixin, ManufacturerMixin):
    _table: BundleCoverSeriesTable = None
