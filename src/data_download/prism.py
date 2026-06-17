"""
This script contains functions that are used to select and download PRISM climate data, 
either in point location or full raster format.

It contains X functions:
* water_year_dates: Generate daily dates for Oct-Jun of given water year
* make_station_csv: Makes a csv of station lat, lon, and names from GeoDataFrame of SNOTEL stations
* get_prism_for_stations: Download PRISM climate data for SNOTEL station locations DEPRACATED
"""

# Library Imports

import glob
import pandas as pd
from datetime import datetime, timedelta # calculate dates
import os
import requests
import time
from tqdm import tqdm
import zipfile

from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Functions

def water_year_dates(start_wy, end_wy):
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

# def make_station_csv(stations_gdf):
#     '''
#     Make a csv for PRISM bulk point submission from stations_gdf.
#     PRISM format expects: lat, lon, stationTriplet
    
#     Args:
#     -----
#     stations_gdf (GeoDataFrame): 
#         Must have geometry (point) and 'stationTriplet' column
    
#     Returns:
#     --------
#     str: CSV-formatted string of station coordinates
#     '''
#     rows = []
#     for _, row in stations_gdf.iterrows():
#         rows.append({
#             "Latitude": round(row.geometry.y, 5),
#             "Longitude": round(row.geometry.x, 5),
#             "Name": row["stationTriplet"]
#         })
#     return pd.DataFrame(rows).to_csv(index=False)

# #----------------------------------------------------------------

# def get_prism_for_stations(stations_gdf, dates, variables):
#     '''
#     Download daily PRISM climate variables for given time range, variables,
#     and SNOTEL stations(s).

#     Args:
#     -----
#     stations_gdf (GeoDataFrame):
#         gdf of SNOTEL stations. 
#         Must include lat, lon, and station triplet for each station.
#     dates (list):
#         List of daily water year dates (can include multiple years)
#     variables (list):
#         List of variables of interest.

#     Returns:
#     --------
#     sntl_prism (pd.DataFrame): 
#         Results of PRISM API query in format: [stationTriplet, date, ppt (precip), tmin, tmax, water_year]
#     '''

#     # Set endpoint
#     url = "https://prism.oregonstate.edu/explorer/bulk.php",
    
#     # Format variables
#     stats_str = " ".join(variables)

#     # initialize df/da/ds
#     results = []

#     # loop through water years and stations
#     for start_date, end_date, wy in tqdm(dates, desc="Water Year"):
#         for _, station in stations_gdf.iterrows:

#             # set parameters
#             params = {
#                 "stats": stats_str,
#                 "units": "si",
#                 "range": "daily",
#                 "start": start_date.strftime("%Y%m%d"),   # YYYYMMDD
#                 "end": end_date.strftime("%Y%m%d"),
#                 "lon": round(station.geometry.x, 5),
#                 "lat": round(station.geometry.y, 5),
#                 "elev": round(station["elevation"]),
#                 "call": "pp/daily_timeseries",
#             }

#             try:
#                 response = requests.get(url, params = params, timeout=60)
#                 response.raise_for_status

#             # Warning flags
#             except requests.exceptions.Timeout:
#                 print(f"Timeout: {station['name']} WY{wy}")
#             except requests.exceptions.HTTPError as e:
#                 print(f"HTTP error: {station['name']} WY{wy} — {e}")
#             except Exception as e:
#                 print(f"Unexpected error: {station['name']} WY{wy} — {e}")
    
#     # Warning if function doesn't work
#     if not results:
#         print("No data returned — check endpoint, parameters, and units flag")
#         return None

#     # Concat results into one big DF
#     sntl_prism = pd.concat(results, ignore_index = True)
#     return sntl_prism

#----------------------------------------------------------------

def get_prism_snow_rasters(dates, resolution, download_dir, variables):
    '''
    Downloads CONUS PRISM daily data for a given set of dates and variables.
    Stores rasters as netCDF files.

    Args:
    -----
    dates (list):
        List of dates desired for download
    resolution (str):
        Desired resolution of PRISM rasters (800m, 4km)
    download_dir (str):
        Directory for downloaded files.
    variables (list):
        Variables of interest. e.g. ['ppt', 'tmin', 'tmax']
    
    Returns:
    --------
    downloads files to disk
    downloaded_files (list):
        List of filepaths for downloaded rasters    
    '''

    # Base URL for the updated PRISM REST API
    base_url = f"https://services.nacse.org/prism/data/get/us/{resolution}"
    session = requests.Session()

    # retry downloads in case of network interrupts
    session = requests.Session()
    retries = Retry(
        total=5,                # Total number of retries before giving up
        backoff_factor=2,       # Wait 2s, 4s, 8s, 16s between retries
        status_forcelist=[500, 502, 503, 504], # Retry on standard server hiccups
        raise_on_status=False   # Let raise_for_status() handle error parsing
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    # track files that have been downloaded
    downloaded_files = []

    # count the number of tasks to complete for tqdm progress bar
    total_tasks = [(var, date) for var in variables for date in dates]

    # loop through variables
    for var, date in tqdm(total_tasks, desc='Processing PRISM Rasters', unit='file'):
        # # print variable monitor
        # print(f"\n--- Fetching all requested dates for {var.upper()} ---")

        # # loop through dates
        # for date in dates:
        # set date string for url
        date_str = date.strftime("%Y%m%d")
        # make url
        url = f'{base_url}/{var}/{date_str}?format=nc'

        # check if file has already been downloaded
        pattern = os.path.join(download_dir, f"prism_{var}_*_{date_str}*.nc")
        existing_files = glob.glob(pattern)

        # Check for existing files; if yes, skip download
        # PRISM will lock files if there are more than two attempted downloads per day
        if existing_files:
            print(f'File for {var} on {date} already exists. Skipping download.')
            downloaded_files.extend(existing_files)
            continue

        # otherwise, proceed
        # set download path for zip file
        zip_path = os.path.join(download_dir, f'prism_{var}_us_{resolution}_{date_str}.zip')

        try:
            response = session.get(url, timeout=15)
            # Check HTTP error codes
            response.raise_for_status()

            # download zip file
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # extract zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)

            # delete zip file and auxiliary files
            os.remove(zip_path)
            for item in os.listdir(download_dir):
                if item.endswith(('.xml', '.txt', '.csv', '.stx')):
                    os.remove(os.path.join(download_dir, item))
            
            # locate extracted .tif file and append
            # this works if the file was just downloaded or earlier
            new_file = glob.glob(pattern)

            # append
            if new_file:
                downloaded_files.extend(new_file)
            
            # Rate-limiting pause to respect OSU's server bandwidth
            time.sleep(2.0)
            
        except requests.exceptions.HTTPError as e:
            print(f"Skipped {date_str} (HTTP Error): {e}")
        except Exception as e:
            print(f"Unexpected error for {date_str}: {e}")

    print("Download complete.")
    return downloaded_files

#----------------------------------------------------------------

def crop_prism_rasters():
    '''
    Crop CONUS-sized PRISM rasters to study area and save as a NetCDF.
    '''