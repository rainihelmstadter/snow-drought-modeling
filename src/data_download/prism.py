"""
This script contains functions that are used to select and download PRISM climate data, 
either in point location or full raster format.

It contains X functions:
* water_year_dates: Generate daily dates for Oct-Jun of given water year
* make_station_csv: Makes a csv of station lat, lon, and names from GeoDataFrame of SNOTEL stations
* get_prism_for_stations: Download PRISM climate data for SNOTEL station locations DEPRACATED
"""

# Library Imports

import pandas as pd
from datetime import datetime, timedelta # calculate dates
import requests
import tqdm

# Functions

def water_year_dates(start_wy=1990, end_wy=2023):
    '''
    Generate daily dates for October-June of each water year.
    
    Args:
    -----
    start_wy (int):
        Start year (e.g. 1990)
    end_wy (int):
        End year (e.g. 2020)
    Returns:
    --------
    dates (list):
        Daily water year dates as list
    '''
    
    dates = []
    for wy in range(start_wy, end_wy + 1):
        start = datetime(wy - 1, 10, 1)   # Oct 1 of previous calendar year
        end = datetime(wy, 6, 1)          # Jun 1 of water year
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)
    return dates

#----------------------------------------------------------------

def make_station_csv(stations_gdf):
    '''
    Make a csv for PRISM bulk point submission from stations_gdf.
    PRISM format expects: lat, lon, stationTriplet
    
    Args:
    -----
    stations_gdf (GeoDataFrame): 
        Must have geometry (point) and 'stationTriplet' column
    
    Returns:
    --------
    str: CSV-formatted string of station coordinates
    '''
    rows = []
    for _, row in stations_gdf.iterrows():
        rows.append({
            "Latitude": round(row.geometry.y, 5),
            "Longitude": round(row.geometry.x, 5),
            "Name": row["stationTriplet"]
        })
    return pd.DataFrame(rows).to_csv(index=False)

#----------------------------------------------------------------

def get_prism_for_stations(stations_gdf, wy_dates, variables):
    '''
    Download daily PRISM climate variables for given time range, variables,
    and SNOTEL stations(s).

    Args:
    -----
    stations_gdf (GeoDataFrame):
        gdf of SNOTEL stations. 
        Must include lat, lon, and station triplet for each station.
    wy_dates (list):
        List of daily water year dates (can include multiple years)
    variables (list):
        List of variables of interest.

    Returns:
    --------
    sntl_prism (pd.DataFrame): 
        Results of PRISM API query in format: [stationTriplet, date, ppt (precip), tmin, tmax, water_year]
    '''

    # Set endpoint
    url = "https://prism.oregonstate.edu/explorer/bulk.php",
    
    # Format variables
    stats_str = " ".join(variables)

    # initialize df/da/ds
    results = []

    # loop through water years and stations
    for start_date, end_date, wy in tqdm(wy_dates, desc="Water Year"):
        for _, station in stations_gdf.iterrows:

            # set parameters
            params = {
                "stats": stats_str,
                "units": "si",
                "range": "daily",
                "start": start_date.strftime("%Y%m%d"),   # YYYYMMDD
                "end": end_date.strftime("%Y%m%d"),
                "lon": round(station.geometry.x, 5),
                "lat": round(station.geometry.y, 5),
                "elev": round(station["elevation"]),
                "call": "pp/daily_timeseries",
            }

            try:
                response = requests.get(url, params = params, timeout=60)
                response.raise_for_status

            # Warning flags
            except requests.exceptions.Timeout:
                print(f"Timeout: {station['name']} WY{wy}")
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error: {station['name']} WY{wy} — {e}")
            except Exception as e:
                print(f"Unexpected error: {station['name']} WY{wy} — {e}")
    
    # Warning if function doesn't work
    if not results:
        print("No data returned — check endpoint, parameters, and units flag")
        return None

    # Concat results into one big DF
    sntl_prism = pd.concat(results, ignore_index = True)
    return sntl_prism

#----------------------------------------------------------------

def make_prism_urls(wy_dates, variables):
    '''
    Define a set of urls to download PRISM rasters.

    Args:
    -----
    wy_dates (list):
        List of dates desired for download
    variables (list):
        List of desired variables

    Returns:
    --------
    prism_urls (list):
        List of valid urls
    '''

    # define base url
    url = 'http://services.nacse.org/prism/data/get/us/4km/'

def get_prism_rasters(prism_urls, download_dir):
    '''
    Download PRISM rasters
    '''