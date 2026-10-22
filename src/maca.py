'''
This script contains functions to download and process MACAv2 climate data. It contains the following functions:
* download_maca_data: Utilizes variables to access specific sections of the MACA dataset, download, preprocess, and save data to file.
'''

# Library Imports
import os
import pandas as pd
import numpy as np
import xarray as xr
import rioxarray as rxr
from tqdm import tqdm

import datetime as dt

#----------------------------------------------------------------

# convert temp from Kelvin to C function
def convert_K_to_C(da):
    '''
    Converts an xarray DataArray from Kelvin to Celcius 

    Args:
    da (DataArray):
        DA of temperature values
    '''

    # Perform conversion pixel-wise
    da_c = da - 273.15
    
    return da_c

#----------------------------------------------------------------

# convert longitude
def convert_longitude(longitude):

    '''
    This function cleans up datasets read from NetCDF files 
    in order to work with the other datasets used in this notebook.
    It converts lon from 0 to 360 to -180 to 180 

    Args:
    =====
    longitude (DataArray):
        DA from larger Dataset that contains longitude data

    Returns:
    ========
    longitude (DataArray)
    '''

    return xr.where(longitude > 180, longitude - 360, longitude )

#----------------------------------------------------------------

# Function to download MACA data
def download_maca_data(
        site_gdf, site_name,
        models, rcp_value,
        variables, 
        start_date, end_date,
        maca_dir):

    '''
    Downloads and processes MACA data for a given site.
    Processing includes clipping bounds and rewriting longitude values

    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    NEED TO ENSURE KELVIN CONVERSION AND LONGITUDE FIX HAPPENS HERE TOO
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    Args:
    =====
    site_gdf (geopandas.GeoDataFrame):
        Site boundary, used for clipping
    site_name (str):
        Name of site
    models (list):
        List of models to programmatically download
    rcp_value (str):
        RCP value for MACA url; can be 'historical' as well
    variables (str or list):
        Variable name or list of variables ('pr', 'tasmax', 'tasmin', etc.)
    start_date (str):
        Desired start date of downloaded dataset
        Format: 'YYYY-MM-DD'
    end_date (str):
        Desired end date of downloaded dataset
        Format: 'YYYY-MM-DD'
    maca_dir (str):
        Path for data to be saved
    '''

    # Initialize results list
    result_paths = []

    # count total steps for progress bar
    total_steps = len(models) * len(variables)

    # make a bounding box
    xmin, ymin, xmax, ymax = site_gdf.total_bounds

    # convert lon to 0-360 to match MACAv2 data standards, add a tiny buffer to preserve edge pixels
    min_lon_360 = (xmin - 0.05) + 360
    max_lon_360 = (xmax + 0.05) + 360

    # set fixed catalog years for the MACA url
    catalog_years = "1950_2005" if rcp_value == "historical" else "2006_2099"

    # Lookup for MACA's internal NetCDF variable names
    maca_var_names = {
        'tasmax': 'air_temperature',
        'tasmin': 'air_temperature',
        'pr': 'precipitation'
    }

    # download and process files
    with tqdm(total=total_steps, desc=f"Processing: ") as pbar:
        # loop through models
        for model in models:
            for variable in variables:
                # set tqdm update
                pbar.set_description(f"Processing: {model} ({variable})")

                # set opendap url to download from
                opendap_url = (f'http://thredds.northwestknowledge.net:8080/thredds/dodsC/'
                            f'agg_macav2metdata_{variable}_{model}_r1i1p1_{rcp_value}'
                            f'_{catalog_years}_CONUS_daily.nc')

                # set filename and path for model results
                file_name = f'maca_{variable}_{model}_{site_name}_{rcp_value}_{start_date}_{end_date}_CONUS_daily.nc'
                maca_path = os.path.join(maca_dir, file_name)   

                # Download or open file
                if not os.path.exists(maca_path):

                    # # Send progress warning
                    # print(f"{variable} - {model} - {start_date} - {end_date} has not been downloaded.")

                    # Load metadata for dataset
                    lazy_ds = xr.open_dataset(opendap_url, mask_and_scale = True)

                    # subset dataset on the server before downloading
                    subset_ds = lazy_ds.sel(
                        time = slice(start_date, end_date),
                        lon = slice(min_lon_360, max_lon_360),
                        # select lat regardless of direction it's counted
                        lat = slice(ymin - 0.05, ymax + 0.05) if lazy_ds.lat[0] < lazy_ds.lat[-1] else slice(ymin - 0.05, ymax + 0.05))

                    # compute request and download subset to RAM
                    maca_360_ds = subset_ds.compute()
                    
                    # drop unneeded dates
                    is_wy_season = (
                        maca_360_ds.time.dt.month >= 10) | (maca_360_ds.time.dt.month <= 5) | (
                        (maca_360_ds.time.dt.month == 6) & (maca_360_ds.time.dt.day == 1))
                    maca_360_wint_ds = maca_360_ds.sel(time=is_wy_season)
                    
                    # rename internal variable ('air_temperature'/'precipitation') to 'tasmax'/'tasmin'/'pr'
                    internal_name = list(maca_360_wint_ds.data_vars)[0]
                    maca_360_wint_ds = maca_360_wint_ds.rename({internal_name: variable})

                    # Standardize MACA ds lon back to -180 to 180
                    maca_ds = maca_360_wint_ds.assign_coords(lon=convert_longitude(maca_360_wint_ds.lon)).sortby('lon')

                    # Drop stale grid_mapping attributes that point to missing server coordinates
                    maca_ds[variable].attrs.pop('grid_mapping', None)

                    # convert K to C
                    if variable in ['tasmin', 'tasmax']:
                        maca_ds[variable] = convert_K_to_C(maca_ds[variable])

                    # Set spatial dims, CRS, and NaNs
                    maca_ds.rio.write_crs('EPSG:4326', inplace=True)
                    maca_ds.rio.set_spatial_dims(x_dim = 'lon', y_dim = 'lat', inplace=True)
                    maca_ds[variable].rio.write_nodata(np.nan, inplace=True)

                    # clip to exact study boundary
                    maca_clip_ds = maca_ds.rio.clip(site_gdf.geometry, site_gdf.crs, drop = True)

                    # # ensure NaNs are read as NaNs
                    # if variable in maca_ds.data_vars:
                    #     maca_ds[variable].rio.write_nodata(np.nan, inplace=True)

                    # Save MACA data to raw data dir
                    maca_clip_ds.to_netcdf(maca_path)

                    # Progress notification
                    tqdm.write(f"{variable} | {model} | {start_date} - {end_date} | {rcp_value} | has been downloaded!.")
                else:
                    # Notification
                    tqdm.write(f"{variable} | {model} | {start_date} - {end_date} | {rcp_value} | already exists.")

                # append MACA path to results so the datasets can be opened easily
                result_paths.append(maca_path)

                # update pbar
                pbar.update(1)

    return result_paths