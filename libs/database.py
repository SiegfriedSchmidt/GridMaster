import sqlite3 as sql


class Database:
    def __init__(self, path: str, clear=False):
        self.con = sql.connect(path)
        self.cur = self.con.cursor()
        self.init(clear)

    def init(self, clear):
        if clear:
            self.drop_table()
        self.create_tables()

    def show_tables(self):
        return self.cur.execute("SELECT name FROM sqlite_master").fetchall()

    def create_tables(self):
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS code (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content LONGTEXT NOT NULL 
        );
        ''')

    def drop_table(self):
        self.cur.execute('DROP TABLE code')

    def save_code(self, content: str):
        self.cur.execute("INSERT INTO code (content) VALUES(?)", [content])
        self.con.commit()
        return self.cur.lastrowid

    def get_all(self):
        return list(map(lambda a: int(a[0]), self.cur.execute("SELECT id FROM code").fetchall()))

    def load_code(self, index):
        res = self.cur.execute("SELECT * FROM code WHERE id=?", str(index)).fetchone()
        if res:
            return res[1]
        else:
            return res


if __name__ == '__main__':
    db = Database('../gridmaster.db')
    print(db.get_all())
