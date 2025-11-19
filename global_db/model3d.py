from typing import Iterable as _Iterable

import io
import requests
import zipfile

from . import EntryBase, TableBase
from ...geometry import angle as _angle
from ...geometry import point as _point
from ...wrappers.decimal import Decimal as _decimal


class Models3DTable(TableBase):
    __table_name__ = 'models3d'

    def __iter__(self) -> _Iterable["Model3D"]:

        for db_id in TableBase.__iter__(self):
            yield Model3D(self, db_id)

    def __getitem__(self, item) -> "Model3D":
        if isinstance(item, int):
            if item in self:
                return Model3D(self, item)
            raise IndexError(str(item))
        raise KeyError(item)

    def insert(self, angle: _angle.Angle, idx: int, offset: _point.Point, data: bytes | None) -> "Model3D":
        db_id = TableBase.insert(self, angle=str(list(angle.as_float)), idx=idx,
                                 offset=str(list(offset.as_float)), data=data)

        return Model3D(self, db_id)


class Model3D(EntryBase):
    _table: Models3DTable = None

    @property
    def angle(self) -> _angle.Angle:
        value = eval(self._table.select('angle', id=self._db_id)[0][0])

        return _angle.Angle(*[_decimal(item) for item in value])

    @angle.setter
    def angle(self, value: _angle.Angle):
        self._table.update(self._db_id, angle=str(list(value.as_float)))

    @property
    def offset(self) -> _point.Point:
        value = eval(self._table.select('offset', id=self._db_id)[0][0])
        return _point.Point(*[_decimal(item) for item in value])

    @offset.setter
    def offset(self, value:  _point.Point):
        self._table.update(self._db_id, offset=str(list(value.as_float)))

    @property
    def index(self) -> int:
        return self._table.select('idx', id=self._db_id)[0][0]

    @index.setter
    def index(self, value: int):
        self._table.update(self._db_id, idx=value)

    @property
    def type(self) -> str:
        return self._table.select('type', id=self._db_id)[0][0]

    @type.setter
    def type(self, value: str):
        self._table.update(self._db_id, type=value)

    def __get_resource(self, db_id):
        if db_id is None:
            return None

        resource = self._table.db.resources_table[db_id]
        return resource.data

    def __set_resource(self, db_id, value) -> int:
        if isinstance(value, (bytes, None)):
            if db_id is None:
                resource = self._table.db.resources_table.insert(path=None, data=value, type='')
                db_id = resource.db_id
            else:
                resource = self._table.db.resources_table[db_id]
                resource.data = value
        else:
            if db_id is None:
                resource = self._table.db.resources_table.insert(path=value, data=None, type='')
                db_id = resource.db_id
            else:
                resource = self._table.db.resources_table[db_id]
                if value.startswith('http'):
                    resource.http = value
                else:
                    resource.path = value
        return db_id

    @property
    def all_model_data(self):

        def _read_zip_file(zip_data):
            buf = io.BytesIO(zip_data)
            buf.seek(0)
            zf = zipfile.ZipFile(buf)
            files = {name: zf.read(name) for name in zf.namelist()}
            zf.close()
            buf.close()

            ret = []

            for fn, file_data in files.items():
                if len(fn) < 5:
                    continue
                if (
                    fn[-4:] not in ('zip', '.stl', '.stp') and
                    not fn.endswith('.step')
                ):
                    continue

                f_type_ = fn.rsplit('.', 1)[-1]
                ret.append((file_data, f_type_))

            return ret

        res = []

        data = self._table.select('data', id=self._db_id)[0][0]
        if data is None:
            return []

        if data.startswith(b'http'):
            if data[-4:] in (b'.stl', b'.stp') or data.endswith(b'.step'):
                maybe_zip = False
                is_zip = False
            else:
                maybe_zip = True
                if data[-4:] == b'.zip':
                    is_zip = True
                else:
                    is_zip = False

            response = requests.get(data)
            data = response.content

            if maybe_zip:
                content_type = response.headers.get('Content-Type', None)
                if not is_zip:
                    if content_type is None:
                        return []

                    if content_type.split(';')[0] != 'application/zip':
                        return []

                res = _read_zip_file(data)

        elif data[-4:] in (b'.stl', b'.stp') or data.endswith(b'.step'):
            f_type = data.rsplit(b'.', 1)[-1].decode('utf-8')

            try:
                with open(data, 'rb') as f:
                    res.append((f.read(), f_type))

            except OSError:
                pass

        elif data[-4:] == b'.zip':
            res = _read_zip_file(data)

        return res

    @property
    def data(self) -> bytes | None:
        data = self.all_model_data
        if not data:
            return None

        index = self.index

        if index >= len(data):
            return None

        return data[index][0]

    @data.setter
    def data(self, value: bytes | None):
        if value is not None:
            if (
                len(value) >= 5 and
                not value.startswith(b'http') and
                (value[-4:] in (b'.zip', b'.stl', b'.stp') or value.endswith(b'.step'))
            ):
                with open(value, 'wb') as f:
                    f.write(value)

        self._table.update(self._db_id, data=value)
