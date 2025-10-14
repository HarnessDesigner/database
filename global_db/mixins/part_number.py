from . import BaseMixin


class PartNumberMixin(BaseMixin):

    @property
    def part_number(self) -> str:
        return self._table.select('part_number', id=self._db_id)[0][0]
