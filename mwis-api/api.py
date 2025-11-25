from fastapi import FastAPI

from database.database import DB_CON

app = FastAPI()
db_con = DB_CON


# TODO: add query params for region, day, info of interest
@app.get("/forecasts")
def retrieve_forecast(db_con):
    return db_con.execute(
        """
        SELECT * FROM forecasts;
        """
    ).fetchall()
