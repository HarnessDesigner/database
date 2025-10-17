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

    def __init__(self, db: "GlobalDB"):
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

    def insert(self, **kwargs) -> int:
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
            self._con.execute(cmd)
        else:
            self._con.execute(cmd, params)

    def fetchall(self):
        return self._con.fetchall()


from .boot import BootsTable  # NOQA
from .wire import WiresTable  # NOQA
from .cover import CoversTable  # NOQA
from .seal import SealsTable  # NOQA
from .datasheet import DatasheetsTable  # NOQA
from .manufacturer import ManufacturersTable  # NOQA
from .tpa_lock import TPALocksTable  # NOQA
from .cpa_lock import CPALocksTable  # NOQA
from .material import MaterialsTable  # NOQA
from .image import ImagesTable  # NOQA
from .direction import DirectionsTable  # NOQA
from .terminal import TerminalsTable  # NOQA
from .series import SeriesTable  # NOQA
from .housing import HousingsTable  # NOQA
from .color import ColorsTable  # NOQA
from .sealing import SealingsTable  # NOQA
from .temperature import TemperaturesTable  # NOQA
from .cad import CADsTable  # NOQA
from .cavity import CavitiesTable  # NOQA
from .cavity_lock import CavityLocksTable  # NOQA
from .cavity_map import CavityMapsTable  # NOQA
from .family import FamiliesTable  # NOQA
from .gender import GendersTable  # NOQA
from .ip import IPRatingsTable  # NOQA
from .ip.fluid import IPFluidsTable  # NOQA
from .ip.solid import IPSolidsTable  # NOQA
from .ip.supp import IPSuppsTable  # NOQA
from .protection.bundle.series import BundleCoverSeriesTable  # NOQA
from .protection.bundle.resistant import BundleCoverResistancesTable  # NOQA
from .protection.bundle.material import BundleCoverMaterialsTable  # NOQA
from .protection.bundle.rigidity import BundleCoverRigiditiesTable  # NOQA
from .protection.bundle import BundleCoversTable  # NOQA
from .protection.transition.shape import TransitionShapesTable  # NOQA
from .protection.transition.layout import TransitionLayoutsTable  # NOQA
from .protection.transition.branch import TransitionBranchesTable  # NOQA
from .protection.transition.adhesive import TransitionAdhesivesTable  # NOQA
from .protection.transition.size import TransitionSizesTable  # NOQA
from .protection.transition.material import TransitionMaterialsTable  # NOQA
from .protection.transition.series import TransitionSeriesTable  # NOQA
from .protection.transition.family import TransitionFamiliesTable  # NOQA
from .protection.transition.protection import TransitionProtectionsTable  # NOQA
from .protection.transition import TransitionsTable  # NOQA


class GlobalDB:

    def __init__(self, mainframe: "_ui.MainFrame"):
        self.mainframe = mainframe

        self.connector = mainframe.db_connector

        self._boots_table = BootsTable(self)
        self._manufacturers_table = ManufacturersTable(self)
        self._tpa_locks_table = TPALocksTable(self)
        self._cpa_locks_table = CPALocksTable(self)
        self._materials_table = MaterialsTable(self)
        self._covers_table = CoversTable(self)
        self._housings_table = HousingsTable(self)
        self._seals_table = SealsTable(self)
        self._series_table = SeriesTable(self)
        self._terminals_table = TerminalsTable(self)
        self._wires_table = WiresTable(self)
        self._cavity_locks_table = CavityLocksTable(self)
        self._colors_table = ColorsTable(self)
        self._directions_table = DirectionsTable(self)
        self._cads_table = CADsTable(self)
        self._datasheets_table = DatasheetsTable(self)
        self._families_table = FamiliesTable(self)
        self._genders_table = GendersTable(self)
        self._images_table = ImagesTable(self)
        self._sealings_table = SealingsTable(self)
        self._temperatures_table = TemperaturesTable(self)
        self._ip_solids_table = IPSolidsTable(self)
        self._ip_fluids_table = IPFluidsTable(self)
        self._ip_supps_table = IPSuppsTable(self)
        self._ip_ratings_table = IPRatingsTable(self)
        self._cavities_table = CavitiesTable(self)
        self._cavity_maps_table = CavityMapsTable(self)
        self._bundle_cover_series_table = BundleCoverSeriesTable(self)
        self._bundle_cover_resistances_table = BundleCoverResistancesTable(self)
        self._bundle_cover_materials_table = BundleCoverMaterialsTable(self)
        self._bundle_cover_rigidities_table = BundleCoverRigiditiesTable(self)
        self._bundle_covers_table = BundleCoversTable(self)
        self._transition_branches_table = TransitionBranchesTable(self)
        self._transition_adhesives_table = TransitionAdhesivesTable(self)
        self._transition_sizes_table = TransitionSizesTable(self)
        self._transition_materials_table = TransitionMaterialsTable(self)
        self._transition_series_table = TransitionSeriesTable(self)
        self._transition_families_table = TransitionFamiliesTable(self)
        self._transition_protections_table = TransitionProtectionsTable(self)
        self._transition_shapes_table = TransitionShapesTable(self)
        self._transition_layouts_table = TransitionLayoutsTable(self)
        self._transitions_table = TransitionsTable(self)

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

    def _setup_new_db(self):
        self.connector.execute('PRAGMA foreign_keys = ON;')
        self.connector.commit()

        from . import create_db

        create_db.create_tables(self.connector)
        # create_db.preload_database(self.connector)
        # create_db.load_tpa_locks(self.connector)
        # create_db.load_cpa_locks(self.connector)
        # create_db.load_covers(self.connector)
        # create_db.load_seals(self.connector)
        # create_db.load_terminals(self.connector)
        # create_db.load_housings(self.connector)
        # create_db.load_cavity_maps(self.connector)
        # create_db.load_transitions(self.connector)
        # create_db.load_shrink_tube(self.connector)
