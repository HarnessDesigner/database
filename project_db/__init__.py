
from typing import Iterable as _Iterable


class PJTEntryBase:

    def __init__(self, table: "PJTTableBase", db_id: int, project_id: int):
        self._table = table
        self._db_id = db_id
        self.project_id = project_id

    @property
    def db_id(self):
        return self._db_id

    def delete(self) -> None:
        self._table.delete(self.db_id)


class PJTTableBase:
    __table_name__: str = None

    def __init__(self, db: "PJTTablesBase", project_id: int):
        self.db = db
        self.project_id = project_id

        self._con = db.con
        self._cur = db.cur

    def __getitem__(self, item):
        self._cur.execute(f'SELECT * FROM {self.__table_name__} WHERE id = {item};')

        for line in self._cur.fetchall():
            return line

    def __iter__(self) -> _Iterable[int]:
        self._cur.execute(f'SELECT id FROM {self.__table_name__} WHERE project_id = {self.project_id};')

        for line in self._cur.fetchall():
            yield line[0]

    @property
    def table_name(self) -> str:
        return self.__table_name__

    def __contains__(self, db_id: int) -> bool:
        self._cur.execute(f'SELECT id FROM {self.__table_name__} WHERE id = {db_id};')

        if self._cur.fetchall():
            return True

        return False

    def insert(self, **kwargs) -> int:
        fields = ['project_id']
        values = ['?']
        args = [self.project_id]

        for key, value in kwargs.items():
            fields.append(key)
            args.append(value)
            values.append('?')

        fields = ', '.join(fields)
        values = ', '.join(values)
        self._cur.execute(f'INSERT INTO {self.__table_name__} ({fields}) VALUES ({values});', args)
        self._con.commit()
        return self._cur.lastrowid

    def select(self, *args, **kwargs):
        args = ', '.join(args)

        values = [f'project_id = {self.project_id}']
        for key, value in kwargs.items():
            if isinstance(value, (str, float)):
                value = f'"{value}"'
            elif value is None:
                value = 'NULL'

            values.append(f'{key} = {value}')

        values = ' AND '.join(values)

        where = f' WHERE {values}'

        self._cur.execute(f'SELECT {args} FROM {self.__table_name__}{where};')
        res = self._cur.fetchall()
        return res

    def delete(self, db_id: int) -> None:
        self._cur.execute(f'DELETE FROM {self.__table_name__} WHERE id = {db_id};')
        self._con.commit()

    def update(self, db_id: int, **kwargs):
        fields = []
        values = []

        for key, value in kwargs.items():
            fields.append(f'{key} = ?')
            values.append(value)

        fields = ', '.join(fields)
        self._cur.execute(f'UPDATE {self.__table_name__} SET {fields} WHERE id = {db_id};', values)
        self._con.commit()

    def execute(self, cmd, params=None):
        if params is None:
            self._cur.execute(cmd)
        else:
            self._cur.execute(cmd, params)

    def fetchall(self):
        return self._cur.fetchall()


