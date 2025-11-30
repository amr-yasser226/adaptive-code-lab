from DB.Creating_DB import get_tables_names
from DB.connection import connect_db
tables=get_tables_names()
print(tables) 


# conn = connect_db()
# cursor = conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS peer_reviews;")
# conn.commit()
# conn.close()