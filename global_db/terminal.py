from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase
from ...wrappers.decimal import Decimal as _decimal
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, GenderMixin,
                     SeriesMixin, FamilyMixin, ResourceMixin, WeightMixin, CavityLockMixin,
                     Model3DMixin, DimensionMixin)

if TYPE_CHECKING:
    from . import plating as _plating


class TerminalsTable(TableBase):
    __table_name__: str = 'terminals'

    def __iter__(self) -> _Iterable["Terminal"]:
        for db_id in TableBase.__iter__(self):
            yield Terminal(self, db_id)

    def __getitem__(self, item) -> "Terminal":
        if isinstance(item, int):
            if item in self:
                return Terminal(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Terminal(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, gender_id: int,
               series_id: int, family_id: int, sealing: bool, cavity_lock_id: int,
               image_id: int, datasheet_id: int, cad_id: int, material_id: int,
               blade_size: _decimal, resistance_mohms: int, mating_cycles: int,
               max_vibration_g: int, max_current_ma: int, wire_size_min_awg: int,
               wire_size_max_awg: int, wire_dia_min: _decimal, wire_dia_max: _decimal,
               min_wire_cross: _decimal, max_wire_cross: _decimal, plating_id: int,
               weight: _decimal, length: _decimal, width, _decimal, height: _decimal) -> "Terminal":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 gender_id=gender_id, series_id=series_id, family_id=family_id, sealing=int(sealing),
                                 cavity_lock_id=cavity_lock_id, image_id=image_id, datasheet_id=datasheet_id,
                                 cad_id=cad_id, material_id=material_id, blade_size=float(blade_size),
                                 resistance_mohms=resistance_mohms, mating_cycles=mating_cycles,
                                 max_vibration_g=max_vibration_g, max_current_ma=max_current_ma,
                                 wire_size_min_awg=wire_size_min_awg, wire_size_max_awg=wire_size_max_awg,
                                 wire_dia_min=float(wire_dia_min), wire_dia_max=float(wire_dia_max),
                                 min_wire_cross=float(min_wire_cross), max_wire_cross=float(max_wire_cross),
                                 plating_id=plating_id, weight=float(weight), length=float(length), width=float(width),
                                 height=float(height))

        return Terminal(self, db_id)

    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Series',
            'Family',
            'Gender',
            'Blade Size',
            'Sealing',
            'Max Current (ma)',
            'Plating',
            'Min Wire Size (mm2)',
            'Max Wire Size (mm2)',
            'Min Wire Size (AWG)',
            'Max Wire Size (AWG)',
            'Min Wire Size (mm)',
            'Max Wire Size (mm)',
            'Weight'
        ]

    def parts_list(self):
        cmd = (
            'SELECT terminal.id, terminal.part_number, terminal.description,',
            'manufacturer.name, series.name, terminal.weight, terminal.sealing,',
            'terminal.blade_size, terminal.max_current_ma, gender.name,',
            'plating.symbol, terminal.min_wire_cross, terminal.max_wire_cross,',
            'terminal.wire_size_min_awg, terminal.wire_size_max_awg, terminal.wire_dia_min,',
            'terminal.wire_dia_max, family.name FROM terminals terminal',
            'INNER JOIN manufacturers manufacturer ON terminal.mfg_id = manufacturer.id',
            'INNER JOIN families family ON terminal.family_id = family.id',
            'INNER JOIN genders gender ON terminal.gender_id = gender.id',
            'INNER JOIN platings plating ON terminal.plating_id = plating.id',
            'INNER JOIN series series ON terminal.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Sealing': dict(),
            'Blade Size': dict(),
            'Max Current (ma)': dict(),
            'Gender': dict(),
            'Plating': dict(),
            'Min Wire Size (mm2)': dict(),
            'Max Wire Size (mm2)': dict(),
            'Min Wire Size (AWG)': dict(),
            'Max Wire Size (AWG)': dict(),
            'Min Wire Size (mm)': dict(),
            'Max Wire Size (mm)': dict(),
            'Series': dict(),
            'Family': dict()
        }

        res = {}

        for (id, part_number, description, mfg, series,
             weight, sealing, blade_size, max_current_ma, gender,
             plating, min_wire_cross, max_wire_cross, wire_size_min_awg,
             wire_size_max_awg, wire_dia_min, wire_dia_max, family) in data:

            res[part_number] = (mfg, description, series, family, gender, blade_size,
                                sealing, max_current_ma, plating, min_wire_cross,
                                max_wire_cross, wire_size_min_awg, wire_size_max_awg,
                                wire_dia_min, wire_dia_max, weight, id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            sealing = 'Yes' if sealing else 'No'

            if sealing not in commons['Sealing']:
                commons['Sealing'][sealing] = []

            commons['Sealing'][sealing].append(part_number)

            if blade_size not in commons['Blade Size']:
                commons['Blade Size'][blade_size] = []

            commons['Blade Size'][blade_size].append(part_number)

            if max_current_ma not in commons['Max Current (ma)']:
                commons['Max Current (ma)'][max_current_ma] = []

            commons['Max Current (ma)'][max_current_ma].append(part_number)

            if gender not in commons['Gender']:
                commons['Gender'][gender] = []

            commons['Gender'][gender].append(part_number)

            if plating not in commons['Plating']:
                commons['Plating'][plating] = []

            commons['Plating'][plating].append(part_number)

            if min_wire_cross not in commons['Min Wire Size (mm2)']:
                commons['Min Wire Size (mm2)'][min_wire_cross] = []

            commons['Min Wire Size (mm2)'][min_wire_cross].append(part_number)

            if max_wire_cross not in commons['Max Wire Size (mm2)']:
                commons['Max Wire Size (mm2)'][max_wire_cross] = []

            commons['Max Wire Size (mm2)'][max_wire_cross].append(part_number)

            if wire_size_min_awg not in commons['Min Wire Size (AWG)']:
                commons['Min Wire Size (AWG)'][wire_size_min_awg] = []

            commons['Min Wire Size (AWG)'][wire_size_min_awg].append(part_number)

            if wire_size_max_awg not in commons['Max Wire Size (AWG)']:
                commons['Max Wire Size (AWG)'][wire_size_max_awg] = []

            commons['Max Wire Size (AWG)'][wire_size_max_awg].append(part_number)

            if wire_dia_min not in commons['Min Wire Size (mm)']:
                commons['Min Wire Size (mm)'][wire_dia_min] = []

            commons['Min Wire Size (mm)'][wire_dia_min].append(part_number)

            if wire_dia_max not in commons['Max Wire Size (mm)']:
                commons['Max Wire Size (mm)'][wire_dia_max] = []

            commons['Max Wire Size (mm)'][wire_dia_max].append(part_number)

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Series'][series].append(part_number)

            if family not in commons['Family']:
                commons['Family'][family] = []

            commons['Family'][family].append(part_number)

        return res, commons


class Terminal(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin,
               GenderMixin, DimensionMixin, SeriesMixin, FamilyMixin, ResourceMixin,
               WeightMixin, CavityLockMixin, Model3DMixin):

    _table: TerminalsTable = None

    @property
    def sealing(self) -> bool:
        return bool(self._table.select('sealing', id=self._db_id)[0][0])

    @sealing.setter
    def sealing(self, value: bool):
        self._table.update(self._db_id, size=int(value))

    @property
    def blade_size(self) -> _decimal:
        return _decimal(self._table.select('blade_size', id=self._db_id)[0][0])

    @blade_size.setter
    def blade_size(self, value: _decimal):
        self._table.update(self._db_id, blade_size=float(value))

    @property
    def resistance_mohms(self) -> int:
        return self._table.select('resistance_mohms', id=self._db_id)[0][0]

    @resistance_mohms.setter
    def resistance_mohms(self, value: int):
        self._table.update(self._db_id, resistance_mohms=value)

    @property
    def mating_cycles(self) -> int:
        return self._table.select('mating_cycles', id=self._db_id)[0][0]

    @mating_cycles.setter
    def mating_cycles(self, value: int):
        self._table.update(self._db_id, mating_cycles=value)

    @property
    def max_vibration_g(self) -> int:
        return self._table.select('max_vibration_g', id=self._db_id)[0][0]

    @max_vibration_g.setter
    def max_vibration_g(self, value: int):
        self._table.update(self._db_id, max_vibration_g=value)

    @property
    def max_current_ma(self) -> int:
        return self._table.select('max_current_ma', id=self._db_id)[0][0]

    @max_current_ma.setter
    def max_current_ma(self, value: int):
        self._table.update(self._db_id, max_current_ma=value)

    @property
    def wire_size_min_awg(self) -> int:
        return self._table.select('wire_size_min_awg', id=self._db_id)[0][0]

    @wire_size_min_awg.setter
    def wire_size_min_awg(self, value: int):
        self._table.update(self._db_id, wire_size_min_awg=value)

    @property
    def wire_size_max_awg(self) -> int:
        return self._table.select('wire_size_max_awg', id=self._db_id)[0][0]

    @wire_size_max_awg.setter
    def wire_size_max_awg(self, value: int):
        self._table.update(self._db_id, wire_size_max_awg=value)

    @property
    def wire_dia_min(self) -> _decimal:
        return _decimal(self._table.select('wire_dia_min', id=self._db_id)[0][0])

    @wire_dia_min.setter
    def wire_dia_min(self, value: _decimal):
        self._table.update(self._db_id, wire_dia_min=float(value))

    @property
    def wire_dia_max(self) -> _decimal:
        return _decimal(self._table.select('wire_dia_max', id=self._db_id)[0][0])

    @wire_dia_max.setter
    def wire_dia_max(self, value: _decimal):
        self._table.update(self._db_id, wire_dia_max=float(value))

    @property
    def min_wire_cross(self) -> _decimal:
        return _decimal(self._table.select('min_wire_cross', id=self._db_id)[0][0])

    @min_wire_cross.setter
    def min_wire_cross(self, value: _decimal):
        self._table.update(self._db_id, min_wire_cross=float(value))

    @property
    def max_wire_cross(self) -> _decimal:
        return _decimal(self._table.select('max_wire_cross', id=self._db_id)[0][0])

    @max_wire_cross.setter
    def max_wire_cross(self, value: _decimal):
        self._table.update(self._db_id, max_wire_cross=float(value))

    @property
    def plating(self) -> "_plating.Plating":
        from .plating import Plating
        plating_id = self.plating_id

        return Plating(self._table.db.platings_table, plating_id)

    @plating.setter
    def plating(self, value: "_plating.Plating"):
        self._table.update(self._db_id, plating_id=value.db_id)

    @property
    def plating_id(self) -> int:
        return self._table.select('plating_id', id=self._db_id)[0][0]

    @plating_id.setter
    def plating_id(self, value: int):
        self._table.update(self._db_id, plating_id=value)
