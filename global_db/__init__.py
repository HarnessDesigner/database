from typing import Iterable as _Iterable, TYPE_CHECKING


if TYPE_CHECKING:
    from ... import ui as _ui


class EntryBase:

    def __init__(self, table: "TableBase", db_id: int):
        self._table = table
        self._db_id = db_id

    @property
    def db_id(self):
        return self._db_id

    def delete(self) -> None:
        self._table.delete(self.db_id)


class TableBase:
    __table_name__: str = None

    def __init__(self, db: "GLBTables"):
        self.db = db
        self._con = db.connector

    def __getitem__(self, item):
        self._con.execute(f'SELECT * FROM {self.__table_name__} WHERE id = {item};')

        for line in self._con.fetchall():
            return line

    def __iter__(self) -> _Iterable[int]:
        self._con.execute(f'SELECT id FROM {self.__table_name__};')

        for line in self._con.fetchall():
            yield line[0]

    @property
    def table_name(self) -> str:
        return self.__table_name__

    def __contains__(self, db_id: int) -> bool:
        self._con.execute(f'SELECT id FROM {self.__table_name__} WHERE id = {db_id};')

        if self._con.fetchall():
            return True

        return False

    def insert(self, *_, **kwargs) -> int:
        fields = []
        values = []
        args = []

        for key, value in kwargs.items():
            fields.append(key)
            args.append(value)
            values.append('?')

        fields = ', '.join(fields)
        values = ', '.join(values)
        self._con.execute(f'INSERT INTO {self.__table_name__} ({fields}) VALUES ({values});', args)
        self._con.commit()
        return self._con.lastrowid

    def select(self, *args, **kwargs):
        args = ', '.join(args)

        if kwargs:
            values = []
            for key, value in kwargs.items():
                if isinstance(value, (str, float)):
                    value = f'"{value}"'
                elif value is None:
                    value = 'NULL'

                values.append(f'{key} = {value}')

            values = ' AND '.join(values)

            where = f' WHERE {values}'
        else:
            where = ''

        self._con.execute(f'SELECT {args} FROM {self.__table_name__}{where};')
        res = self._con.fetchall()
        return res

    def delete(self, db_id: int) -> None:
        self._con.execute(f'DELETE FROM {self.__table_name__} WHERE id = {db_id};')
        self._con.commit()

    def update(self, db_id: int, **kwargs):
        fields = []
        values = []

        for key, value in kwargs.items():
            fields.append(f'{key} = ?')
            values.append(value)

        fields = ', '.join(fields)
        self._con.execute(f'UPDATE {self.__table_name__} SET {fields} WHERE id = {db_id};', values)
        self._con.commit()

    def execute(self, cmd, params=None):
        if params is None:
            return self._con.execute(cmd)
        else:
            return self._con.execute(cmd, params)

    def fetchall(self):
        return self._con.fetchall()

    @property
    def search_items(self) -> dict:
        raise NotImplementedError

    def get_unique(self, field_name, table_name=None, get_field_name='name'):
        if table_name is None:
            self.execute(f'SELECT DISTINCT {field_name} FROM {self.__table_name__};')
            values = [item[0] for item in self._con.fetchall()]
            return values
        else:
            self.execute(f'SELECT DISTINCT {field_name} FROM {self.__table_name__};')
            ids = self._con.fetchall()

            cmd = [f'id = {id_[0]}' for id_ in ids]

            if cmd:
                self.execute(f'SELECT id, {get_field_name} FROM {table_name} WHERE {" OR ".join(cmd)};')
                return self._con.fetchall()

            return []



