
from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_point_3d as _pjt_point_3d
    from . import pjt_point_2d as _pjt_point_2d
    from . import pjt_circuit as _pjt_circuit
    from . import pjt_wire as _pjt_wire

    from ..global_db import splice as _splice


class PJTSplicesTable(PJTTableBase):
    __table_name__ = 'pjt_splices'

    def __iter__(self) -> _Iterable["PJTSplice"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTSplice(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTSplice":
        if isinstance(item, int):
            if item in self:
                return PJTSplice(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, circuit_id: int, point3d_id: int, point2d_id: int) -> "PJTSplice":
        db_id = PJTTableBase.insert(self, part_id=part_id, circuit_id=circuit_id,
                                    point3d_id=point3d_id, point2d_id=point2d_id)

        return PJTSplice(self, db_id, self.project_id)


class PJTSplice(PJTEntryBase):
    _table: PJTSplicesTable = None

    @property
    def table(self) -> PJTSplicesTable:
        return self._table

    @property
    def wire(self) -> "_pjt_wire.PJTWire":
        db_ids = self._table.db.pjt_wires_table.select(
            'id', OR=True, start_point3d_id=self.point1_3d_id, stop_point3d_id=self.point1_3d_id)
        for db_id in db_ids:
            return self._table.db.pjt_wires_table[db_id[0]]

    @property
    def attached_wires(self) -> list["_pjt_wire.PJTWire"]:
        res = []
        db_ids = self._table.db.pjt_wires_table.select(
            'id', OR=True, start_point3d_id=self.point2_3d_id, stop_point3d_id=self.point2_3d_id)

        for db_id in db_ids:
            res.append(self._table.db.pjt_wires_table[db_id[0]])

        return res

    @property
    def point1_3d(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.point1_3d_id
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def point1_3d_id(self) -> int:
        return self._table.select('point1_3d_id', id=self._db_id)[0][0]

    @point1_3d_id.setter
    def point1_3d_id(self, value: int):
        self._table.update(self._db_id, point1_3d_id=value)
        self._process_callbacks()

    @property
    def point2_3d(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.point2_3d_id
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def point2_3d_id(self) -> int:
        return self._table.select('point2_3d_id', id=self._db_id)[0][0]

    @point2_3d_id.setter
    def point2_3d_id(self, value: int):
        self._table.update(self._db_id, point2_3d_id=value)
        self._process_callbacks()

    @property
    def point3_3d(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.point3_3d_id
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def point3_3d_id(self) -> int:
        return self._table.select('point3_3d_id', id=self._db_id)[0][0]

    @point3_3d_id.setter
    def point3_3d_id(self, value: int):
        self._table.update(self._db_id, point3_3d_id=value)
        self._process_callbacks()

    @property
    def point2d(self) -> "_pjt_point_2d.PJTPoint2D":
        point_id = self.point2d_id
        return self._table.db.pjt_points_2d_table[point_id]

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
        self._process_callbacks()
