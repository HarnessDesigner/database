from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal


if TYPE_CHECKING:
    from . import pjt_point_2d as _pjt_point_2d
    from . import pjt_point_3d as _pjt_point_3d
    from ..global_db import wire_marker as _wire_marker
    from . import pjt_wire as _pjt_wire


class PJTWireMarkersTable(PJTTableBase):
    __table_name__ = 'pjt_wire_markers'

    def __iter__(self) -> _Iterable["PJTWireMarker"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTWireMarker(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTWireMarker":
        if isinstance(item, int):
            if item in self:
                return PJTWireMarker(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, point_2d_id: int, point_3d_id: int,
               wire_id: int, part_id: int, label: str) -> "PJTWireMarker":

        db_id = PJTTableBase.insert(self, point_2d_id=point_2d_id, point_3d_id=point_3d_id,
                                    wire_id=wire_id, part_id=part_id, label=label)

        return PJTWireMarker(self, db_id, self.project_id)


class PJTWireMarker(PJTEntryBase):
    _table: PJTWireMarkersTable = None

    @property
    def table(self) -> PJTWireMarkersTable:
        return self._table

    @property
    def point_2d(self) -> "_pjt_point_2d.PJTPoint2D":
        point_id = self.point_2d
        return self._table.db.pjt_points_2d_table[point_id]

    @property
    def point_2d_id(self) -> int:
        return self._table.select('point_2d_id', id=self._db_id)[0][0]

    @point_2d_id.setter
    def point_2d_id(self, value: int):
        self._table.update(self._db_id, point_2d_id=value)
        self._process_callbacks()

    @property
    def point_3d(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.point_3d
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def point_3d_id(self) -> int:
        return self._table.select('point_3d_id', id=self._db_id)[0][0]

    @point_3d_id.setter
    def point_3d_id(self, value: int):
        self._table.update(self._db_id, point_3d_id=value)
        self._process_callbacks()

    @property
    def wire(self) -> "_pjt_wire.PJTWire":
        wire_id = self.wire_id
        return self._table.db.pjt_wires_table[wire_id]

    @property
    def wire_id(self) -> int:
        return self._table.select('wire_id', id=self._db_id)[0][0]

    @wire_id.setter
    def wire_id(self, value: int):
        self._table.update(self._db_id, wire_id=value)
        self._process_callbacks()

    @property
    def part(self) -> "_wire_marker.WireMarker":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.wire_markers_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)
        self._process_callbacks()

    @property
    def label(self) -> str:
        return self._table.select('label', id=self._db_id)[0][0]

    @label.setter
    def label(self, value: str):
        self._table.update(self._db_id, label=value)
        self._process_callbacks()
