from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from . import terminal as _terminal
from . import seal as _seal
from . import cpa_lock as _cpa_lock
from . import tpa_lock as _tpa_lock
from . import cover as _cover
from . import ip as _ip
from . import cavity_lock as _cavity_lock


from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin, 
                     SeriesMixin, GenderMixin, ImageMixin, DatasheetMixin, CADMixin,
                     TemperatureMixin, DirectionMixin, DimensionMixin, ColorMixin)


class HousingsTable(TableBase):
    __table_name__ = 'housings'

    def __iter__(self) -> _Iterable["Housing"]:

        for db_id in TableBase.__iter__(self):
            yield Housing(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int, series_id: int,
               gender_id: int, ip_rating_id: int, image_id: int, datasheet_id: int, cad_id: int,
               min_temp_id: int, max_temp_id: int, cavity_lock_id: int, direction_id: int, sealed: bool,
               length: float, width: float, height: float, centerline: float, color_id: int, rows: int,
               num_pins: int, terminal_sizes: list[float], compat_cpas: list, compat_tpas: list,
               compat_covers: list, compat_terminals: list, compat_seals: list, mates_to: list) -> "Housing":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, gender_id=gender_id, 
                                 ip_rating_id=ip_rating_id, image_id=image_id, datasheet_id=datasheet_id,
                                 cad_id=cad_id, min_temp_id=min_temp_id, max_temp_id=max_temp_id, 
                                 cavity_lock_id=cavity_lock_id, direction_id=direction_id, sealed=int(sealed),
                                 length=length, width=width, height=height, centerline=centerline,
                                 color_id=color_id, rows=rows, num_pins=num_pins, terminal_sizes=str(terminal_sizes),
                                 compat_cpas=str(compat_cpas), compat_tpas=str(compat_tpas), 
                                 compat_covers=str(compat_covers), compat_terminals=str(compat_terminals),
                                 compat_seals=str(compat_seals), mates_to=str(mates_to))

        return Housing(self, db_id)