class PJTTablesBase:

    def __init__(self, connector):
        self.connector = connector
        self.con = connector
        self.cur = connector

        self._boots_table = None
        self._manufacturers_table = None
        self._tpa_locks_table = None
        self._cpa_locks_table = None
        self._materials_table = None
        self._covers_table = None
        self._housings_table = None
        self._seals_table = None
        self._series_table = None
        self._terminals_table = None
        self._wires_table = None
        self._cavity_locks_table = None
        self._colors_table = None
        self._directions_table = None
        self._cads_table = None
        self._datasheets_table = None
        self._families_table = None
        self._genders_table = None
        self._images_table = None
        self._sealings_table = None
        self._temperatures_table = None
        self._ip_solids_table = None
        self._ip_fluids_table = None
        self._ip_supps_table = None
        self._ip_ratings_table = None
        self._cavities_table = None
        self._cavity_maps_table = None
        self._bundle_cover_series_table = None
        self._bundle_cover_resistances_table = None
        self._bundle_cover_materials_table = None
        self._bundle_cover_rigidities_table = None
        self._bundle_covers_table = None
        self._transition_branches_table = None
        self._transition_adhesives_table = None
        self._transition_sizes_table = None
        self._transition_materials_table = None
        self._transition_series_table = None
        self._transition_families_table = None
        self._transition_protections_table = None
        self._transition_shapes_table = None
        self._transition_layouts_table = None
        self._transitions_table = None

    @property
    def boots_table(self) -> BootsTable:
        return self._boots_table

    @property
    def manufacturers_table(self) -> ManufacturersTable:
        return self._manufacturers_table

    @property
    def tpa_locks_table(self) -> TPALocksTable:
        return self._tpa_locks_table

    @property
    def cpa_locks_table(self) -> CPALocksTable:
        return self._cpa_locks_table

    @property
    def materials_table(self) -> MaterialsTable:
        return self._materials_table

    @property
    def covers_table(self) -> CoversTable:
        return self._covers_table

    @property
    def housings_table(self) -> HousingsTable:
        return self._housings_table

    @property
    def seals_table(self) -> SealsTable:
        return self._seals_table

    @property
    def series_table(self) -> SeriesTable:
        return self._series_table

    @property
    def terminals_table(self) -> TerminalsTable:
        return self._terminals_table

    @property
    def wires_table(self) -> WiresTable:
        return self._wires_table

    @property
    def cavity_locks_table(self) -> CavityLocksTable:
        return self._cavity_locks_table

    @property
    def colors_table(self) -> ColorsTable:
        return self._colors_table

    @property
    def directions_table(self) -> DirectionsTable:
        return self._directions_table

    @property
    def cads_table(self) -> CADsTable:
        return self._cads_table

    @property
    def datasheets_table(self) -> DatasheetsTable:
        return self._datasheets_table

    @property
    def families_table(self) -> FamiliesTable:
        return self._families_table

    @property
    def genders_table(self) -> GendersTable:
        return self._genders_table

    @property
    def images_table(self) -> ImagesTable:
        return self._images_table

    @property
    def sealings_table(self) -> SealingsTable:
        return self._sealings_table

    @property
    def temperatures_table(self) -> TemperaturesTable:
        return self._temperatures_table

    @property
    def ip_solids_table(self) -> IPSolidsTable:
        return self._ip_solids_table

    @property
    def ip_fluids_table(self) -> IPFluidsTable:
        return self._ip_fluids_table

    @property
    def ip_supps_table(self) -> IPSuppsTable:
        return self._ip_supps_table

    @property
    def ip_ratings_table(self) -> IPRatingsTable:
        return self._ip_ratings_table

    @property
    def cavities_table(self) -> CavitiesTable:
        return self._cavities_table

    @property
    def cavity_maps_table(self) -> CavityMapsTable:
        return self._cavity_maps_table

    @property
    def bundle_cover_series_table(self) -> BundleCoverSeriesTable:
        return self._bundle_cover_series_table

    @property
    def bundle_cover_resistances_table(self) -> BundleCoverResistancesTable:
        return self._bundle_cover_resistances_table

    @property
    def bundle_cover_materials_table(self) -> BundleCoverMaterialsTable:
        return self._bundle_cover_materials_table

    @property
    def bundle_cover_rigidities_table(self) -> BundleCoverRigiditiesTable:
        return self._bundle_cover_rigidities_table

    @property
    def bundle_covers_table(self) -> BundleCoversTable:
        return self._bundle_covers_table

    @property
    def transition_branches_table(self) -> TransitionBranchesTable:
        return self._transition_branches_table

    @property
    def transition_adhesives_table(self) -> TransitionAdhesivesTable:
        return self._transition_adhesives_table

    @property
    def transition_sizes_table(self) -> TransitionSizesTable:
        return self._transition_sizes_table

    @property
    def transition_materials_table(self) -> TransitionMaterialsTable:
        return self._transition_materials_table

    @property
    def transition_series_table(self) -> TransitionSeriesTable:
        return self._transition_series_table

    @property
    def transition_families_table(self) -> TransitionFamiliesTable:
        return self._transition_families_table

    @property
    def transition_protections_table(self) -> TransitionProtectionsTable:
        return self._transition_protections_table

    @property
    def transition_shapes_table(self) -> TransitionShapesTable:
        return self._transition_shapes_table

    @property
    def transition_layouts_table(self) -> TransitionLayoutsTable:
        return self._transition_layouts_table

    @property
    def transitions_table(self) -> TransitionsTable:
        return self._transitions_table

