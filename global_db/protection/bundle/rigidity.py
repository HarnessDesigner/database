
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class BundleCoverRigiditiesTable(TableBase):
    __table_name__ = 'bundle_cover_rigidities'

    def __iter__(self) -> _Iterable["BundleCoverRigidity"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCoverRigidity(self, db_id)

    def insert(self, name: str) -> "BundleCoverRigidity":
        db_id = TableBase.insert(self, name=name)
        return BundleCoverRigidity(self, db_id)


class BundleCoverRigidity(EntryBase, NameMixin):
    _table: BundleCoverRigiditiesTable = None




