
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin


class TransitionMaterialsTable(TableBase):
    __table_name__ = 'transition_materials'
    
    def __iter__(self) -> _Iterable["TransitionMaterial"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionMaterial(self, db_id)

    def insert(self, name: str) -> "TransitionMaterial":
        
        db_id = TableBase.insert(self, name=name)
        
        return TransitionMaterial(self, db_id)


class TransitionMaterial(EntryBase, NameMixin):
    _table: TransitionMaterialsTable = None