pjt_manufacturers
id, global_id, local_id

pjt_temperatures
id, global_id, local_id

pjt_genders
id, global_id, local_id

pjt_transition_protections
id, global_id, local_id

pjt_transition_adhesives
id, global_id, local_id

pjt_transition_sizes
id, global_id, local_id

pjt_transition_materials
id, global_id, local_id

pjt_transition_families
id, global_id, local_id

pjt_transition_shapes
id, global_id, local_id

pjt_cads
id, global_id, local_id

pjt_cavity_locks
id, global_id, local_id

pjt_colors
id, global_id, local_id

pjt_datasheets
id, global_id, local_id

pjt_directions
id, global_id, local_id

pjt_images
id, global_id, local_id

pjt_ip_fluids
id, global_id, local_id

pjt_ip_solids
id, global_id, local_id

pjt_ip_supps
id, global_id, local_id

pjt_materials
id, global_id, local_id

pjt_series
id, global_id, local_id

pjt_families
id, global_id, local_id

pjt_ip_ratings
id, global_id, local_id

pjt_transition_series
id, global_id, local_id

pjt_transitions
id, global_id, local_id

pjt_transition_maps
id, global_id, local_id

pjt_transition_branches
id, global_id, local_id

pjt_boots
id, global_id, local_id

pjt_bundle_cover_series
id, global_id, local_id

pjt_bundle_cover_resistances
id, global_id, local_id

pjt_bundle_cover_materials
id, global_id, local_id

pjt_bundle_cover_rigidities
id, global_id, local_id

pjt_bundle_covers
id, global_id, local_id

pjt_covers
id, global_id, local_id

pjt_cpa_locks
id, global_id, local_id

pjt_tpa_locks
id, global_id, local_id

pjt_seals
id, global_id, local_id

pjt_wires
id, global_id, local_id

pjt_terminals
id, global_id, local_id

pjt_housings
id, global_id, local_id

pjt_cavity_maps
id, global_id, local_id

pjt_cavities
id, global_id, local_id




terminals
id, project_id, part_id, circuit_id, cavity_id

seals
id, project_id, part_id, cavity_id

cavities
id, project_id, part_id, cavity_map_id, name, wire_ids

cavity_maps
id, project_id, part_id, housing_id

housings
id, project_id, part_id, coords3d_id, coords2d_id, x_angle_3d, y_angle_3d, z_angle_3d, angle_2d



coordinates_3d

id, project_id, x, y, z


transitions
id, project_id, part_id, branch1_coord_id, branch2_coord_id, branch3_coord_id, branch4_coord_id, branch5_coord_id, branch6_coord_id


bundle_layouts
id, project_id, coord_id,


bundles
id, project_id, part_id, start_coord_id, end_coord_id



wire2d_layouts
id, project_id, circuit_id, coord_id


wire3d_lauouts
id, project_id, circuit_id, coord_id


splices
id, project_id, part_id, circuit_id, coord3d_id, coord2d_id


wires
id, project_id, part_id, circuit_id, start_coord3d_id, end_coord3d_id, start_coord2d_id, end_coord2d_id









schematic_housings
id, project_id, x1, y1, x2, y2,

schematic_terminals
id, project_id, x1, y1, x2, y2,

schematic_bundles
id, project_id, x1, y1, x2, y2,

schematic_transitions
id, project_id, x1, y1, x2, y2,


schematic_wires
id, project_id, x1, y1, x2, y2,

schematic_layouts
id, project_id, x, y

schematics
id, project_id


projects
id, name, schematic_id, plan_id


project_parts
id,project_id, part_id, part_type


part_types

TRANSITION = 1
BOOT = 2
BUNDLE_COVER = 3
COVER = 4
CPA_LOCK = 5
TPA_LOCK = 6
SEAL = 7
WIRE = 8
TERMINAL = 9
HOUSING = 10


