from typing import TYPE_CHECKING, Iterable as _Iterable

import numpy as np

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal

if TYPE_CHECKING:
    from . import pjt_cavity as _pjt_cavity
    from . import pjt_circuit as _pjt_circuit
    from . import pjt_point_2d as _pjt_point_2d
    from . import pjt_point_3d as _pjt_point_3d
    from . import pjt_seal as _pjt_seal

    from ..global_db import terminal as _terminal


class PJTTerminalsTable(PJTTableBase):
    __table_name__ = 'pjt_terminals'

    def __iter__(self) -> _Iterable["PJTTerminal"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTTerminal(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTTerminal":
        if isinstance(item, int):
            if item in self:
                return PJTTerminal(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, cavity_id: int, circuit_id: int,
               point3d_id: int, point2d_id: int, angle: _decimal,
               quat: np.ndarray) -> "PJTTerminal":

        db_id = PJTTableBase.insert(self, part_id=part_id, cavity_id=cavity_id,
                                    circuit_id=circuit_id, point3d_id=point3d_id,
                                    point2d_id=point2d_id, angle=float(angle),
                                    quat=str(quat.tolist()))

        return PJTTerminal(self, db_id, self.project_id)


class PJTTerminal(PJTEntryBase):
    _table: PJTTerminalsTable = None

    @property
    def quat(self) -> np.ndarray:
        return np.array(eval(self._table.select('quat', id=self._db_id)[0][0]), dtype=np.dtypes.Float64DType)

    @quat.setter
    def quat(self, value: np.ndarray):
        value = str(value.tolist())
        self._table.update(self._db_id, quat=value)
        self._process_callbacks()

    @property
    def angle(self) -> _decimal:
        return _decimal(self._table.select('cavity_id', id=self._db_id)[0][0])

    @angle.setter
    def angle(self, value: _decimal):
        self._table.update(self._db_id, angle=float(value))
        self._process_callbacks()

    @property
    def table(self) -> PJTTerminalsTable:
        return self._table

    @property
    def cavity(self) -> "_pjt_cavity.PJTCavity":
        cavity_id = self.cavity_id
        return self._table.db.pjt_cavities_table[cavity_id]

    @property
    def cavity_id(self) -> int:
        return self._table.select('cavity_id', id=self._db_id)[0][0]

    @cavity_id.setter
    def cavity_id(self, value: int):
        self._table.update(self._db_id, cavity_id=value)
        self._process_callbacks()

    @property
    def point3d(self) -> "_pjt_point_3d.PJTPoint3D":
        point3d_id = self.point3d_id
        return self._table.db.pjt_points_3d_table[point3d_id]

    @property
    def point3d_id(self) -> int:
        return self._table.select('point3d_id', id=self._db_id)[0][0]

    @point3d_id.setter
    def point3d_id(self, value: int):
        self._table.update(self._db_id, point3d_id=value)
        self._process_callbacks()

    @property
    def point2d(self) -> "_pjt_point_2d.PJTPoint2D":
        point2d_id = self.point2d_id
        return self._table.db.pjt_points_2d_table[point2d_id]

    @property
    def point2d_id(self) -> int:
        return self._table.select('point2d_id', id=self._db_id)[0][0]

    @point2d_id.setter
    def point2d_id(self, value: int):
        self._table.update(self._db_id, point2d_id=value)
        self._process_callbacks()

    @property
    def circuit(self) -> "_pjt_circuit.PJTCircuit":
        circuit_id = self.circuit_id
        return self._table.db.pjt_circuits_table[circuit_id]

    @property
    def circuit_id(self) -> int:
        return self._table.select('circuit_id', id=self._db_id)[0][0]

    @circuit_id.setter
    def circuit_id(self, value: int):
        self._table.update(self._db_id, circuit_id=value)
        self._process_callbacks()

    @property
    def seal(self) -> "_pjt_seal.PJTSeal":
        db_ids = self._table.db.pjt_seals_table.select('id', terminal_id=self.db_id)

        for db_id in db_ids:
            try:
                seal = self._table.db.pjt_seals_table[db_id[0]]
            except IndexError:
                continue

            return seal

    @property
    def part(self) -> "_terminal.Terminal":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.terminals_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)
        self._process_callbacks()
