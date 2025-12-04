import sqlite3
def create_database():
    conn=sqlite3.connect('/home/omar-hazem/projects/SWE Project/src/DB/Accl_DB.db') 
    conn.close()

def get_tables_names():
    conn=sqlite3.connect('/home/omar-hazem/projects/SWE Project/src/DB/Accl_DB.db')
    c=conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return tables

