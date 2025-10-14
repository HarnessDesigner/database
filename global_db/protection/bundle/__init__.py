

from typing import Iterable as _Iterable, TYPE_CHECKING

from ... import EntryBase, TableBase
from ...mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, 
                       ImageMixin, DatasheetMixin, CADMixin, TemperatureMixin, ColorMixin)

if TYPE_CHECKING:
    pass

from ... import temperature as _temperature
from . import series as _series
from . import resistant as _resistant
from . import material as _material
from . import rigidity as _rigidity


class BundleCoversTable(TableBase):
    __table_name__ = 'bundle_covers'

    def __iter__(self) -> _Iterable["BundleCover"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCover(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, series_id: int, image_id: int,
               datasheet_id: int, cad_id: int, min_temp_id: int, max_temp_id: int, color_id: int,
               min_size: float, max_size: float, wall: str, shrink_ratio: str, resistance_values: int,
               material_id: int, rigidity_id: int, shrink_temp_id: int) -> "BundleCover":
        
        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description, 
                                 series_id=series_id, image_id=image_id, datasheet_id=datasheet_id, 
                                 cad_id=cad_id, min_temp_id=min_temp_id, max_temp_id=max_temp_id,
                                 color_id=color_id, min_size=min_size, max_size=max_size, wall=wall,
                                 shrink_ratio=shrink_ratio, resistance_values=resistance_values,
                                 material_id=material_id, rigidity_id=rigidity_id, shrink_temp_id=shrink_temp_id)

        return BundleCover(self, db_id)


class BundleCover(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, 
                  ImageMixin, DatasheetMixin, CADMixin, TemperatureMixin, ColorMixin):
    
    _table: BundleCoversTable = None
    
    @property
    def series(self) -> _series.BundleCoverSeries:
        series_id = self._table.select('series_id', id=self._db_id)
        return _series.BundleCoverSeries(self._table.db.bundle_cover_series_table, series_id[0][0])

    @series.setter
    def series(self, value: _series.BundleCoverSeries):
        self._table.update(self._db_id, series_id=value.db_id)

    @property
    def series_id(self) -> int:
        return self._table.select('series_id', id=self._db_id)[0][0]

    @series_id.setter
    def series_id(self, value: int):
        self._table.update(self._db_id, series_id=value)

    @property
    def material(self) -> _material.BundleCoverMaterial:
        material_id = self._table.select('material_id', id=self._db_id)
        return _material.BundleCoverMaterial(self._table.db.bundle_cover_resistances_table, material_id[0][0])

    @material.setter
    def material(self, value: _material.BundleCoverMaterial):
        self._table.update(self._db_id, material_id=value.db_id)

    @property
    def material_id(self) -> int:
        return self._table.select('material_id', id=self._db_id)[0][0]

    @material_id.setter
    def material_id(self, value: int):
        self._table.update(self._db_id, material_id=value)
    
    @property
    def rigidity(self) -> _rigidity.BundleCoverRigidity:
        rigidity_id = self._table.select('rigidity_id', id=self._db_id)
        return _rigidity.BundleCoverRigidity(self._table.db.bundle_cover_rigidities_table, rigidity_id[0][0])

    @rigidity.setter
    def rigidity(self, value: _rigidity.BundleCoverRigidity):
        self._table.update(self._db_id, material_id=value.db_id)

    @property
    def rigidity_id(self) -> int:
        return self._table.select('rigidity_id', id=self._db_id)[0][0]

    @rigidity_id.setter
    def rigidity_id(self, value: int):
        self._table.update(self._db_id, rigidity_id=value)

    @property
    def shrink_temp(self) -> _temperature.Temperature:
        shrink_temp_id = self._table.select('shrink_temp_id', id=self._db_id)
        return _temperature.Temperature(self._table.db.temperatures_table, shrink_temp_id[0][0])

    @shrink_temp.setter
    def shrink_temp(self, value: _temperature.Temperature):
        self._table.update(self._db_id, shrink_temp_id=value.db_id)

    @property
    def shrink_temp_id(self) -> int:
        return self._table.select('shrink_temp_id', id=self._db_id)[0][0]

    @shrink_temp_id.setter
    def shrink_temp_id(self, value: int):
        self._table.update(self._db_id, shrink_temp_id=value)

    @property
    def resistances(self) -> dict:
        res = {}
        values = self._table.select('resistance_values', id=self._db_id)[0][0]
        for resistance in self._table.db.bundle_cover_resistances_table:
            res[resistance.name] = bool(values & resistance.value)
        
        return res

    @resistances.setter
    def resistances(self, value: dict):
        values = 0
        
        for resistance in self._table.db.bundle_cover_resistances_table:
            if resistance.name in value:
                if value[resistance.name]:
                    values |= resistance.value
                            
        self._table.update(self._db_id, resistance_values=values)
    
    @property
    def shrink_ratio(self) -> str:
        return self._table.select('shrink_ratio', id=self._db_id)[0][0]

    @shrink_ratio.setter
    def shrink_ratio(self, value: str):
        self._table.update(self._db_id, shrink_ratio=value)

    @property
    def wall(self) -> str:
        return self._table.select('wall', id=self._db_id)[0][0]

    @wall.setter
    def wall(self, value: str):
        self._table.update(self._db_id, wall=value)
    
    @property
    def min_size(self) -> float:
        return self._table.select('min_size', id=self._db_id)[0][0]

    @min_size.setter
    def min_size(self, value: float):
        self._table.update(self._db_id, min_size=value)
        
    @property
    def max_size(self) -> float:
        return self._table.select('max_size', id=self._db_id)[0][0]

    @max_size.setter
    def max_size(self, value: float):
        self._table.update(self._db_id, max_size=value)
    
    