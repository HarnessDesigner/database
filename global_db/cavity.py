from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase

from .mixins import NameMixin

if TYPE_CHECKING:
    from . import cavity_map as _cavity_map


class CavitiesTable(TableBase):
    __table_name__ = 'cavities'

    def __iter__(self) -> _Iterable["Cavity"]:
        for db_id in TableBase.__iter__(self):
            yield Cavity(self, db_id)

    def insert(self, cavity_map_id: int, idx: int, name: int, size: float, x: int, 
               y: int, w: int, h: int, rgb: int) -> "Cavity":
        db_id = TableBase.insert(self, cavity_map_id=cavity_map_id, idx=idx,
                                 name=name, size=size, x=x, y=y, w=w, h=h, rgb=rgb)

        return Cavity(self, db_id)


class Cavity(EntryBase, NameMixin):
    _table: CavitiesTable = None

    @property
    def cavity_map(self) -> "_cavity_map.CavityMap":
        from .cavity_map import CavityMap
        cavity_map_id = self._table.select('cavity_map_id', id=self._db_id)
        return CavityMap(self._table.db.cavity_maps_table, cavity_map_id[0][0])

    @property
    def cavity_map_id(self) -> int:
        return self._table.select('cavity_map_id', id=self._db_id)[0][0]
        
    @property
    def idx(self) -> int:
        return self._table.select('idx', id=self._db_id)[0][0]

    @idx.setter
    def idx(self, value: int):
        self._table.update(self._db_id, idx=value)
    
    @property
    def size(self) -> float:
        return self._table.select('size', id=self._db_id)[0][0]

    @size.setter
    def size(self, value: float):
        self._table.update(self._db_id, size=value)

    @property
    def x(self) -> int:
        return self._table.select('x', id=self._db_id)[0][0]

    @x.setter
    def x(self, value: int):
        self._table.update(self._db_id, x=value)

    @property
    def y(self) -> int:
        return self._table.select('y', id=self._db_id)[0][0]

    @y.setter
    def y(self, value: int):
        self._table.update(self._db_id, y=value)

    @property
    def width(self) -> int:
        return self._table.select('w', id=self._db_id)[0][0]

    @width.setter
    def width(self, value: int):
        self._table.update(self._db_id, w=value)

    @property
    def height(self) -> int:
        return self._table.select('h', id=self._db_id)[0][0]

    @height.setter
    def height(self, value: int):
        self._table.update(self._db_id, h=value)

    @property
    def rgb(self) -> tuple[int, int, int, int]:
        rgb = self._table.select('rgb', id=self._db_id)[0][0]
        
        r = rgb >> 16
        g = rgb >> 8 & 0xFF
        b = rgb & 0xFF
        
        return r, g, b, 255

    @rgb.setter
    def rgb(self, value: tuple[int, int, int, int]):
        r, g, b = value[:3]
        
        rgb = r << 16 | g << 8 | b
        self._table.update(self._db_id, rgb=rgb)