from .accessory import AccessoriesTable  # NOQA
from .boot import BootsTable  # NOQA
from .wire import WiresTable  # NOQA
from .cover import CoversTable  # NOQA
from .seal import SealsTable  # NOQA
from .manufacturer import ManufacturersTable  # NOQA
from .tpa_lock import TPALocksTable  # NOQA
from .cpa_lock import CPALocksTable  # NOQA
from .plating import PlatingsTable  # NOQA
from .material import MaterialsTable  # NOQA
from .direction import DirectionsTable  # NOQA
from .terminal import TerminalsTable  # NOQA
from .series import SeriesTable  # NOQA
from .housing import HousingsTable  # NOQA
from .color import ColorsTable  # NOQA
from .sealing import SealingsTable  # NOQA
from .temperature import TemperaturesTable  # NOQA
from .resource import ResourcesTable  # NOQA
from .cavity import CavitiesTable  # NOQA
from .cavity_lock import CavityLocksTable  # NOQA
from .family import FamiliesTable  # NOQA
from .gender import GendersTable  # NOQA
from .ip import IPRatingsTable  # NOQA
from .ip.fluid import IPFluidsTable  # NOQA
from .ip.solid import IPSolidsTable  # NOQA
from .ip.supp import IPSuppsTable  # NOQA
from .bundle_cover import BundleCoversTable  # NOQA
from .shape import ShapesTable  # NOQA
from .transition_branch import TransitionBranchesTable  # NOQA
from .adhesive import AdhesivesTable  # NOQA
from .protection import ProtectionsTable  # NOQA
from .transition import TransitionsTable  # NOQA
from .splice import SplicesTable  # NOQA
from .model3d import Models3DTable  # NOQA
from .wire_marker import WireMarkersTable  # NOQA
from .splice_types import SpliceTypesTable  # NOQA


