from datatables import ColumnDT

class Error(Exception):
    pass

class ModelIsNotSetError(Error):
    pass

class ColumnManager:
    def __init__(self, model, **kwargs):
        self.model = model
        self.drop_column_ids = kwargs.get('drop_column_ids', [])
        self.titles_map = kwargs.get('titles_map', 
            dict([(c.name, c.comment) for c in self.model.__table__.columns]))

    def get_ids(self):
        columns = self.model.__table__.columns
        column_ids = [c.name for c in self.model.__table__.columns]
        return list(filter(lambda col_id: col_id not in self.drop_column_ids, column_ids))

    @property
    def ids(self):
        return self.get_ids()

    def get_titles(self):
        return [self.titles_map[col_id] if col_id in self.titles_map else col_id for col_id in self.get_ids()]

    @property
    def titles(self):
        return self.get_titles()

    def get_columns(self):
        return [getattr(self.model, col_id) for col_id in self.get_ids()]

    @property
    def columns(self):
        return self.get_columns()

    def get_dt_columns(self):
        return [ColumnDT(m) for m in self.get_columns()]

    @property
    def dt_columns(self):
        return self.get_dt_columns()


