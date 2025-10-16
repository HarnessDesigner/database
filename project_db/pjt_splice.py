
from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTSplicesTable(PJTTableBase):
    __table_name__ = 'pjt_splices'

    def __iter__(self) -> _Iterable["PJTSplice"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTSplice(self, db_id, self.project_id)

    def insert(self, part_id: int, circuit_id: int, coord3d_id: int, coord2d_id: int) -> "PJTSplice":
        db_id = PJTTableBase.insert(self, project_id=self.project_id, part_id=part_id,
                                    circuit_id=circuit_id, coord3d_id=coord3d_id, coord2d_id=coord2d_id)
        return PJTSplice(self, db_id, self.project_id)


class PJTSplice(PJTEntryBase):
    _table: PJTSplicesTable = None

    @property
    def coord3d(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.coord3d_id
        return self._table.db.pjt_coordinate_3d[coord_id]

    @property
    def coord3d_id(self) -> int:
        return self._table.select('coord3d_id', id=self._db_id)[0][0]

    @coord3d_id.setter
    def coord3d_id(self, value: int):
        self._table.update(self._db_id, coord3d_id=value)

    @property
    def coord2d(self) -> "_pjt_coordinate_2d.PJTCoordinate2D":
        coord_id = self.coord2d_id
        return self._table.db.pjt_coordinate_2d[coord_id]

    @property
    def coord2d_id(self) -> int:
        return self._table.select('coord2d_id', id=self._db_id)[0][0]

    @coord2d_id.setter
    def coord2d_id(self, value: int):
        self._table.update(self._db_id, coord2d_id=value)

    @property
    def circuit(self) -> "_pjt_circuit.PJTCircuit":
        circuit_id = self.circuit_id
        return self._table.db.pjt_circuits[circuit_id]

    @property
    def circuit_id(self) -> int:
        return self._table.select('circuit_id', id=self._db_id)[0][0]

    @circuit_id.setter
    def circuit_id(self, value: int):
        self._table.update(self._db_id, circuit_id=value)

    @property
    def part(self) -> "_splice.Splice":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.splices_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d
from . import pjt_coordinate_2d as _pjt_coordinate_2d
from . import pjt_circuit as _pjt_circuit

from ..global_db import splice as _splice
