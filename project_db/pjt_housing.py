from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase
from ...wrappers.decimal import Decimal as _decimal


class PJTHousingsTable(PJTTableBase):
    __table_name__ = 'pjt_housings'

    def __iter__(self) -> _Iterable["PJTHousing"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTHousing(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTHousing":
        if isinstance(item, int):
            if item in self:
                return PJTHousing(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, name: str, coord3d_id: int, coord2d_id: int,
               x_angle_3d: _decimal, y_angle_3d: _decimal, z_angle_3d: _decimal, angle_2d: _decimal,
               seal_ids: list[int], cpa_lock_ids: list[int], tpa_lock_ids: list[int],
               cover_id: int | None, boot_id: int | None, accessory_ids: list[int]) -> "PJTHousing":

        db_id = PJTTableBase.insert(self, part_id=part_id, name=name, coord3d_id=coord3d_id,
                                    coord2d_id=coord2d_id, x_angle_3d=float(x_angle_3d),
                                    y_angle_3d=float(y_angle_3d), z_angle_3d=float(z_angle_3d),
                                    angle_2d=float(angle_2d), seal_ids=seal_ids, cpa_lock_ids=cpa_lock_ids,
                                    tpa_lock_ids=tpa_lock_ids, cover_id=cover_id, boot_id=boot_id,
                                    accessory_ids=accessory_ids)

        return PJTHousing(self, db_id, self.project_id)


class PJTHousing(PJTEntryBase):
    _table: PJTHousingsTable = None

    @property
    def cavities(self) -> list["_pjt_cavity.PJTCavity"]:
        cavities = [None] * self.part.count

        cavity_ids = self._table.db.pjt_cavities_table.select(
            'id', cavity_map_id=self._db_id)

        for cavity_id in cavity_ids:
            cavity = _pjt_cavity.PJTCavity(
                self._table.db.pjt_cavities_table, cavity_id[0], self.project_id)

            cavities[cavity.part.idx] = cavity

        return cavities

    def add_cavity(self, index, name):
        cavities = self.cavities
        assert cavities[index] is None, 'Sanity Check'

        part = self.part
        cavity_part = part.cavities[index]

        if name is None:
            name = cavity_part.name

        cavity = self._table.db.pjt_cavities_table.insert(
            part_id=cavity_part.db_id, cavity_map_id=self._db_id,
            name=name, terminal_id=None)

        return cavity

    @property
    def point3d(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.coord3d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def coord3d_id(self) -> int:
        return self._table.select('coord3d_id', id=self._db_id)[0][0]

    @coord3d_id.setter
    def coord3d_id(self, value: int):
        self._table.update(self._db_id, coord3d_id=value)

    @property
    def x_angle_3d(self) -> _decimal:
        return _decimal(self._table.select('x_angle_3d', id=self._db_id)[0][0])

    @x_angle_3d.setter
    def x_angle_3d(self, value: _decimal):
        self._table.update(self._db_id, x_angle_3d=float(value))

    @property
    def y_angle_3d(self) -> _decimal:
        return _decimal(self._table.select('y_angle_3d', id=self._db_id)[0][0])

    @y_angle_3d.setter
    def y_angle_3d(self, value: _decimal):
        self._table.update(self._db_id, y_angle_3d=float(value))

    @property
    def z_angle_3d(self) -> _decimal:
        return _decimal(self._table.select('z_angle_3d', id=self._db_id)[0][0])

    @z_angle_3d.setter
    def z_angle_3d(self, value: _decimal):
        self._table.update(self._db_id, z_angle_3d=float(value))

    @property
    def angle_2d(self) -> _decimal:
        return _decimal(self._table.select('angle_2d', id=self._db_id)[0][0])

    @angle_2d.setter
    def angle_2d(self, value: _decimal):
        self._table.update(self._db_id, angle_2d=float(value))

    @property
    def point2d(self) -> "_pjt_coordinate_2d.PJTCoordinate2D":
        coord_id = self.coord2d_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_2d_table[coord_id]

    @property
    def coord2d_id(self) -> int:
        return self._table.select('coord2d_id', id=self._db_id)[0][0]

    @coord2d_id.setter
    def coord2d_id(self, value: int):
        self._table.update(self._db_id, coord2d_id=value)

    @property
    def seals(self) -> list["_seal.Seal"]:
        seal_ids = self.seal_ids

        res = []
        for seal_id in seal_ids:
            seal = self._table.db.global_db.seals_table[seal_id]
            if seal is not None:
                res.append(seal)
        return res

    @property
    def seal_ids(self) -> list[int]:
        return eval(self._table.select('seal_ids', id=self._db_id)[0][0])

    @seal_ids.setter
    def seal_ids(self, value: list[int]):
        self._table.update(self._db_id, seal_ids=str(value))

    @property
    def cpa_locks(self) -> list["_cpa_lock.CPALock"]:
        cpa_lock_ids = self.cpa_lock_ids

        res = []
        for cpa_lock_id in cpa_lock_ids:
            cpa_lock = self._table.db.global_db.cpa_locks_table[cpa_lock_id]
            if cpa_lock is not None:
                res.append(cpa_lock)
        return res

    @property
    def cpa_lock_ids(self) -> list[int]:
        return eval(self._table.select('cpa_lock_ids', id=self._db_id)[0][0])

    @cpa_lock_ids.setter
    def cpa_lock_ids(self, value: list[int]):
        self._table.update(self._db_id, cpa_lock_ids=str(value))

    @property
    def tpa_locks(self) -> list["_tpa_lock.TPALock"]:
        tpa_lock_ids = self.tpa_lock_ids

        res = []
        for tpa_lock_id in tpa_lock_ids:
            tpa_lock = self._table.db.global_db.tpa_locks_table[tpa_lock_id]
            if tpa_lock is not None:
                res.append(tpa_lock)
        return res

    @property
    def tpa_lock_ids(self) -> list[int]:
        return eval(self._table.select('tpa_lock_ids', id=self._db_id)[0][0])

    @tpa_lock_ids.setter
    def tpa_lock_ids(self, value: list[int]):
        self._table.update(self._db_id, tpa_lock_ids=str(value))

    @property
    def cover(self) -> "_cover.Cover":
        cover_id = self.cover_id
        if cover_id is None:
            return None

        return self._table.db.global_db.covers_table[cover_id]

    @property
    def cover_id(self) -> int:
        return self._table.select('cover_id', id=self._db_id)[0][0]

    @cover_id.setter
    def cover_id(self, value: int):
        self._table.update(self._db_id, cover_id=value)

    @property
    def boot(self) -> "_boot.Boot":
        boot_id = self.boot_id
        if boot_id is None:
            return None

        return self._table.db.global_db.boots_table[boot_id]

    @property
    def boot_id(self) -> int:
        return self._table.select('boot_id', id=self._db_id)[0][0]

    @boot_id.setter
    def boot_id(self, value: int):
        self._table.update(self._db_id, boot_id=value)

    @property
    def accessories(self) -> list["_accessory.Accessory"]:
        accessory_ids = self.accessory_ids

        res = []
        for accessory_id in accessory_ids:
            accessory = self._table.db.global_db.accessories_table[accessory_id]
            if accessory is not None:
                res.append(accessory)

        return res

    @property
    def accessory_ids(self) -> list[int]:
        return eval(self._table.select('accessory_ids', id=self._db_id)[0][0])

    @accessory_ids.setter
    def accessory_ids(self, value: list[int]):
        self._table.update(self._db_id, accessory_ids=str(value))

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)

    @property
    def part(self) -> "_housing.Housing":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.housings_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d  # NOQA
from . import pjt_coordinate_2d as _pjt_coordinate_2d  # NOQA
from . import pjt_cavity as _pjt_cavity  # NOQA


from ..global_db import housing as _housing  # NOQA
from ..global_db import cover as _cover  # NOQA
from ..global_db import tpa_lock as _tpa_lock  # NOQA
from ..global_db import cpa_lock as _cpa_lock  # NOQA
from ..global_db import seal as _seal  # NOQA
from ..global_db import boot as _boot  # NOQA
from ..global_db import accessory as _accessory  # NOQA



