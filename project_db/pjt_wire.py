
from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_point_3d as _pjt_point_3d
    from . import pjt_point_2d as _pjt_point_2d
    from . import pjt_circuit as _pjt_circuit

    from ..global_db import wire as _wire


class PJTWiresTable(PJTTableBase):
    __table_name__ = 'pjt_wires'

    def __iter__(self) -> _Iterable["PJTWire"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTWire(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTWire":
        if isinstance(item, int):
            if item in self:
                return PJTWire(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, circuit_id: int, start_coord3d_id: int | None, stop_coord3d_id: int | None,
               start_coord2d_id: int | None, stop_coord2d_id: int | None, is_visible: bool) -> "PJTWire":

        db_id = PJTTableBase.insert(self, part_id=part_id, circuit_id=circuit_id,
                                    start_coord3d_id=start_coord3d_id, stop_coord3d_id=stop_coord3d_id,
                                    start_coord2d_id=start_coord2d_id, stop_coord2d_id=stop_coord2d_id,
                                    is_visible=int(is_visible))

        return PJTWire(self, db_id, self.project_id)


class PJTWire(PJTEntryBase):
    _table: PJTWiresTable = None

    @property
    def start_point3d(self) -> "_pjt_point_3d.PJTPoint3D":
        coord_id = self.start_coord3d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_points_3d_table[coord_id]

    @property
    def start_coord3d_id(self) -> int:
        return self._table.select('start_coord3d_id', id=self._db_id)[0][0]

    @start_coord3d_id.setter
    def start_coord3d_id(self, value: int):
        self._table.update(self._db_id, start_coord3d_id=value)

    @property
    def stop_point3d(self) -> "_pjt_point_3d.PJTPoint3D":
        coord_id = self.stop_coord3d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_points_3d_table[coord_id]

    @property
    def stop_coord3d_id(self) -> int:
        return self._table.select('stop_coord3d_id', id=self._db_id)[0][0]

    @stop_coord3d_id.setter
    def stop_coord3d_id(self, value: int):
        self._table.update(self._db_id, stop_coord3d_id=value)
    
    @property
    def start_point2d(self) -> "_pjt_point_2d.PJTPoint2D":
        coord_id = self.start_coord2d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_points_2d_table[coord_id]

    @property
    def start_coord2d_id(self) -> int:
        return self._table.select('start_coord2d_id', id=self._db_id)[0][0]

    @start_coord2d_id.setter
    def start_coord2d_id(self, value: int):
        self._table.update(self._db_id, start_coord2d_id=value)

    @property
    def stop_point2d(self) -> "_pjt_point_2d.PJTPoint2D":
        coord_id = self.stop_coord2d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_points_2d_table[coord_id]

    @property
    def stop_coord2d_id(self) -> int:
        return self._table.select('stop_coord2d_id', id=self._db_id)[0][0]

    @stop_coord2d_id.setter
    def stop_coord2d_id(self, value: int):
        self._table.update(self._db_id, stop_coord2d_id=value)
        
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
    def is_visible(self) -> bool:
        return bool(self._table.select('is_visible', id=self._db_id)[0][0])

    @is_visible.setter
    def is_visible(self, value: bool):
        self._table.update(self._db_id, is_visible=int(value))

    @property
    def part(self) -> "_wire.Wire":
        part_id = self.part_id
        if part_id is None:
            return None
        
        return self._table.db.global_db.wires_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)
