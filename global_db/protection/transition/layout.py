
from typing import Iterable as _Iterable, TYPE_CHECKING

from ... import EntryBase, TableBase
from ...mixins import OverlayMixin, ImageMixin
from . import branch as _branch

if TYPE_CHECKING:
    from . import series as _series


class TransitionLayoutsTable(TableBase):
    __table_name__ = 'transition_maps'
    
    def __iter__(self) -> _Iterable["TransitionLayout"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionLayout(self, db_id)

    def insert(self, tran_series_id: int, overlay_id: int, 
               image_id: int, num_branches: int) -> "TransitionLayout":
        
        db_id = TableBase.insert(self, tran_series_id=tran_series_id, overlay_id=overlay_id, 
                                 image_id=image_id, num_branches=num_branches)
        
        return TransitionLayout(self, db_id)


class TransitionLayout(EntryBase, OverlayMixin, ImageMixin):
    _table: TransitionLayoutsTable = None
    
    @property
    def series(self) -> "_series.TransitionSeries":
        from .series import TransitionSeries
        tran_series_id = self._table.select('tran_series_id', id=self._db_id)
        return TransitionSeries(self._table.db.transition_series_table, tran_series_id[0][0])

    @property
    def tran_series_id(self) -> int:
        return self._table.select('tran_series_id', id=self._db_id)[0][0]
    
    @property
    def branches(self) -> list[_branch.TransitionBranch]:
        res = []
        db_ids = self._table.db.transition_branches_table.select('id', transition_map_id=self._db_id)
        for db_id in db_ids:
            res.append(_branch.TransitionBranch(self._table.db.transition_branches_table, db_id[0]))
            
        return res

    @property
    def num_branches(self) -> str:
        return self._table.select('num_branches', id=self._db_id)[0][0]

    @num_branches.setter
    def num_branches(self, value: str):
        self._table.update(self._db_id, num_branches=value)

    
    