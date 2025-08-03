class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_db(self):
        return self.db_url


def foo(t):
    return t
