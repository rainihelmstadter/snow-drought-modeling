"""
This script contains functions that are used to select and download PRISM climate data, 
either in point location or full raster format.

It contains X functions:
* water_year_dates: Generate daily dates for Oct-Jun of given water year
* get_prism_rasters: Download PRISM rasters for given dates and variables
"""

# Library Imports

import glob
from datetime import datetime, timedelta # calculate dates
import geopandas as gpd
import os
import pandas as pd
import requests
import rioxarray as rxr
import time
from tqdm import tqdm
import xarray as xr 
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

def get_prism_rasters(dates, resolution, download_dir, variables):
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

def crop_prism_rasters(prism_dir, study_gdf):
    '''
    Crop CONUS-sized PRISM rasters to study area and save as a NetCDF.

    Args:
    -----
    prism_dir (str):
        Path to folder where PRISM rasters are stored
    study_gdf (geopandas.GeoDataFrame):
        gdf defining study area boundary to crop to
    
    Returns:
    prism_crop_da (xarray.DataArray)
    '''

    # reproject study_gdf CRS (currently in EPSG:4326) to raster CRS (EPSG:4269)
    if not study_gdf.crs == 'EPSG:4269':
        study_gdf = study_gdf.to_crs('EPSG:4269')


    # use open_mfdataset to wrangle all the prism rasters
    # open_mfdataset looks at multiple files (the mf in the name) and can load them into one variable, 
    # but not all at once, so that the computer doesn't crash
    raw_rasters = xr.open_mfdataset(
        # grab all netCDF files in the raw raster directory
        f'{prism_dir}/*.nc', 
        # look at header information and combine each netCDF by coords (lat, lon, time, etc)
        combine='by_coords', 
        # use multiple CPU cores to run this
        parallel=True
        )
    
    # set area bounding box for initial crop
    xmin, ymin, xmax, ymax = study_gdf.total_bounds

    # select raster data within bounding box
    bbox = raw_rasters.sel(
        lon = slice(xmin, xmax),
        # PRISM lats are max to min because PRISM data is stored North to South (according to Gemini - check this)
        lat = slice(ymax, ymin)
    )

    # load data within bounding box into memory
    print('Cropping PRISM rasters to bounding box')
    prism_bbox_da = bbox.compute()
    print('Bounding box crop complete!')

    # set da CRS and geospatial components
    prism_bbox_da.rio.write_crs('EPSG:4269', inplace=True)
    prism_bbox_da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)

    # clip to exact study area bounds and reproject to match other data types
    crop_da = prism_bbox_da.rio.clip(study_gdf.geometry, study_gdf.crs, drop=True)
    prism_crop_da = crop_da.rio.to_crs('EPSG:4326')
    prism_crop_da = prism_crop_da.rename({'x': 'lon', 'y': 'lat'})

    return prism_crop_da

#----------------------------------------------------------------

def clean_prism_data(prism_da):
    '''
    This function will clean, standardize, and streamline the PRISM 
    data before it gets saved for use in later notebooks.

    The workflow is as follows:
    1. Clean of NaNs and physically impossible values
    2. Standardize datetime
    3. Set variables to float32
    4. Set chunking strategy for future loading

    Args:
    -----
    prism_crop_da (xarray.DataArray):
        array of prism rasters cropped to study area

    Returns:
    --------
    prism_clean_da (xarray.DataArray):
        array of prism rasters that's been cleaned and prepped
    '''