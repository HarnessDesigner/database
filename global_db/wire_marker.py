
from typing import Iterable as _Iterable, TYPE_CHECKING
import math

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
                     ResourceMixin, ColorMixin, FamilyMixin, MaterialMixin, TemperatureMixin)

from ...wrappers.decimal import Decimal as _decimal

if TYPE_CHECKING:
    from . import color as _color
    from . import plating as _plating


class WireMarkersTable(TableBase):
    __table_name__: str = 'wire_markers'

    def __iter__(self) -> _Iterable["WireMarker"]:

        for db_id in TableBase.__iter__(self):
            yield WireMarker(self, db_id)

    def __getitem__(self, item) -> "WireMarker":
        if isinstance(item, int):
            if item in self:
                return WireMarker(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return WireMarker(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, image_id: int, datasheet_id: int,
               cad_id: int, color_id: int, min_diameter: _decimal, max_diameter: _decimal, length: _decimal) -> "WireMarker":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 image_id=image_id, datasheet_id=datasheet_id, cad_id=cad_id,
                                 color_id=color_id, min_diameter=float(min_diameter),
                                 max_diameter=float(max_diameter), length=float(length))

        return WireMarker(self, db_id)

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


class WireMarker(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin,
                 ColorMixin, ResourceMixin):

    _table: WireMarkersTable = None

    @property
    def weight(self) -> _decimal:
        return _decimal(self._table.select('weight', id=self._db_id)[0][0])

    @weight.setter
    def weight(self, value: _decimal):
        self._table.update(self._db_id, weight=float(value))

    @property
    def has_label(self) -> bool:
        return bool(self._table.select('has_label', id=self._db_id)[0][0])

    @has_label.setter
    def has_label(self, value: bool):
        self._table.update(self._db_id, has_label=int(value))

    @property
    def min_diameter(self) -> _decimal:
        return _decimal(self._table.select('min_diameter', id=self._db_id)[0][0])

    @min_diameter.setter
    def min_diameter(self, value: _decimal):
        self._table.update(self._db_id, min_diameter=float(value))

    @property
    def max_diameter(self) -> _decimal:
        return _decimal(self._table.select('max_diameter', id=self._db_id)[0][0])

    @max_diameter.setter
    def max_diameter(self, value: _decimal):
        self._table.update(self._db_id, max_diameter=float(value))

    @property
    def length(self) -> _decimal:
        return _decimal(self._table.select('length', id=self._db_id)[0][0])

    @length.setter
    def length(self, value: _decimal):
        self._table.update(self._db_id, length=float(value))
