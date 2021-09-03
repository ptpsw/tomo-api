from functools import lru_cache
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Optional

import pymysql.cursors
from pymysql.connections import Connection

import config

app = FastAPI()

@lru_cache()
def get_settings():
    return config.Settings()

settings = get_settings()

def get_db():
    conn = pymysql.connect(
        host=settings.mysql_host, user=settings.mysql_user, 
        password=settings.mysql_pass, database=settings.mysql_db)
    try:
        yield conn
    finally:
        conn.close()

class StationLink(BaseModel):
    link_id: str
    link_name: Optional[str] = None
    source_station_id: str
    dest_station_id: str

class Station(BaseModel):
    station_id: str
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    station_links: List[StationLink]

@app.get("/")
async def root():
    return {"message": "Tomography API Server"}


@app.get("/stations", response_model=List[Station])
def get_all_stations(conn: Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute('SELECT station_id, name, lat, lon FROM stations;')
    results = cur.fetchall()
    stations_list = []
    if results:
        for row in results:
            id, name, lat, lon = row
            cur.execute("""
                SELECT link_id, link_name, source_station_id, dest_station_id
                FROM station_links
                WHERE source_station_id=%s OR dest_station_id=%s 
                """, (id, id)
            )
            links_result = cur.fetchall()
            if links_result:
                station_links = []
                for link in links_result:
                    link_id, link_name, source_id, dest_id = link
                    station_link = StationLink(
                        link_id = link_id,
                        link_name = link_name,
                        source_station_id = source_id,
                        dest_station_id = dest_id
                    )
                    station_links.append(station_link)
            station = Station(station_id=id, name=name, lat=lat, lon=lon, station_links=station_links)
            stations_list.append(station)
    return stations_list
    