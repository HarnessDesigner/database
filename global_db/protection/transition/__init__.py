
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import PartNumberMixin

from ... import temperature as _temperature
from . import series as _series
from . import adhesive as _adhesive
from . import size as _size


class TransitionsTable(TableBase):
    __table_name__ = 'transitions'

    def __iter__(self) -> _Iterable["Transition"]:
        for db_id in TableBase.__iter__(self):
            yield Transition(self, db_id)

    def insert(self, part_number: str, tran_series_id: int, tran_adhesive_id: int, 
               tran_size_ids: int) -> "Transition":
        db_id = TableBase.insert(self, part_number=part_number, tran_series_id=tran_series_id, 
                                 tran_adhesive_id=tran_adhesive_id, tran_size_ids=tran_size_ids)

        return Transition(self, db_id)


class Transition(EntryBase, PartNumberMixin):
    
    _table: TransitionsTable = None
    
    @property
    def series(self) -> _series.TransitionSeries:
        series_id = self._table.select('tran_series_id', id=self._db_id)
        return _series.TransitionSeries(self._table.db.transition_series_table, series_id[0][0])

    @property
    def tran_series_id(self) -> int:
        return self._table.select('tran_series_id', id=self._db_id)[0][0]

    @property
    def adhesive(self) -> _adhesive.TransitionAdhesive:
        tran_adhesive_id = self._table.select('tran_adhesive_id', id=self._db_id)
        return _adhesive.TransitionAdhesive(self._table.db.transition_adhesives_table, tran_adhesive_id[0][0])

    @adhesive.setter
    def adhesive(self, value: _adhesive.TransitionAdhesive):
        self._table.update(self._db_id, tran_adhesive_id=value.db_id)

    @property
    def tran_adhesive_id(self) -> int:
        return self._table.select('tran_adhesive_id', id=self._db_id)[0][0]

    @tran_adhesive_id.setter
    def tran_adhesive_id(self, value: int):
        self._table.update(self._db_id, tran_adhesive_id=value)
    
    @property
    def sizes(self) -> list[_size.TransitionSize]:
        res = []
        tran_size_ids = eval(self._table.select('tran_size_ids', id=self._db_id)[0][0])
        for size_id in tran_size_ids:
            res.append(_size.TransitionSize(self._table.db.transition_sizes_table, size_id))
            
        return res

    @sizes.setter
    def sizes(self, value: list[_size.TransitionSize]):
        values = [v.db_id for v in value]        
        self._table.update(self._db_id, tran_size_ids=str(values))