class Housing(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin, 
              SeriesMixin, GenderMixin, ImageMixin, DatasheetMixin, CADMixin, TemperatureMixin, 
              DirectionMixin, DimensionMixin, ColorMixin):

    _table: HousingsTable = None

    @property
    def compat_covers(self) -> list[_cover.Cover]:
        compat_covers = eval(self._table.select('compat_covers', id=self._db_id)[0][0])
        res = []
        for part_number in compat_covers:
            db_id = self._table.db.covers_table.select('id', part_number=part_number)
            if db_id:
                res.append(_cover.Cover(self._table.db.covers_table, db_id[0][0]))
        return res

    @compat_covers.setter
    def compat_covers(self, value: list[_cover.Cover]):
        compat_covers = [cover.part_number for cover in value]
        self._table.update(self._db_id, compat_covers=str(compat_covers))

    @property
    def compat_cpas(self) -> list[_cpa_lock.CPALock]:
        compat_cpas = eval(self._table.select('compat_cpas', id=self._db_id)[0][0])
        res = []
        for part_number in compat_cpas:
            db_id = self._table.db.cpa_locks_table.select('id', part_number=part_number)
            if db_id:
                res.append(_cpa_lock.CPALock(self._table.db.cpa_locks_table, db_id[0][0]))
        return res

    @compat_cpas.setter
    def compat_cpas(self, value: list[_cpa_lock.CPALock]):
        compat_cpas = [cpa.part_number for cpa in value]
        self._table.update(self._db_id, compat_cpas=str(compat_cpas))

    @property
    def compat_tpas(self) -> list[_tpa_lock.TPALock]:
        compat_tpas = eval(self._table.select('compat_tpas', id=self._db_id)[0][0])
        res = []
        for part_number in compat_tpas:
            db_id = self._table.db.tpa_locks_table.select('id', part_number=part_number)
            if db_id:
                res.append(_tpa_lock.TPALock(self._table.db.tpa_locks_table, db_id[0][0]))
        return res

    @compat_tpas.setter
    def compat_tpas(self, value: list[_tpa_lock.TPALock]):
        compat_tpas = [tpa.part_number for tpa in value]
        self._table.update(self._db_id, compat_tpas=str(compat_tpas))

    @property
    def compat_terminals(self) -> list[_terminal.Terminal]:
        compat_terminals = eval(self._table.select('compat_terminals', id=self._db_id)[0][0])
        res = []
        for part_number in compat_terminals:
            db_id = self._table.db.terminals_table.select('id', part_number=part_number)
            if db_id:
                res.append(_terminal.Terminal(self._table.db.terminals_table, db_id[0][0]))
        return res

    @compat_terminals.setter
    def compat_terminals(self, value: list[_terminal.Terminal]):
        compat_terminals = [terminal.part_number for terminal in value]
        self._table.update(self._db_id, compat_terminals=str(compat_terminals))

    @property
    def compat_seals(self) -> list[_seal.Seal]:
        compat_seals = eval(self._table.select('compat_seals', id=self._db_id)[0][0])
        res = []
        for part_number in compat_seals:
            db_id = self._table.db.seals_table.select('id', part_number=part_number)
            if db_id:
                res.append(_seal.Seal(self._table.db.seals_table, db_id[0][0]))
        return res

    @compat_seals.setter
    def compat_seals(self, value: list[_seal.Seal]):
        compat_seals = [seal.part_number for seal in value]
        self._table.update(self._db_id, compat_seals=str(compat_seals))

    @property
    def mates_to(self) -> list["Housing"]:
        housings = eval(self._table.select('mates_to', id=self._db_id)[0][0])
        res = []
        for part_number in housings:
            db_id = self._table.db.housings_table.select('id', part_number=part_number)
            if db_id:
                res.append(Housing(self._table.db.housings_table, db_id[0][0]))
        return res

    @mates_to.setter
    def mates_to(self, value: list["Housing"]):
        mates_to = [housing.part_number for housing in value]
        self._table.update(self._db_id, mates_to=str(mates_to))

    @property
    def ip_rating(self) -> _ip.IPRating:
        ip_rating_id = self._table.select('ip_rating_id', id=self._db_id)
        return _ip.IPRating(self._table.db.ip_ratings_table, ip_rating_id[0][0])

    @ip_rating.setter
    def ip_rating(self, value: _ip.IPRating):
        self._table.update(self._db_id, ip_rating_id=value.db_id)
    
    @property
    def ip_rating_id(self):
        return self._table.select('ip_rating_id', id=self._db_id)[0][0]

    @ip_rating_id.setter
    def ip_rating_id(self, value):
        self._table.update(self._db_id, ip_rating_id=value)

    @property
    def cavity_lock(self) -> _cavity_lock.CavityLock:
        cavity_lock_id = self._table.select('cavity_lock_id', id=self._db_id)
        return _cavity_lock.CavityLock(self._table.db.cavity_locks_table, cavity_lock_id[0][0])

    @cavity_lock.setter
    def cavity_lock(self, value: _cavity_lock.CavityLock):
        self._table.update(self._db_id, cavity_lock_id=value.db_id)

    @property
    def cavity_lock_id(self):
        return self._table.select('cavity_lock_id', id=self._db_id)[0][0]

    @cavity_lock_id.setter
    def cavity_lock_id(self, value):
        self._table.update(self._db_id, cavity_lock_id=value)

    @property
    def terminal_sizes(self) -> list[float]:
        return eval(self._table.select('terminal_sizes', id=self._db_id)[0][0])

    @terminal_sizes.setter
    def terminal_sizes(self, value: list[float]):
        self._table.update(self._db_id, terminal_sizes=str(value))

    @property
    def sealed(self) -> bool:
        return bool(self._table.select('sealed', id=self._db_id)[0][0])

    @sealed.setter
    def sealed(self, value: bool):
        self._table.update(self._db_id, sealed=int(value))

    @property
    def centerline(self) -> float:
        return self._table.select('centerline', id=self._db_id)[0][0]

    @centerline.setter
    def centerline(self, value: float):
        self._table.update(self._db_id, centerline=value)

    @property
    def rows(self) -> int:
        return self._table.select('rows', id=self._db_id)[0][0]

    @rows.setter
    def rows(self, value: int):
        self._table.update(self._db_id, rows=value)

    @property
    def num_pins(self) -> int:
        return self._table.select('num_pins', id=self._db_id)[0][0]

    @num_pins.setter
    def num_pins(self, value: int):
        self._table.update(self._db_id, num_pins=value)
