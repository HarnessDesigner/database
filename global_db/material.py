from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import DescriptionMixin, NameMixin


class MaterialsTable(TableBase):
    __table_name__ = 'materials'

    def __iter__(self) -> _Iterable["Material"]:

        for db_id in TableBase.__iter__(self):
            yield Material(self, db_id)

    def insert(self, name: str, description: str) -> "Material":
        db_id = TableBase.insert(self, name=name, description=description)
        return Material(self, db_id)


class Material(EntryBase, NameMixin, DescriptionMixin):
    _table: MaterialsTable = None
