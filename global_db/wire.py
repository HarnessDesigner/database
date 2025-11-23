from typing import Iterable as _Iterable

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
                     ResourceMixin, WeightMixin, ColorMixin, FamilyMixin, MaterialMixin)

from . import color as _color
from . import temperature as _temperature


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

        for (id, part_number, description, mfg, series, weight, material, od_mm,
             shielded, tpi, conductor_dia_mm, num_conductors, size_mm2, size_awg,
             maxtemp, family) in data:

            res[part_number] = (mfg, description, size_mm2, size_awg, num_conductors,
                                series, family, material, od_mm, shielded, tpi, weight,
                                maxtemp, conductor_dia_mm, id)

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
           FamilyMixin, SeriesMixin, ResourceMixin, WeightMixin, ColorMixin, MaterialMixin):

    _table: WiresTable = None

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
    def conductor_dia_mm(self) -> float:
        return self._table.select('conductor_dia_mm', id=self._db_id)[0][0]

    @conductor_dia_mm.setter
    def conductor_dia_mm(self, value: float):
        self._table.update(self._db_id, conductor_dia_mm=value)

    @property
    def num_conductors(self) -> int:
        return self._table.select('num_conductors', id=self._db_id)[0][0]

    @num_conductors.setter
    def num_conductors(self, value: int):
        self._table.update(self._db_id, num_conductors=value)

    @property
    def size_mm2(self) -> float:
        return self._table.select('size_mm2', id=self._db_id)[0][0]

    @size_mm2.setter
    def size_mm2(self, value: float):
        self._table.update(self._db_id, size_mm2=value)

    @property
    def size_awg(self) -> int:
        return self._table.select('size_awg', id=self._db_id)[0][0]

    @size_awg.setter
    def size_awg(self, value: int):
        self._table.update(self._db_id, size_awg=value)

    @property
    def addl_colors(self) -> list[_color.Color]:
        addl_color_ids = self._table.select('addl_color_ids', id=self._db_id)[0][0]
        addl_color_ids = eval(addl_color_ids)

        return [_color.Color(self._table.db.colors_table, db_id) for db_id in addl_color_ids]

    @addl_colors.setter
    def addl_colors(self, value: list[_color.Color]):
        addl_color_ids = [color.db_id for color in value]
        self._table.update(self._db_id, addl_color_ids=addl_color_ids)

    @property
    def max_temp(self) -> _temperature.Temperature:
        max_temp_id = self._table.select('max_temp_id', id=self._db_id)
        return _temperature.Temperature(self, max_temp_id[0][0])

    @max_temp.setter
    def max_temp(self, value: _temperature.Temperature):
        self._table.update(self._db_id, max_temp_id=value.db_id)

    @property
    def max_temp_id(self) -> int:
        return self._table.select('max_temp_id', id=self._db_id)[0][0]

    @max_temp_id.setter
    def max_temp_id(self, value: int):
        self._table.update(self._db_id, max_temp_id=value)
