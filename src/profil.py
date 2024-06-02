# import sqlite3
# from src.config import engine

# def deleteSqliteRecord(id):
#     try:
#         with engine.connect() as conn:
#             conn.execute(f"delete from profil where uid = '{id}'")
#         sqliteConnection = sqlite3.connect('')
#         cursor = sqliteConnection.cursor()
#         print("Connected to SQLite")

#         sql_update_query = """DELETE from SqliteDb_developers where id = ?"""
#         cursor.execute(sql_update_query, (id,))
#         sqliteConnection.commit()
#         print("Record deleted successfully")

#         cursor.close()

#     except sqlite3.Error as error:
#         print("Failed to delete reocord from a sqlite table", error)
#     finally:
#         if sqliteConnection:
#             sqliteConnection.close()
#             print("sqlite connection is closed")