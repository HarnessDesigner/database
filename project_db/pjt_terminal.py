from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_cavity as _pjt_cavity
    from . import pjt_circuit as _pjt_circuit
    from . import pjt_point_2d as _pjt_point_2d
    from . import pjt_point_3d as _pjt_point_3d

    from ..global_db import terminal as _terminal
    from ..global_db import seal as _seal


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

    def insert(self, part_id: int, cavity_id: int, seal_id: int, circuit_id: int,
               coord3d_id: int, coord2d_id: int) -> "PJTTerminal":

        db_id = PJTTableBase.insert(self, part_id=part_id, cavity_id=cavity_id,
                                    seal_id=seal_id, circuit_id=circuit_id,
                                    coord3d_id=coord3d_id, coord2d_id=coord2d_id)

        return PJTTerminal(self, db_id, self.project_id)


class PJTTerminal(PJTEntryBase):
    _table: PJTTerminalsTable = None

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

    @property
    def point3d(self) -> "_pjt_point_3d.PJTPoint3D":
        coord3d_id = self.coord3d_id
        return self._table.db.pjt_points_3d_table[coord3d_id]

    @property
    def coord3d_id(self) -> int:
        return self._table.select('coord3d_id', id=self._db_id)[0][0]

    @coord3d_id.setter
    def coord3d_id(self, value: int):
        self._table.update(self._db_id, coord3d_id=value)

    @property
    def point2d(self) -> "_pjt_point_2d.PJTPoint2D":
        coord2d_id = self.coord2d_id
        return self._table.db.pjt_points_2d_table[coord2d_id]

    @property
    def coord2d_id(self) -> int:
        return self._table.select('coord2d_id', id=self._db_id)[0][0]

    @coord2d_id.setter
    def coord2d_id(self, value: int):
        self._table.update(self._db_id, coord2d_id=value)

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

    @property
    def seal(self) -> "_seal.Seal":
        seal_id = self.seal_id
        if seal_id is None:
            return None

        return self._table.db.global_db.seals_table[seal_id]

    @property
    def seal_id(self) -> int:
        return self._table.select('seal_id', id=self._db_id)[0][0]

    @seal_id.setter
    def seal_id(self, value: int):
        self._table.update(self._db_id, seal_id=value)
    
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
