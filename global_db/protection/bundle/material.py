
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class BundleCoverMaterialsTable(TableBase):
    __table_name__ = 'bundle_cover_materials'

    def __iter__(self) -> _Iterable["BundleCoverMaterial"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCoverMaterial(self, db_id)

    def insert(self, name: str) -> "BundleCoverMaterial":
        db_id = TableBase.insert(self, name=name)
        return BundleCoverMaterial(self, db_id)


class BundleCoverMaterial(EntryBase, NameMixin):
    _table: BundleCoverMaterialsTable = None
