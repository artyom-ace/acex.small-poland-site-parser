import os
import sqlite3
import json
from datetime import date

from httpx import Cookies

from const import Good
from settings import db_path


# method to check or create local sqlite database
def check_or_create_db():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE settings(fname text NOT NULL PRIMARY KEY, fvalue text)''')
        c.execute('''CREATE TABLE goods(fid integer NOT NULL PRIMARY KEY, fscan_date date, fcode text, fname text, fprice real, fstatus text)''')
        c.execute('''create index goods__scan_date on goods(fscan_date)''')
        c.execute('''create index goods__code on goods(fcode)''')
        conn.commit()
        conn.close()


check_or_create_db()

db_con = sqlite3.connect(db_path)
db_cur = db_con.cursor()


def cookies_save(cookies: Cookies):
    db_cur.execute('DELETE FROM settings WHERE fname = "cookies"')
    db_cur.execute('INSERT INTO settings(fname, fvalue) VALUES(?, ?)',
                   ('cookies',  json.dumps({key: value for key, value in cookies.items()})))
    db_con.commit()


def cookies_load(cookies: Cookies):
    db_cur.execute('SELECT fvalue FROM settings WHERE fname = "cookies"')
    row = db_cur.fetchone()
    if row:
        cookies.clear()
        db_data = json.loads(row[0])
        for key, value in db_data.items():
            cookies[key] = value


def goods_save(goods: list[Good], scan_date: date):
    db_cur.execute('DELETE FROM goods where fscan_date = ?', (scan_date,))
    for good in goods:
        db_cur.execute('INSERT INTO goods(fscan_date, fcode, fname, fprice, fstatus) VALUES(?, ?, ?, ?)',
                       (scan_date, good.code, good.name, good.price, good.status))
    db_con.commit()


def goods_load(scan_date: date) -> list[Good]:
    db_cur.execute('SELECT fcode, fname, fprice, fstatus FROM goods where fscan_date = ? ORDER BY fcode', (scan_date,))
    result = []
    for row in db_cur.fetchall():
        result.append(Good(row[0], row[1], row[2], row[3]))
    return result