class GLBTables:

    def __init__(self, mainframe: "_ui.MainFrame"):
        self.mainframe = mainframe

        self.connector = mainframe.db_connector

        if self.connector.create_tables:
            self._setup_new_db()

        self._boots_table = BootsTable(self)
        self._manufacturers_table = ManufacturersTable(self)
        self._tpa_locks_table = TPALocksTable(self)
        self._cpa_locks_table = CPALocksTable(self)
        self._materials_table = MaterialsTable(self)
        self._platings_table = PlatingsTable(self)
        self._covers_table = CoversTable(self)
        self._housings_table = HousingsTable(self)
        self._seals_table = SealsTable(self)
        self._series_table = SeriesTable(self)
        self._terminals_table = TerminalsTable(self)
        self._wires_table = WiresTable(self)
        self._cavity_locks_table = CavityLocksTable(self)
        self._colors_table = ColorsTable(self)
        self._directions_table = DirectionsTable(self)
        self._resources_table = ResourcesTable(self)
        self._families_table = FamiliesTable(self)
        self._genders_table = GendersTable(self)
        self._sealings_table = SealingsTable(self)
        self._temperatures_table = TemperaturesTable(self)
        self._ip_solids_table = IPSolidsTable(self)
        self._ip_fluids_table = IPFluidsTable(self)
        self._ip_supps_table = IPSuppsTable(self)
        self._ip_ratings_table = IPRatingsTable(self)
        self._cavities_table = CavitiesTable(self)
        self._protections_table = ProtectionsTable(self)
        self._bundle_covers_table = BundleCoversTable(self)
        self._transition_branches_table = TransitionBranchesTable(self)
        self._adhesives_table = AdhesivesTable(self)
        self._protections_table = ProtectionsTable(self)
        self._shapes_table = ShapesTable(self)
        self._transitions_table = TransitionsTable(self)
        self._accessories_table = AccessoriesTable(self)
        self._splices_table = SplicesTable(self)
        self._models3d_table = Models3DTable(self)
        self._wire_markers_table = WireMarkersTable(self)
        self._splice_types_table = SpliceTypesTable(self)

    @property
    def accessories_table(self) -> AccessoriesTable:
        return self._accessories_table

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
    def platings_table(self) -> PlatingsTable:
        return self._platings_table

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
    def resources_table(self) -> ResourcesTable:
        return self._resources_table

    @property
    def families_table(self) -> FamiliesTable:
        return self._families_table

    @property
    def genders_table(self) -> GendersTable:
        return self._genders_table

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
    def bundle_covers_table(self) -> BundleCoversTable:
        return self._bundle_covers_table

    @property
    def transition_branches_table(self) -> TransitionBranchesTable:
        return self._transition_branches_table

    @property
    def adhesives_table(self) -> AdhesivesTable:
        return self._adhesives_table

    @property
    def protections_table(self) -> ProtectionsTable:
        return self._protections_table

    @property
    def shapes_table(self) -> ShapesTable:
        return self._shapes_table

    @property
    def transitions_table(self) -> TransitionsTable:
        return self._transitions_table

    @property
    def splices_table(self) -> SplicesTable:
        return self._splices_table

    @property
    def models3d_table(self) -> Models3DTable:
        return self._models3d_table

    @property
    def wire_markers_table(self) -> WireMarkersTable:
        return self._wire_markers_table

    @property
    def splice_types_table(self) -> SpliceTypesTable:
        return self._splice_types_table

    def _setup_new_db(self):
        # self.connector.execute('PRAGMA foreign_keys = ON;')
        # self.connector.commit()

        from ..setup_db import create_tables

        funcs = (
            create_tables.resources,
            create_tables.manufacturers,
            create_tables.temperatures,
            create_tables.genders,
            create_tables.protections,
            create_tables.adhesives,
            create_tables.cavity_locks,
            create_tables.colors,
            create_tables.directions,
            create_tables.ip_fluids,
            create_tables.ip_solids,
            create_tables.ip_supps,
            create_tables.platings,
            create_tables.materials,
            create_tables.shapes,
            create_tables.series,
            create_tables.families,
            create_tables.ip_ratings,
            create_tables.accessories,
            create_tables.transition_series,
            create_tables.transitions,
            create_tables.transition_branches,
            create_tables.boots,
            create_tables.bundle_covers,
            create_tables.covers,
            create_tables.cpa_locks,
            create_tables.tpa_locks,
            create_tables.seal_types,
            create_tables.seals,
            create_tables.wire_markers,
            create_tables.wires,
            create_tables.terminals,
            create_tables.splice_types,
            create_tables.splices,
            create_tables.models3d,
            create_tables.housings,
            create_tables.cavities,
            create_tables.housing_crossref,
            create_tables.terminal_crossref,
            create_tables.seal_crossref,
            create_tables.cover_crossref,
            create_tables.boot_crossref,
            create_tables.tpa_lock_crossref,
            create_tables.cpa_lock_crossref,
            create_tables.projects,
            create_tables.pjt_points_3d,
            create_tables.pjt_points_2d,
            create_tables.pjt_circuits,
            create_tables.pjt_bundle_layouts,
            create_tables.pjt_wire3d_layouts,
            create_tables.pjt_wire2d_layouts,
            create_tables.pjt_bundles,
            create_tables.pjt_seals,
            create_tables.pjt_cpa_locks,
            create_tables.pjt_tpa_locks,
            create_tables.pjt_splices,
            create_tables.pjt_housings,
            create_tables.pjt_cavities,
            create_tables.pjt_terminals,
            create_tables.pjt_transitions,
            create_tables.pjt_wire_markers,
            create_tables.pjt_wires
        )

        for func in funcs:
            func(self.connector, self.connector)

        from ..setup_db import load_database

        funcs = [
            load_database.tpa_locks,
            load_database.cpa_locks,
            load_database.boots,
            load_database.terminals,
            load_database.covers,
            load_database.seals,
            load_database.transitions,
            load_database.bundle_covers,
            load_database.housings,
            load_database.splices,
            load_database.wire_markers,
            load_database.wires
        ]

        for func in funcs:
            try:
                func(self.connector, self.connector)
            except FileNotFoundError:
                continue
            except:
                print(func)
                raise
