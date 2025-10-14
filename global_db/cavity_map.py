from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase
from .mixins import ImageMixin, OverlayMixin

if TYPE_CHECKING:
    from . import housing as _housing
    from . import cavity as _cavity


class CavityMapsTable(TableBase):
    __table_name__ = 'cavity_maps'

    def __iter__(self) -> _Iterable["CavityMap"]:
        for db_id in TableBase.__iter__(self):
            yield CavityMap(self, db_id)

    def insert(self, housing_id: int, overlay_id: int, image_id: int, count: int) -> "CavityMap":
        db_id = TableBase.insert(self, housing_id=housing_id, overlay_id=overlay_id,
                                 image_id=image_id, count=count)

        return CavityMap(self, db_id)


class CavityMap(EntryBase, ImageMixin, OverlayMixin):

    _table: CavityMapsTable = None

    @property
    def housing(self) -> "_housing.Housing":
        from .housing import Housing

        housing_id = self._table.select('housing_id', id=self._db_id)
        return Housing(self._table.db.housings_table, housing_id[0][0])

    @property
    def housing_id(self) -> int:
        return self._table.select('housing_id', id=self._db_id)[0][0]

    @property
    def count(self) -> int:
        return self._table.select('count', id=self._db_id)[0][0]

    @count.setter
    def count(self, value: int):
        self._table.update(self._db_id, count=value)

    @property
    def cavities(self) -> list["_cavity.Cavity"]:
        from .cavity import Cavity
        res = []

        cavity_ids = self._table.db.cavities_table.select('id', cavity_map_id=self._db_id)
        for db_id in cavity_ids:
            res.append(Cavity(self._table.db.cavities_table, db_id[0]))

        return res
