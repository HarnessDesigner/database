from .base import BaseMixin


class GenderMixin(BaseMixin):

    @property
    def gender(self) -> "_gender.Gender":
        gender_id = self._table.select('gender_id', id=self._db_id)
        return _gender.Gender(self._table.db.genders_table, gender_id[0][0])

    @gender.setter
    def gender(self, value: "_gender.Gender"):
        self._table.update(self._db_id, gender_id=value.db_id)

    @property
    def gender_id(self) -> int:
        return self._table.select('gender_id', id=self._db_id)[0][0]

    @gender_id.setter
    def gender_id(self, value: int):
        self._table.update(self._db_id, gender_id=value)


from .. import gender as _gender  # NOQA
