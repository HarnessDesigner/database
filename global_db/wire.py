from typing import Iterable as _Iterable, TYPE_CHECKING
import math

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
                     ResourceMixin, ColorMixin, FamilyMixin, MaterialMixin, TemperatureMixin)

from ...wrappers.decimal import Decimal as _decimal

if TYPE_CHECKING:
    from . import color as _color
    from . import plating as _plating


class WiresTable(TableBase):
    __table_name__: str = 'wires'

    def __iter__(self) -> _Iterable["Wire"]:

        for db_id in TableBase.__iter__(self):
            yield Wire(self, db_id)

    def __getitem__(self, item) -> "Wire":
        if isinstance(item, int):
            if item in self:
                return Wire(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Wire(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int, series_id: int,
               image_id: int, datasheet_id: int, cad_id: int, color_id: int, addl_color_ids: list,
               material_id: int, num_conductors: int, shielded: bool, tpi: int, conductor_dia_mm: float,
               size_mm2: float, size_awg: int, od_mm: float, max_temp_id: int, weight: float) -> "Wire":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, color_id=color_id,
                                 addl_color_ids=str(addl_color_ids), material_id=material_id,
                                 num_conductors=num_conductors, shielded=int(shielded), tpi=tpi,
                                 conductor_dia_mm=conductor_dia_mm, size_mm2=size_mm2, size_awg=size_awg,
                                 od_mm=od_mm, max_temp_id=max_temp_id, weight=weight)

        return Wire(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        series = self.get_unique('series_id', 'series')
        families = self.get_unique('family_id', 'families')
        colors = self.get_unique('color_id', 'colors')
        min_temps = self.get_unique('min_temp_id', 'temperatures')
        max_temps = self.get_unique('max_temp_id', 'temperatures')
        stripe_colors = self.get_unique('stripe_color_id', 'colors')
        materials = self.get_unique('material_id', 'materials')
        num_conductors = self.get_unique('num_conductors')
        shieldeds = self.get_unique('shielded')
        tpis = self.get_unique('tpi')
        conductor_dia_mms = self.get_unique('conductor_dia_mm')
        size_mm2s = self.get_unique('size_mm2')
        size_awgs = self.get_unique('size_awg')
        od_mms = self.get_unique('od_mm')
        weight_1kms = self.get_unique('weight_1km')
        core_materials = self.get_unique('core_material_id', 'platings')
        resistance_1kms = self.get_unique('resistance_1km')
        volts = self.get_unique('volts')

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
            'Stripe Color': {
                'field': 'stripe_color_id',
                'type': 'is',
                'values': stripe_colors
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
            'Weight (1km)': {
                'field': 'weight_1km',
                'type': 'float',
                'values': weight_1kms
            },
            'Core Material': {
                'field': 'core_material_id',
                'type': 'id',
                'values': core_materials
            },
            'Size (mm2)': {
                'field': 'size_mm2',
                'type': 'float',
                'values': size_mm2s
            },
            'Size (AWG)': {
                'field': 'size_awg',
                'type': 'int',
                'values': size_awgs
            },
            'Conductor Count': {
                'field': 'num_conductors',
                'type': 'int',
                'values': num_conductors
            },
            'Shielded': {
                'field': 'shielded',
                'type': 'int',
                'values': shieldeds
            },
            'Turns Per Inch': {
                'field': 'tpi',
                'type': 'int',
                'values': tpis
            },
            'Conductor Diameter': {
                'field': 'conductor_dia_mm',
                'type': 'float',
                'values': conductor_dia_mms
            },
            'Outside Diameter': {
                'field': 'od_mm',
                'type': 'float',
                'values': od_mms
            },
            'Resistance (1km)': {
                'field': 'resistance_1km',
                'type': 'float',
                'values': resistance_1kms
            },
            'Volts': {
                'field': 'volts',
                'type': 'float',
                'values': volts
            }
        }

        return ret

    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Size (mm2)',
            'Size (AWG)',
            'Conductor Count',
            'Series',
            'Family',
            'Material',
            'Outside Diameter',
            'Shielded',
            'TPI',
            'Weight',
            'Max Temperature',
            'Conductor Diameter'
        ]

    def parts_list(self):
        cmd = (
            'SELECT wire.id, wire.part_number, wire.description,',
            'manufacturer.name, series.name, wire.weight, material.name,',
            'wire.od_mm, wire.shielded, wire.tpi, wire.conductor_dia_mm,',
            'wire.num_conductors, wire.size_mm2, wire.size_awg, maxtemp.name,',
            'family.name FROM wires wire',
            'INNER JOIN manufacturers manufacturer ON transition.mfg_id = manufacturer.id',
            'INNER JOIN families family ON wire.family_id = family.id',
            'INNER JOIN materials material ON wire.material_id = material.id',
            'INNER JOIN temperatures maxtemp ON wire.max_temp_id = maxtemp.id',
            'INNER JOIN series series ON wire.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Material': dict(),
            'Outside Diameter': dict(),
            'Shielded': dict(),
            'TPI': dict(),
            'Conductor Count': dict(),
            'Size (mm2)': dict(),
            'Size (AWG)': dict(),
            'Series': dict(),
            'Family': dict()
        }

        res = {}

        for (db_id, part_number, description, mfg, series, weight, material, od_mm,
             shielded, tpi, conductor_dia_mm, num_conductors, size_mm2, size_awg,
             maxtemp, family) in data:

            res[part_number] = (mfg, description, size_mm2, size_awg, num_conductors,
                                series, family, material, od_mm, shielded, tpi, weight,
                                maxtemp, conductor_dia_mm, db_id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            if material not in commons['Material']:
                commons['Material'][material] = []

            commons['Material'][material].append(part_number)

            if od_mm not in commons['Outside Diameter']:
                commons['Outside Diameter'][od_mm] = []

            commons['Outside Diameter'][od_mm].append(part_number)

            shielded = 'Yes' if shielded else 'No'

            if shielded not in commons['Shielded']:
                commons['Shielded'][shielded] = []

            commons['Shielded'][shielded].append(part_number)

            if tpi not in commons['TPI']:
                commons['TPI'][tpi] = []

            commons['TPI'][tpi].append(part_number)

            if size_mm2 not in commons['Size (mm2)']:
                commons['Size (mm2)'][size_mm2] = []

            commons['Size (mm2)'][size_mm2].append(part_number)

            if size_awg not in commons['Size (AWG)']:
                commons['Size (AWG)'][size_awg] = []

            commons['Size (AWG)'][size_awg].append(part_number)

            if num_conductors not in commons['Conductor Count']:
                commons['Conductor Count'][num_conductors] = []

            commons['Conductor Count'][num_conductors].append(part_number)

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Series'][series].append(part_number)

            if family not in commons['Family']:
                commons['Family'][family] = []

            commons['Family'][family].append(part_number)

        return res, commons


class Wire(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin,
           FamilyMixin, SeriesMixin, ResourceMixin, ColorMixin, MaterialMixin,
           TemperatureMixin):

    _table: WiresTable = None

    @property
    def resistance_1km(self) -> _decimal:
        resistance = _decimal(self._table.select('resistance_1km', id=self._db_id)[0][0])
        return resistance

    @resistance_1km.setter
    def resistance_1km(self, value: _decimal):
        self._table.update(self._db_id, resistance_1km=float(value))

    @property
    def resistance_1kft(self) -> _decimal:
        return self.resistance_ft * _decimal(1000)

    @resistance_1kft.setter
    def resistance_1kft(self, value: _decimal):
        self.resistance_ft = value / _decimal(1000)

    @property
    def resistance_m(self) -> _decimal:
        resistance = self.resistance_1km
        return resistance / _decimal(1000)

    @resistance_m.setter
    def resistance_m(self, value: _decimal):
        value *= _decimal(1000)
        self.resistance_1km = value

    @property
    def resistance_ft(self) -> _decimal:
        resistance = self.resistance_m
        return resistance * _decimal(3.28084)

    @resistance_ft.setter
    def resistance_ft(self, value: _decimal):
        value /= _decimal(3.28084)
        self.resistance_m = value

    @property
    def weight_1km(self) -> _decimal:
        weight = _decimal(self._table.select('weight_1km', id=self._db_id)[0][0])
        return weight

    @weight_1km.setter
    def weight_1km(self, value: _decimal):
        self._table.update(self._db_id, weight_1km=float(value))

    @property
    def weight_1kft(self) -> _decimal:
        return self.weight_lb_ft * _decimal(1000)

    @weight_1kft.setter
    def weight_1kft(self, value: _decimal):
        self.weight_lb_ft = value / _decimal(1000)

    @property
    def weight_g_m(self) -> _decimal:
        weight = self.weight_1km
        return weight / _decimal(1000)

    @weight_g_m.setter
    def weight_g_m(self, value: _decimal):
        value *= _decimal(1000)
        self.weight_1km = value

    @property
    def weight_g_ft(self) -> _decimal:
        weight = self.weight_g_m
        return weight * _decimal(3.28084)

    @weight_g_ft.setter
    def weight_g_ft(self, value: _decimal):
        value /= _decimal(3.28084)
        self.weight_g_m = value

    @property
    def weight_lb_ft(self) -> _decimal:
        weight = self.weight_g_ft
        return weight / _decimal(453.592)

    @weight_lb_ft.setter
    def weight_lb_ft(self, value: _decimal):
        value *= _decimal(453.592)
        self.weight_g_ft = value

    @property
    def od_mm(self) -> float:
        return self._table.select('od_mm', id=self._db_id)[0][0]

    @od_mm.setter
    def od_mm(self, value: float):
        self._table.update(self._db_id, od_mm=value)

    @property
    def shielded(self) -> bool:
        return bool(self._table.select('shielded', id=self._db_id)[0][0])

    @shielded.setter
    def shielded(self, value: bool):
        self._table.update(self._db_id, shielded=int(value))

    @property
    def tpi(self) -> int:
        return self._table.select('tpi', id=self._db_id)[0][0]

    @tpi.setter
    def tpi(self, value: int):
        self._table.update(self._db_id, tpi=value)

    @property
    def num_conductors(self) -> int:
        return self._table.select('num_conductors', id=self._db_id)[0][0]

    @num_conductors.setter
    def num_conductors(self, value: int):
        self._table.update(self._db_id, num_conductors=value)

    @property
    def core_material(self) -> "_plating.Plating":
        db_id = self.core_material_id
        return self._table.db.platings_table[db_id]

    @core_material.setter
    def core_material(self, value: "_plating.Plating"):
        self.core_material_id = value.db_id

    @property
    def core_material_id(self) -> int:
        return self._table.select('core_material_id', id=self._db_id)[0][0]

    @core_material_id.setter
    def core_material_id(self, value: int):
        self._table.update(self._db_id, core_material_id=value)

    @property
    def conductor_dia_mm(self) -> _decimal:
        d_mm = self._table.select('conductor_dia_mm', id=self._db_id)[0][0]

        if d_mm is None:
            d_mm = round(self.conductor_dia_in * _decimal(25.4), 4)
        else:
            d_mm = _decimal(d_mm)

        return d_mm

    @conductor_dia_mm.setter
    def conductor_dia_mm(self, value: _decimal):
        self._table.update(self._db_id, conductor_dia_mm=float(value))

    @property
    def conductor_dia_in(self) -> _decimal:
        d_in = _decimal(0.005) * (_decimal(92) ** ((_decimal(36) - _decimal(self.size_awg)) / _decimal(39)))
        return round(d_in, 4)

    @conductor_dia_in.setter
    def conductor_dia_in(self, value: _decimal):
        self.conductor_dia_mm = value * _decimal(25.4)

    @property
    def size_mm2(self) -> _decimal:
        mm2 = self._table.select('size_mm2', id=self._db_id)[0][0]

        if mm2 is None:
            awg = self.size_awg

            if awg is None:
                d_mm = self.conductor_dia_mm

                if d_mm is None:
                    raise RuntimeError('sanity check')

                return self.__mm_to_mm2(d_mm)

            return self.__awg_to_mm2(awg)

        return _decimal(mm2)

    @size_mm2.setter
    def size_mm2(self, value: _decimal):
        self._table.update(self._db_id, size_mm2=float(value))

    @property
    def size_awg(self) -> int:
        awg = self._table.select('size_awg', id=self._db_id)[0][0]

        if awg is None:
            mm2 = self.size_mm2

            if mm2 is None:
                dia_mm = self.conductor_dia_mm

                if dia_mm is None:
                    raise RuntimeError('sanity check')

                return self.__mm_to_awg(dia_mm)

            return self.__mm2_to_awg(mm2)

        return awg

    @size_awg.setter
    def size_awg(self, value: int):
        self._table.update(self._db_id, size_awg=value)

    @staticmethod
    def __awg_to_mm2(awg: int) -> _decimal:
        d_in = _decimal(0.005) * (_decimal(92) ** ((_decimal(36) - _decimal(awg)) / _decimal(39)))
        d_mm = d_in * _decimal(25.4)
        area_mm2 = (_decimal(math.pi) / _decimal(4)) * (d_mm ** _decimal(2))
        return round(area_mm2, 4)

    @staticmethod
    def __mm_to_mm2(d_mm: _decimal) -> _decimal:
        area_mm2 = (_decimal(math.pi) / _decimal(4)) * (d_mm ** _decimal(2))
        return float(round(area_mm2, 4))

    @classmethod
    def __mm_to_awg(cls, d_mm: _decimal) -> int:
        area_mm2 = (_decimal(math.pi) / _decimal(4)) * (d_mm ** _decimal(2))
        return cls.__mm2_to_awg(area_mm2)

    @staticmethod
    def __mm2_to_awg(mm2: _decimal) -> int:
        d_mm = _decimal(2) * _decimal(math.sqrt(mm2 / _decimal(math.pi)))
        d_in = d_mm / _decimal(25.4)
        awg = _decimal(36) - _decimal(39) * _decimal(math.log(float(d_in / _decimal(0.005)), 92))
        return int(round(awg))

    @property
    def size_in2(self) -> _decimal:
        area_mm2 = self.size_mm2
        area_in2 = area_mm2 / _decimal(25.4) / _decimal(25.4)
        return round(area_in2, 4)

    @size_in2.setter
    def size_in2(self, value: _decimal):
        self.size_mm2 = value * _decimal(25.4) * _decimal(25.4)

    @property
    def in2_symbol(self) -> str:
        return 'in²'

    @property
    def mm2_symbol(self) -> str:
        return 'mm²'

    @property
    def stripe_color(self) -> "_color.Color":
        db_id = self.stripe_color_id
        return self._table.db.colors_table[db_id]

    @stripe_color.setter
    def stripe_color(self, value: "_color.Color"):
        self._table.update(self._db_id, stripe_color_id=value.db_id)

    @property
    def stripe_color_id(self) -> int | None:
        return self._table.select('stripe_color_id', id=self._db_id)[0][0]

    @stripe_color_id.setter
    def stripe_color_id(self, value: int | None):
        self._table.update(self._db_id, stripe_color_id=value)

