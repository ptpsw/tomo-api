from functools import lru_cache
from os import times
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import pymysql.cursors
from pymysql.connections import Connection

import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@lru_cache()
def get_settings():
    return config.Settings()

settings = get_settings()

def get_db():
    conn = pymysql.connect(
        host=settings.mysql_host, port=settings.mysql_port, 
        user=settings.mysql_user, password=settings.mysql_pass, 
        database=settings.mysql_db)
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

class SDE(BaseModel):
    station_id: str
    timestamp: datetime
    sde: float

class SDR(BaseModel):
    station_id: str
    timestamp: datetime
    travel_time: float

class Temperature(BaseModel):
    station_link_id: int
    timestamp: datetime
    temperature: float

class Current(BaseModel):
    station_link_id: int
    timestamp: datetime
    current: float
    direction: Optional[float]

@app.get("/")
async def root():
    return {"message": "Tomography API Server"}


@app.get("/v0/stations", response_model=List[Station])
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
            station_links = []
            if links_result:
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

@app.get("/v0/sde/", response_model=List[SDE])
def get_sde_by_station(station_id: str, conn: Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute('SELECT station_id, timestamp, value FROM sde\
        WHERE station_id=%s', (station_id))
    results = cur.fetchall()
    sde_list = []
    print(len(results))
    if results:
        for row in results:
            station_id, timestamp, value = row
            sde = SDE(
                station_id = station_id,
                timestamp = timestamp,
                sde = value
            )
            sde_list.append(sde)
    return sde_list

@app.get("/v0/sdr/", response_model=List[SDR])
def get_sdr_by_station(station_id: str, conn: Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute('SELECT station_id, timestamp, value FROM sdr\
        WHERE station_id=%s', (station_id))
    results = cur.fetchall()
    sdr_list = []
    print(len(results))
    if results:
        for row in results:
            station_id, timestamp, value = row
            sdr = SDR(
                station_id = station_id,
                timestamp = timestamp,
                travel_time = value
            )
            sdr_list.append(sdr)
    return sdr_list
    
@app.get("/v0/temperature/", response_model=List[Temperature])
def get_temperature_by_station_link(station_link_id: int, conn: Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute('SELECT station_link_id, timestamp, value FROM temperature\
        WHERE station_link_id=%s', (station_link_id))
    results = cur.fetchall()
    temperature_list = []
    print(len(results))
    if results:
        for row in results:
            station_link_id, timestamp, value = row
            temp = Temperature(
                station_link_id = station_link_id,
                timestamp = timestamp,
                temperature = value
            )
            temperature_list.append(temp)
    return temperature_list

@app.get("/v0/current/", response_model=List[Current])
def get_current_by_station_link(station_link_id: int, conn: Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute('SELECT station_link_id, timestamp, value, direction FROM current\
        WHERE station_link_id=%s', (station_link_id))
    results = cur.fetchall()
    current_list = []
    print(len(results))
    if results:
        for row in results:
            station_link_id, timestamp, value, direction = row
            current = Current(
                station_link_id = station_link_id,
                timestamp = timestamp,
                current = value,
                direction = direction
            )
            current_list.append(current)
    return current_list