from typing import Iterable as _Iterable, TYPE_CHECKING

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal

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

    def insert(self, circuit_num: int, name: str, description: str, volts: _decimal,
               load: _decimal, voltage_drop: _decimal) -> "PJTCircuit":

        db_id = PJTTableBase.insert(self, circuit_num=circuit_num,
                                    name=name, description=description, volts=float(volts),
                                    load=float(load), voltage_drop=float(voltage_drop))

        return PJTCircuit(self, db_id, self.project_id)


class PJTCircuit(PJTEntryBase):
    _table: PJTCircuitsTable = None

    @property
    def table(self) -> PJTCircuitsTable:
        return self._table

    @property
    def circuit_num(self) -> int:
        return self._table.select('circuit_num', id=self._db_id)[0][0]

    @circuit_num.setter
    def circuit_num(self, value: int):
        self._table.update(self._db_id, circuit_num=value)
        self._process_callbacks()

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)
        self._process_callbacks()

    @property
    def description(self) -> str:
        return self._table.select('description', id=self._db_id)[0][0]

    @description.setter
    def description(self, value: str):
        self._table.update(self._db_id, description=value)
        self._process_callbacks()

    @property
    def volts(self) -> _decimal:
        return _decimal(self._table.select('volts', id=self._db_id)[0][0])

    @volts.setter
    def volts(self, value: _decimal):
        self._table.update(self._db_id, volts=float(value))
        self._process_callbacks()

    @property
    def load(self) -> _decimal:
        return _decimal(self._table.select('load', id=self._db_id)[0][0])

    @load.setter
    def load(self, value: _decimal):
        self._table.update(self._db_id, load=float(value))
        self._process_callbacks()

    @property
    def voltage_drop(self) -> _decimal:
        return _decimal(self._table.select('voltage_drop', id=self._db_id)[0][0])

    @voltage_drop.setter
    def voltage_drop(self, value: _decimal):
        self._table.update(self._db_id, voltage_drop=float(value))
        self._process_callbacks()

    @property
    def wire_length_mm(self) -> _decimal:
        return sum([wire.length_mm for wire in self.wires])

    @property
    def wire_length_m(self) -> _decimal:
        return self.wire_length_mm / _decimal(1000.0)

    @property
    def wire_length_ft(self) -> _decimal:
        return self.wire_length_m * _decimal(3.28084)

    @property
    def wire_weight_g(self) -> _decimal:
        return sum([wire.weight_g for wire in self.wires])

    @property
    def wire_weight_lb(self) -> _decimal:
        return sum([wire.weight_lb for wire in self.wires])

    @property
    def terminal_weight_g(self):
        return sum([terminal.part.weight for terminal in self.terminals])

    @property
    def terminal_weight_lb(self):
        weight_g = self.terminal_weight_g
        return weight_g * _decimal(0.00220462)

    @property
    def splice_weight_g(self):
        return sum([splice.part.weight for splice in self.splices])

    @property
    def splice_weight_lb(self):
        weight_g = self.splice_weight_g
        return weight_g * _decimal(0.00220462)

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

