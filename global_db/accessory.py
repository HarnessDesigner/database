from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import PartNumberMixin, DescriptionMixin, ManufacturerMixin, FamilyMixin, SeriesMixin, ColorMixin, MaterialMixin


class AccessoriesTable(TableBase):
    __table_name__ = 'accessories'

    def __iter__(self) -> _Iterable["Accessory"]:
        for db_id in TableBase.__iter__(self):
            yield Accessory(self, db_id)

    def __getitem__(self, item) -> "Accessory":
        if isinstance(item, int):
            if item in self:
                return Accessory(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Accessory(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, code: str, description: str) -> "Accessory":
        db_id = TableBase.insert(self, code=code, description=description)
        return Accessory(self, db_id)

    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Series',
            'Family',
            'Material'
        ]

    def parts_list(self):
        cmd = (
         'SELECT accessory.id, accessory.part_number, accessory.description, manufacturer.name,',
         'family.name, series.name, material.name FROM accessories accessory',
         'INNER JOIN manufacturers manufacturer ON accessory.mfg_id = manufacturer.id',
         'INNER JOIN families family ON accessory.family_id = family.id',
         'INNER JOIN series series ON accessory.series_id = series.id',
         'INNER JOIN materials material ON accessory.material_id = material.id'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Family': dict(),
            'Series': dict(),
            'Material': dict()
        }

        res = {}

        for id, part_number, description, mfg, family, series, material in data:
            res[part_number] = (mfg, description, series, family, material, id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            if family not in commons['Family']:
                commons['Family'][family] = []

            if series not in commons['Series']:
                commons['Series'][series] = []

            if material not in commons['Material']:
                commons['Material'][material] = []

            commons['Manufacturer'][mfg].append(part_number)
            commons['Family'][family].append(part_number)
            commons['Series'][series].append(part_number)
            commons['Material'][material].append(part_number)

        return res, commons


class Accessory(EntryBase, PartNumberMixin, DescriptionMixin, ManufacturerMixin, FamilyMixin, SeriesMixin, ColorMixin, MaterialMixin):
    _table: AccessoriesTable = None
