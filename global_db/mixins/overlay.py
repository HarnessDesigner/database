from . import BaseMixin


class OverlayMixin(BaseMixin):

    @property
    def overlay(self) -> "_image.Image":
        image_id = self._table.select('overlay_id', id=self._db_id)
        return _image.Image(self._table.db.images_table, image_id[0])

    @overlay.setter
    def overlay(self, value: "_image.Image"):
        self._table.update(self._db_id, overlay_id=value.db_id)

    @property
    def overlay_id(self) -> int:
        return self._table.select('overlay_id', id=self._db_id)[0][0]

    @overlay_id.setter
    def overlay_id(self, value: int):
        self._table.update(self._db_id, overlay_id=value)


from .. import image as _image  # NOQA
