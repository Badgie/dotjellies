import sqlite3

DB = 'static/db/jstat.db'


def get_recent_machine() -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT *, max(time) FROM machine')
    machine = c.fetchone()
    return list(machine[:len(machine) - 1])


def get_recent_machine_col(col: str) -> list:
    """
    Gets col(s) from machine database. {col} may be a comma separated array of cols.
    """
    query = f'SELECT MAX(time), {col} FROM machine'
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query)
    return c.fetchone()


def get_all_machine(cols: str) -> list:
    query = f'SELECT {cols} FROM machine'
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query)
    return c.fetchall()


def get_recent_cpu_pair() -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM cpu')
    cpus = c.fetchall()
    return cpus[len(cpus) - 10: len(cpus)]


def get_all_cpu() -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM cpu')
    return c.fetchall()


def get_recent_storage() -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM storage')
    drives = c.fetchall()
    m_stamp = max([x[0] for x in drives])
    return [x for x in drives if x[0] == m_stamp]
