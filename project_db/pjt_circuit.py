from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTCircuitsTable(PJTTableBase):
    __table_name__ = 'pjt_circuits'

    def __iter__(self) -> _Iterable["PJTCircuit"]:

        for db_id in PJTTableBase.__iter__(self):
            yield PJTCircuit(self, db_id, self.project_id)

    def insert(self, circuit_num: int, name: str, description: str) -> "PJTCircuit":
        db_id = PJTTableBase.insert(self, circuit_num=circuit_num,
                                    name=name, description=description)

        return PJTCircuit(self, db_id, self.project_id)


class PJTCircuit(PJTEntryBase):
    _table: PJTCircuitsTable = None

    @property
    def circuit_num(self) -> int:
        return self._table.select('circuit_num', id=self._db_id)[0][0]

    @circuit_num.setter
    def circuit_num(self, value: int):
        self._table.update(self._db_id, circuit_num=value)

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)

    @property
    def description(self) -> str:
        return self._table.select('description', id=self._db_id)[0][0]

    @description.setter
    def description(self, value: str):
        self._table.update(self._db_id, description=value)
