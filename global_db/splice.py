

'''
    def __getitem__(self, item) -> "Shape":
        if isinstance(item, int):
            if item in self:
                return Shape(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', name=item)
        if db_id:
            return Shape(self, db_id[0][0])

        raise KeyError(item)


'''

class Splice:
    pass
