from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_point2d as _pjt_point2d
    from . import pjt_point3d as _pjt_point3d


class PJTNotesTable(PJTTableBase):
    __table_name__ = 'pjt_notes'

    def __iter__(self) -> _Iterable["PJTNote"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTNote(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTNote":
        if isinstance(item, int):
            if item in self:
                return PJTNote(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, point2d_id: int | None, point3d_id: int | None,
               note: str, size: int) -> "PJTNote":

        db_id = PJTTableBase.insert(self, point2d_id=point2d_id,
                                    point3d_id=point3d_id, note=note, size=size)

        return PJTNote(self, db_id, self.project_id)


class PJTNote(PJTEntryBase):
    _table: PJTNotesTable = None

    @property
    def table(self) -> PJTNotesTable:
        return self._table

    @property
    def point2d(self) -> "_pjt_point2d.PJTPoint2D":
        db_id = self.point2d_id
        if db_id is None:
            return None

        return self._table.db.pjt_points2d_table[db_id]

    @property
    def point2d_id(self) -> int:
        return self._table.select('point2d_id', id=self._db_id)[0][0]

    @point2d_id.setter
    def point2d_id(self, value: int):
        self._table.update(self._db_id, point2d_id=value)
        self._process_callbacks()

    @property
    def point3d(self) -> "_pjt_point3d.PJTPoint3D":
        db_id = self.point3d_id
        if db_id is None:
            return None

        return self._table.db.pjt_points3d_table[db_id]

    @property
    def point3d_id(self) -> int:
        return self._table.select('point3d_id', id=self._db_id)[0][0]

    @point3d_id.setter
    def point3d_id(self, value: int):
        self._table.update(self._db_id, point3d_id=value)
        self._process_callbacks()

    @property
    def size(self) -> int:
        return self._table.select('size', id=self._db_id)[0][0]

    @size.setter
    def size(self, value: int):
        self._table.update(self._db_id, size=value)
        self._process_callbacks()

    @property
    def note(self) -> str:
        return self._table.select('note', id=self._db_id)[0][0]

    @size.setter
    def size(self, value: str):
        self._table.update(self._db_id, note=value)
        self._process_callbacks()
