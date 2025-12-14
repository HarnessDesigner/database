

from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase
from ...wrappers.decimal import Decimal as _decimal
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin,
                     ResourceMixin, TemperatureMixin, ColorMixin, SeriesMixin,
                     MaterialMixin, ProtectionMixin, AdhesiveMixin, WeightMixin)


if TYPE_CHECKING:
    from . import temperature as _temperature


class BundleCoversTable(TableBase):
    __table_name__ = 'bundle_covers'

    def __iter__(self) -> _Iterable["BundleCover"]:
        for db_id in TableBase.__iter__(self):
            yield BundleCover(self, db_id)

    def __getitem__(self, item) -> "BundleCover":
        if isinstance(item, int):
            if item in self:
                return BundleCover(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return BundleCover(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, series_id: int, image_id: int,
               datasheet_id: int, cad_id: int, min_temp_id: int, max_temp_id: int, color_id: int,
               min_size: _decimal, max_size: _decimal, wall: str, shrink_ratio: str, protections: str,
               material_id: int, rigidity: str, shrink_temp_id: int, adhesives: list[str],
               weight: _decimal) -> "BundleCover":
        
        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description, 
                                 series_id=series_id, image_id=image_id, datasheet_id=datasheet_id, 
                                 cad_id=cad_id, min_temp_id=min_temp_id, max_temp_id=max_temp_id,
                                 color_id=color_id, min_size=float(min_size), max_size=float(max_size), wall=wall,
                                 shrink_ratio=shrink_ratio, protections=protections,
                                 material_id=material_id, rigidity=rigidity, shrink_temp_id=shrink_temp_id,
                                 adhesives=f"[{', '.join(adhesives)}]", weight=float(weight))

        return BundleCover(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        series = self.get_unique('series_id', 'series')
        families = self.get_unique('family_id', 'families')
        materials = self.get_unique('material_id', 'materials')
        colors = self.get_unique('color_id', 'colors')
        rigidities = self.get_unique('rigidity')
        shrink_temps = self.get_unique('shrink_temp_id', 'temperatures')
        min_temps = self.get_unique('min_temp_id', 'temperatures')
        max_temps = self.get_unique('max_temp_id', 'temperatures')
        min_diameters = self.get_unique('min_dia')
        max_diameters = self.get_unique('min_dia')
        walls = self.get_unique('wall')
        shrink_ratios = self.get_unique('shrink_ratio')
        protections = self.get_unique('protection_id', 'protections')
        weights = self.get_unique('weight')

        ret = {
            'Manufacturer': {
                'field': 'mfg_id',
                'type': 'id',
                'values': mfgs
            },
            'Family': {
                'field': 'family_id',
                'type': 'id',
                'values': families
            },
            'Series': {
                'field': 'series_id',
                'type': 'id',
                'values': series
            },
            'Rigidity': {
                'field': 'rigidity',
                'type': 'str',
                'values': rigidities
            },
            'Color': {
                'field': 'color_id',
                'type': 'id',
                'values': colors
            },
            'Material': {
                'field': 'material_id',
                'type': 'id',
                'values': materials
            },
            'Min Temp': {
                'field': 'min_temp_id',
                'type': 'id',
                'values': min_temps
            },
            'Max Temp': {
                'field': 'max_temp_id',
                'type': 'id',
                'values': max_temps
            },
            'Weight': {
                'field': 'weight',
                'type': 'float',
                'values': weights
            },
            'Shrink Temp': {
                'field': 'shrink_temp_id',
                'type': 'id',
                'values': shrink_temps
            },
            'Protection': {
                'field': 'protection_id',
                'type': 'id',
                'values': protections
            },
            'Min Diameter': {
                'field': 'min_dia',
                'type': 'float',
                'values': min_diameters
            },

            'Max Diameter': {
                'field': 'max_dia',
                'type': 'float',
                'values': max_diameters
            },
            'Wall Type': {
                'field': 'wall',
                'type': 'str',
                'values': walls
            },
            'Shrink Ratio': {
                'field': 'shrink_ratio',
                'type': 'str',
                'values': shrink_ratios
            },
        }

        return ret

    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Series',
            'Min Dia',
            'Max Dia',
            'Material',
            'Wall',
            'Shrink Ratio',
            'Adhesive',
            'Protection',
            'Rigidity',
            'Shrink Temp',
            'Weight',
            'Min Temp',
            'Max Temp'
        ]

    def parts_list(self):
        cmd = (
            'SELECT bundle_cover.id, bundle_cover.part_number, bundle_cover.description,',
            'manufacturer.name, material.name, series.name, bundle_cover.weight,',
            'mintemp.name, maxtemp.name, adhesive.name, protection.name, bundle_cover.rigidity,',
            'shrinktemp.name, bundle_cover.shrink_ratio, bundle_cover.wall, bundle_cover.min_size,',
            'bundle_cover.max_size FROM bundle_covers bundle_cover',
            'INNER JOIN manufacturers manufacturer ON bundle_cover.mfg_id = manufacturer.id',
            'INNER JOIN materials material ON bundle_cover.material_id = material.id',
            'INNER JOIN temperatures mintemp ON bundle_cover.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON bundle_cover.max_temp_id = maxtemp.id',
            'INNER JOIN adhesives adhesive ON bundle_cover.adhesive_id = ashesive.id',
            'INNER JOIN protections protection ON bundle_cover.protection_id = protection.id',
            'INNER JOIN temperatures shrinktemp ON bundle_cover.shrink_temp_id = shrinktemp.id',
            'INNER JOIN series series ON bundle_cover.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Rigidity': dict(),
            'Shrink Ratio': dict(),
            'Wall Type': dict(),
            'Min Diameter': dict(),
            'Nax Diameter': dict(),
            'Material': dict(),
            'Series': dict(),
            'Min Temp': dict(),
            'Max Temp': dict(),
            'Adhesive': dict(),
            'Protections': dict()
        }

        res = {}

        for (id, part_number, description, mfg, material, series, weight, mintemp, maxtemp,
             adhesive, protection, rigidity, shrinktemp, shrink_ratio, wall, min_size, max_size) in data:

            res[part_number] = (mfg, description, series, min_size, max_size,
                                material, wall, shrink_ratio, adhesive, protection,
                                rigidity, shrinktemp, weight, mintemp, maxtemp, id)

            if rigidity not in commons['Rigidity']:
                commons['Rigidity'][rigidity] = []

            commons['Rigidity'][rigidity].append(part_number)

            if shrink_ratio not in commons['Shrink Ratio']:
                commons['Shrink Ratio'][shrink_ratio] = []

            commons['Shrink Ratio'][shrink_ratio].append(part_number)

            if wall not in commons['Wall Type']:
                commons['Wall Type'][wall] = []

            commons['Wall Type'][wall].append(part_number)

            if min_size not in commons['Min Diameter']:
                commons['Min Diameter'][min_size] = []

            commons['Min Diameter'][min_size].append(part_number)

            if max_size not in commons['Max Diameter']:
                commons['Nax Diameter'][max_size] = []

            commons['Max Diameter'][max_size].append(part_number)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            if material not in commons['Material']:
                commons['Material'][material] = []

            commons['Material'][material].append(part_number)

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Series'][series].append(part_number)

            if mintemp not in commons['Min Temp']:
                commons['Min Temp'][mintemp] = []

            commons['Min Temp'][mintemp].append(part_number)

            if maxtemp not in commons['Max Temp']:
                commons['Max Temp'][maxtemp] = []

            commons['Max Temp'][maxtemp].append(part_number)

            if adhesive not in commons['Adhesive']:
                commons['Adhesive'][adhesive] = []

            commons['Adhesive'][adhesive].append(part_number)

            if protection not in commons['Protections']:
                commons['Protections'][protection] = []

            commons['Protections'][protection].append(part_number)

        return res, commons


class BundleCover(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, 
                  ResourceMixin, TemperatureMixin, ColorMixin, SeriesMixin,
                  MaterialMixin, ProtectionMixin, AdhesiveMixin, WeightMixin):
    
    _table: BundleCoversTable = None

    @property
    def rigidity(self) -> str:
        return self._table.select('rigidity', id=self._db_id)[0][0]

    @rigidity.setter
    def rigidity(self, value: str):
        self._table.update(self._db_id, rigidity=value)

    @property
    def shrink_temp(self) -> "_temperature.Temperature":
        shrink_temp_id = self.shrink_temp_id
        from .temperature import Temperature

        return Temperature(self._table.db.temperatures_table, shrink_temp_id)

    @shrink_temp.setter
    def shrink_temp(self, value: "_temperature.Temperature"):
        self._table.update(self._db_id, shrink_temp_id=value.db_id)

    @property
    def shrink_temp_id(self) -> int:
        return self._table.select('shrink_temp_id', id=self._db_id)[0][0]

    @shrink_temp_id.setter
    def shrink_temp_id(self, value: int):
        self._table.update(self._db_id, shrink_temp_id=value)

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
