
from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase
from .mixins import (PartNumberMixin, SeriesMixin, MaterialMixin, FamilyMixin,
                     ManufacturerMixin, DescriptionMixin, ColorMixin, ProtectionMixin,
                     AdhesiveMixin, ResourceMixin, TemperatureMixin, WeightMixin)


if TYPE_CHECKING:
    from . import transition_branch as _transition_branch
    from . import shape as _shape


class TransitionsTable(TableBase):
    __table_name__ = 'transitions'

    def __iter__(self) -> _Iterable["Transition"]:
        for db_id in TableBase.__iter__(self):
            yield Transition(self, db_id)

    def __getitem__(self, item) -> "Transition":
        if isinstance(item, int):
            if item in self:
                return Transition(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Transition(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, color_id: int, material_id: int, branch_count: int,
               shape_id: int, protection_ids: list[int], adhesive_ids: list[int],
               cad_id: int, datasheet_id: int, image_id: int, min_temp_id: int,
               max_temp_id: int, weight: float) -> "Transition":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, color_id=color_id,
                                 material_id=material_id, branch_count=branch_count, shape_id=shape_id,
                                 protection_ids=str(protection_ids), adhesive_ids=str(adhesive_ids),
                                 cad_id=cad_id, datasheet_id=datasheet_id, image_id=image_id,
                                 min_temp_id=min_temp_id, max_temp_id=max_temp_id, weight=weight)

        return Transition(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        families = self.get_unique('family_id', 'families')
        series = self.get_unique('series_id', 'series')
        transition_series = self.get_unique('transition_series_id', 'transition_series')
        colors = self.get_unique('color_id', 'colors')
        materials = self.get_unique('material_id', 'materials')
        branch_counts = self.get_unique('branch_count')
        shapes = self.get_unique('shape_id', 'shapes')
        protections = self.get_unique('protection_id', 'protections')
        min_temps = self.get_unique('min_temp_id', 'temperatures')
        max_temps = self.get_unique('max_temp_id', 'temperatures')
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
            'Transition Series': {
                'field': 'transition_series_id',
                'type': 'id',
                'values': transition_series
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
            'Branch Count': {
                'field': 'branch_count',
                'type': 'int',
                'values': branch_counts
            },
            'Shape': {
                'field': 'shape_id',
                'type': 'id',
                'values': shapes
            },
            'Protection': {
                'field': 'protection_id',
                'type': 'id',
                'values': protections
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
            }
        }

        return ret


    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Branch Count',
            'Shape',
            'Series',
            'Family',
            'Material',
            'Weight',
            'Protection',
            'Adhesive',
            'Min Temp',
            'Max Temp'
        ]

    def parts_list(self):
        cmd = (
            'SELECT transition.id, transition.part_number, transition.description,',
            'manufacturer.name, series.name, transition.weight, material.name,',
            'transition.branch_count, protection.name, adhesive.name, shape.name,',
            'mintemp.name, maxtemp.name, family.name FROM transitions transition',
            'INNER JOIN manufacturers manufacturer ON transition.mfg_id = manufacturer.id',
            'INNER JOIN families family ON transition.family_id = family.id',
            'INNER JOIN materials material ON transition.material_id = material.id',
            'INNER JOIN adhesives adhesive ON transition.adhesive_id = adhesive.id',
            'INNER JOIN protections adhesive ON transition.protection_id = protection.id',
            'INNER JOIN shapes shape ON transition.shape_id = shape.id',
            'INNER JOIN temperatures mintemp ON transition.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON transition.max_temp_id = maxtemp.id',
            'INNER JOIN series series ON transition.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Material': dict(),
            'Branch Count': dict(),
            'Protection': dict(),
            'Adhesive': dict(),
            'Shape': dict(),
            'Series': dict(),
            'Family': dict()
        }

        res = {}

        for (id, part_number, description, mfg, series, weight, material, branch_count,
             protection, adhesive, shape, mintemp, maxtemp, family) in data:

            res[part_number] = (mfg, description, branch_count, shape, series,
                                family, material, weight, protection, adhesive,
                                mintemp, maxtemp, id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            if material not in commons['Material']:
                commons['Material'][material] = []

            commons['Material'][material].append(part_number)

            if branch_count not in commons['Branch Count']:
                commons['Branch Count'][branch_count] = []

            commons['Branch Count'][branch_count].append(part_number)

            if protection not in commons['Protection']:
                commons['Protection'][protection] = []

            commons['Protection'][protection].append(part_number)

            if adhesive not in commons['Adhesive']:
                commons['Adhesive'][adhesive] = []

            commons['Adhesive'][adhesive].append(part_number)

            if shape not in commons['Shape']:
                commons['Shape'][shape] = []

            commons['Shape'][shape].append(part_number)

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Series'][series].append(part_number)

            if family not in commons['Family']:
                commons['Family'][family] = []

            commons['Family'][family].append(part_number)

        return res, commons


class Transition(EntryBase, PartNumberMixin, SeriesMixin, MaterialMixin, FamilyMixin,
                 ManufacturerMixin, DescriptionMixin, ColorMixin, ProtectionMixin, AdhesiveMixin,
                 ResourceMixin, TemperatureMixin, WeightMixin):
    
    _table: TransitionsTable = None

    @property
    def branch_count(self) -> int:
        return self._table.select('branch_count', id=self._db_id)[0][0]

    @branch_count.setter
    def branch_count(self, value: int):
        self._table.update(self._db_id, branch_count=value)

    @property
    def branches(self) -> list["_transition_branch.TransitionBranch"]:
        res = [None] * self.branch_count

        branch_ids = self._table.db.transition_branches_table.select('id', transition_id=self._db_id)

        for branch_id in branch_ids:
            branch = self._table.db.transition_branches_table[branch_id[0]]
            res[branch.idx - 1] = branch

        return res

    @property
    def shape(self) -> "_shape.Shape":
        shape_id = self.shape_id
        from .shape import Shape

        return Shape(self._table.db.shapes_table, shape_id)

    @shape.setter
    def shape(self, value: "_shape.Shape"):
        self._table.update(self._db_id, shape_id=value.db_id)

    @property
    def shape_id(self) -> int:
        return self._table.select('shape_id', id=self._db_id)[0][0]

    @shape_id.setter
    def shape_id(self, value: int):
        self._table.update(self._db_id, shape_id=value)
