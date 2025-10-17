
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

    def __init__(self, db: "PJTTables", project_id: int | None = None):
        self.db = db
        self.project_id = project_id

        self._con = db.con
        self._cur = db.cur

    def __getitem__(self, item):
        self._cur.execute(f'SELECT * FROM {self.__table_name__} WHERE id = {item};')

        for line in self._cur.fetchall():
            return line

    def __iter__(self) -> _Iterable[int]:
        if self.project_id is None:
            self._cur.execute(f'SELECT id FROM {self.__table_name__};')
        else:
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
        fields = []
        values = []
        args = []

        if self.project_id is not None:
            fields.append('project_id')
            values.append('?')
            args.append(self.project_id)

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

        values = []

        if self.project_id is not None:
            values.append(f'project_id = {self.project_id}')

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


from .pjt_bundle import PJTBundlesTable  # NOQA
from .pjt_bundle_layout import PJTBundleLayoutsTable  # NOQA
from .pjt_circuit import PJTCircuitsTable  # NOQA
from .pjt_coordinate_2d import PJTCoordinates2DTable  # NOQA
from .pjt_coordinate_3d import PJTCoordinates3DTable  # NOQA
from .pjt_housing import PJTHousingsTable  # NOQA
from .pjt_splice import PJTSplicesTable  # NOQA
from .pjt_transition import PJTTransitionsTable  # NOQA
from .pjt_wire import PJTWiresTable  # NOQA
from .pjt_wire2d_layout import PJTWire2DLayoutsTable  # NOQA
from .pjt_wire3d_layout import PJTWire3DLayoutsTable  # NOQA
from .pjt_cavity_map import PJTCavityMapsTable  # NOQA
from .pjt_cavity import PJTCavitiesTable  # NOQA
from .pjt_terminal import PJTTerminalsTable  # NOQA

from .project import ProjectsTable  # NOQA


class PJTTables:

    def __init__(self, global_db, connector):
        self.global_db = global_db

        self.connector = connector
        self.con = connector.con
        self.cur = connector.cur

        self._projects_table = ProjectsTable(self)

        self._pjt_bundles_table = None
        self._pjt_bundle_layouts_table = None
        self._pjt_circuits_table = None
        self._pjt_coordinates_2d_table = None
        self._pjt_coordinates_3d_table = None
        self._pjt_housings_table = None
        self._pjt_splices_table = None
        self._pjt_transitions_table = None
        self._pjt_wires_table = None
        self._pjt_wire_2d_layouts_table = None
        self._pjt_wire_3d_layouts_table = None
        self._pjt_cavities_table = None
        self._pjt_cavity_maps_table = None
        self._pjt_terminals_table = None

    def load(self, project_id):
        self._pjt_bundles_table = PJTBundlesTable(self, project_id)
        self._pjt_bundle_layouts_table = PJTBundleLayoutsTable(self, project_id)
        self._pjt_circuits_table = PJTCircuitsTable(self, project_id)
        self._pjt_coordinates_2d_table = PJTCoordinates2DTable(self, project_id)
        self._pjt_coordinates_3d_table = PJTCoordinates3DTable(self, project_id)
        self._pjt_housings_table = PJTHousingsTable(self, project_id)
        self._pjt_splices_table = PJTSplicesTable(self, project_id)
        self._pjt_transitions_table = PJTTransitionsTable(self, project_id)
        self._pjt_wires_table = PJTWiresTable(self, project_id)
        self._pjt_wire_2d_layouts_table = PJTWire2DLayoutsTable(self, project_id)
        self._pjt_wire_3d_layouts_table = PJTWire3DLayoutsTable(self, project_id)
        self._pjt_cavities_table = PJTCavitiesTable(self, project_id)
        self._pjt_cavity_maps_table = PJTCavityMapsTable(self, project_id)
        self._pjt_terminals_table = PJTTerminalsTable(self, project_id)

    @property
    def pjt_bundles_table(self) -> PJTBundlesTable:
        return self._pjt_bundles_table

    @property
    def pjt_bundle_layouts_table(self) -> PJTBundleLayoutsTable:
        return self._pjt_bundle_layouts_table

    @property
    def pjt_circuits_table(self) -> PJTCircuitsTable:
        return self._pjt_circuits_table

    @property
    def pjt_coordinates_2d_table(self) -> PJTCoordinates2DTable:
        return self._pjt_coordinates_2d_table

    @property
    def pjt_coordinates_3d_table(self) -> PJTCoordinates3DTable:
        return self._pjt_coordinates_3d_table

    @property
    def pjt_housings_table(self) -> PJTHousingsTable:
        return self._pjt_housings_table

    @property
    def pjt_splices_table(self) -> PJTSplicesTable:
        return self._pjt_splices_table

    @property
    def pjt_transitions_table(self) -> PJTTransitionsTable:
        return self._pjt_transitions_table

    @property
    def pjt_wires_table(self) -> PJTWiresTable:
        return self._pjt_wires_table

    @property
    def pjt_wire_2d_layouts_table(self) -> PJTWire2DLayoutsTable:
        return self._pjt_wire_2d_layouts_table

    @property
    def pjt_wire_3d_layouts_table(self) -> PJTWire3DLayoutsTable:
        return self._pjt_wire_3d_layouts_table

    @property
    def projects_table(self) -> ProjectsTable:
        return self._projects_table

    @property
    def pjt_cavities_table(self) -> PJTCavitiesTable:
        return self._pjt_cavities_table

    @property
    def pjt_cavity_maps_table(self) -> PJTCavityMapsTable:
        return self._pjt_cavity_maps_table

    @property
    def pjt_terminals_table(self) -> PJTTerminalsTable:
        return self._pjt_terminals_table



circuits
id, circuit_num, name, description

terminals
id, project_id, part_id, cavity_id, seal_id, circuit_id, coord3d_id, coord2d_id


cavities
id, project_id, part_id, cavity_map_id, terminal_id, name

cavity_maps
id, project_id, part_id, housing_id


housings
id, project_id, part_id, name, coords3d_id, coords2d_id, x_angle_3d, y_angle_3d, z_angle_3d, angle_2d, seal_ids, cpa_lock_ids, tpa_lock_ids, cover_id, boot_id, accessory_ids


coordinates_2d
id, project_id, x, y

coordinates_3d
id, project_id, x, y, z

transitions
id, project_id, part_id, name, branch1_coord_id, branch2_coord_id, branch3_coord_id, branch4_coord_id, branch5_coord_id, branch6_coord_id, angle_x, angle_y, angle_z

bundle_layouts
id, project_id, coord_id,

bundles
id, project_id, part_id, start_coord_id, stop_coord_id

wire2d_layouts
id, project_id, coord_id

wire3d_layouts
id, project_id, coord_id

splices
id, project_id, part_id, circuit_id, coord3d_id, coord2d_id

wires
id, project_id, part_id, circuit_id, start_coord3d_id, stop_coord3d_id, start_coord2d_id, stop_coord2d_id, is_visible
