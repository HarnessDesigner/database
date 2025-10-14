from typing import Iterable as _Iterable, TYPE_CHECKING

from ... import EntryBase, TableBase

from ...mixins import NameMixin

if TYPE_CHECKING:
    from . import layout as _layout


class TransitionBranchesTable(TableBase):
    __table_name__ = 'transition_branches'

    def __iter__(self) -> _Iterable["TransitionBranch"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionBranch(self, db_id)

    def insert(self, tran_map_id: int, idx: int, name: int, x: int, 
               y: int, w: int, h: int, rgb: int) -> "TransitionBranch":
        db_id = TableBase.insert(self, tran_map_id=tran_map_id, idx=idx,
                                 name=name, x=x, y=y, w=w, h=h, rgb=rgb)

        return TransitionBranch(self, db_id)


class TransitionBranch(EntryBase, NameMixin):
    _table: TransitionBranchesTable = None

    @property
    def tran_layout(self) -> "_layout.TransitionLayout":
        from .layout import TransitionLayout

        tran_map_id = self._table.select('tran_map_id', id=self._db_id)
        return TransitionLayout(self._table.db.transition_layouts_table, tran_map_id[0][0])

    @property
    def tran_layout_id(self) -> int:
        return self._table.select('tran_map_id', id=self._db_id)[0][0]

    @property
    def idx(self) -> int:
        return self._table.select('idx', id=self._db_id)[0][0]

    @idx.setter
    def idx(self, value: int):
        self._table.update(self._db_id, idx=value)

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
