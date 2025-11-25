import duckdb

DB_CON = duckdb.connect(database=":memory:", read_only=False)
