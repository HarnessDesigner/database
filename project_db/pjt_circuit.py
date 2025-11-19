from typing import Iterable as _Iterable, TYPE_CHECKING

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_wire as _pjt_wire
    from . import pjt_splice as _pjt_splice
    from . import pjt_terminal as _pjt_terminal
    from . import pjt_housing as _pjt_housing


class PJTCircuitsTable(PJTTableBase):
    __table_name__ = 'pjt_circuits'

    def __iter__(self) -> _Iterable["PJTCircuit"]:

        for db_id in PJTTableBase.__iter__(self):
            yield PJTCircuit(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTCircuit":
        if isinstance(item, int):
            if item in self:
                return PJTCircuit(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

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

    @property
    def wires(self) -> list["_pjt_wire.PJTWire"]:
        res = []
        for wire_id in self._table.db.pjt_wires_table.select('id', circuit_id=self._db_id):
            res.append(self._table.db.pjt_wires_table[wire_id[0]])

        return res

    @property
    def splices(self) -> list["_pjt_splice.PJTSplice"]:
        res = []
        for wire_id in self._table.db.pjt_splices_table.select('id', circuit_id=self._db_id):
            res.append(self._table.db.pjt_splices_table[wire_id[0]])

        return res

    @property
    def terminals(self) -> list["_pjt_terminal.PJTTerminal"]:
        res = []
        for wire_id in self._table.db.pjt_terminals_table.select('id', circuit_id=self._db_id):
            res.append(self._table.db.pjt_terminals_table[wire_id[0]])

        return res

    @property
    def housings(self) -> list["_pjt_housing.PJTHousing"]:
        res = []
        for wire_id in self._table.db.pjt_housings_table.select('id', circuit_id=self._db_id):
            res.append(self._table.db.pjt_housings_table[wire_id[0]])

        return res

