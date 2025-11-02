from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, GenderMixin,
                     SeriesMixin, FamilyMixin, ResourceMixin, WeightMixin, CavityLockMixin)

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
               blade_size: float, resistance_mohms: float, mating_cycles: int,
               max_vibration_g: int, max_current_ma: int, wire_size_min_awg: int,
               wire_size_max_awg: int, wire_dia_min: float, wire_dia_max: float,
               min_wire_cross: float, max_wire_cross: float, plating_id: int,
               weight: float) -> "Terminal":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 gender_id=gender_id, series_id=series_id, family_id=family_id, sealing=int(sealing),
                                 cavity_lock_id=cavity_lock_id, image_id=image_id, datasheet_id=datasheet_id,
                                 cad_id=cad_id, material_id=material_id, blade_size=blade_size,
                                 resistance_mohms=resistance_mohms, mating_cycles=mating_cycles,
                                 max_vibration_g=max_vibration_g, max_current_ma=max_current_ma,
                                 wire_size_min_awg=wire_size_min_awg, wire_size_max_awg=wire_size_max_awg,
                                 wire_dia_min=wire_dia_min, wire_dia_max=wire_dia_max,
                                 min_wire_cross=min_wire_cross, max_wire_cross=max_wire_cross,
                                 plating_id=plating_id, weight=weight)
        return Terminal(self, db_id)


class Terminal(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, GenderMixin,
               SeriesMixin, FamilyMixin, ResourceMixin, WeightMixin, CavityLockMixin):

    _table: TerminalsTable = None

    @property
    def sealing(self) -> bool:
        return bool(self._table.select('sealing', id=self._db_id)[0][0])

    @sealing.setter
    def sealing(self, value: bool):
        self._table.update(self._db_id, size=int(value))

    @property
    def blade_size(self) -> float:
        return self._table.select('blade_size', id=self._db_id)[0][0]

    @blade_size.setter
    def blade_size(self, value: float):
        self._table.update(self._db_id, blade_size=value)

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
    def wire_dia_min(self) -> float:
        return self._table.select('wire_dia_min', id=self._db_id)[0][0]

    @wire_dia_min.setter
    def wire_dia_min(self, value: float):
        self._table.update(self._db_id, wire_dia_min=value)

    @property
    def wire_dia_max(self) -> float:
        return self._table.select('wire_dia_max', id=self._db_id)[0][0]

    @wire_dia_max.setter
    def wire_dia_max(self, value: float):
        self._table.update(self._db_id, wire_dia_max=value)

    @property
    def min_wire_cross(self) -> float:
        return self._table.select('min_wire_cross', id=self._db_id)[0][0]

    @min_wire_cross.setter
    def min_wire_cross(self, value: float):
        self._table.update(self._db_id, min_wire_cross=value)

    @property
    def max_wire_cross(self) -> float:
        return self._table.select('max_wire_cross', id=self._db_id)[0][0]

    @max_wire_cross.setter
    def max_wire_cross(self, value: float):
        self._table.update(self._db_id, max_wire_cross=value)

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
