import sqlite3
import pandas as pd
conn = sqlite3.connecSt('logs/audit_trail.db')
df = pd.read_sql_query("SELECT * FROM audit_log", conn)
print(df)
conn.close()


