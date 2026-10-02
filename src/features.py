'''
This script contains functions to complete feature engineering for both PRISM and MACA datasets.

It contains the following functions:
* roll_mean_da: Calculates a rolling mean on an xarray.DataArray
* roll_sum_da: Calculates a rolling sum on an xarray.DataArray
* add_water_year: Calculates and assigns a water year coordinate
* add_day_of_water_year: Calculates and assigns a day of water year (DOWY) value
* add_cumulative_precip: Calculates and assigns cumulative precipitation per water year
* add_degree_days: Calculates and assigns cumulative degrees above freezing per water year
* add_rolling_features: Calculates and assigns rolling means and sums
* engineer_all_features: Master function leveraging previous functions
* reorder_df_vars: Ensures dataframe variables are in the appropriate order
'''

import numpy as np
import pandas as pd
import xarray as xr

# Helper functions
#----------------------------------------------------------------

def roll_mean_da(da, num_days):
    '''
    Calculate a rolling mean on an Xarray.DataArray.

    Args:
    -----
    da (xarray.DataArray):
        DataArray of temperature data timeseries
    num_days (int):
        Number of days for rolling window

    Returns:
    --------
    rolling_mean_da (xarray.DataArray):
        DataArray of rolling mean window
    '''

    rolling_mean_da = da.rolling(time=num_days, min_periods=1).mean()

    return rolling_mean_da

def roll_sum_da(da, num_days):
    '''
    Calculate a rolling sum on an Xarray.DataArray.

    Args:
    -----
    da (xarray.DataArray):
        DataArray of precipitation data timeseries
    num_days (int):
        Number of days for rolling window

    Returns:
    --------
    rolling_sum_da (xarray.DataArray):
        DataArray of rolling mean window
    '''

    rolling_sum_da = da.rolling(time=num_days, min_periods=1).sum()

    return rolling_sum_da
#----------------------------------------------------------------

# Feature Engineering Functions

#----------------------------------------------------------------

def add_water_year(ds, time_dim='time'):
    '''
    Calculates and assigns the water year coordinate.
    Water Year = Calendar Year + 1 if month >= October.
    
    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.    
    '''
    water_year_vals = ds[time_dim].dt.year + (ds[time_dim].dt.month >= 10).astype(int)
    return ds.assign_coords(water_year=water_year_vals)

#----------------------------------------------------------------
def add_day_of_water_year(ds):
    '''
    Calculates and assigns the day of water year to ds.

    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.      
    '''
    #time_index = ds.time.to_index()

    wy_start_date = pd.to_datetime(
        # get water year, subtract 1 (since the water year started the previous year)
        (ds['water_year'] - 1)
        # set to a string and add the month and day start
        .astype(str) + '-10-01'
        )
    dowy_values = (ds['time'] - wy_start_date).dt.days + 1

    return ds.assign_coords(dowy = dowy_values)

#----------------------------------------------------------------

def add_cumulative_precip(ds, precip_var='ppt', time_dim='time'):
    '''
    Calculates the cumulative precipitation received in a winter season.

    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.
    precip_var (str):
        Name of precip variable in coordinates.
    time_dim (str):
        Name of time variable in coordinates to sum along.
    '''

    # check to ensure water_year in ds coords
    if 'water_year' not in ds.coords:
        ds = add_water_year(ds, time_dim)
        
    # dim = 'time' sums along time dim
    wy_cumul_precip = ds[precip_var].groupby('water_year').cumsum(dim=time_dim)
    return ds.assign(wy_cumul_ppt_mm=wy_cumul_precip)

#----------------------------------------------------------------

def add_degree_days(ds):
    '''
    Calculates and assigns cumulative degrees above freezing through water year 
    
    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.
    '''

    # cumulative degree > 0 days
    positive_tmean_days = ds['tmean_c'].clip(min=0)
    ds['wy_cumul_pos_degree_days'] = positive_tmean_days.groupby('water_year').cumsum(dim='time')

    return ds

#----------------------------------------------------------------

def add_rolling_features(ds, num_days_list=[3, 7]):
    '''
    Calculates rolling metrics safely across water years to prevent 
    spring data from bleeding into autumn across the summer gap.

    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.
    num_days_list (list):
        Number of days in rolling feature periods. 
        Set to 3 and 7 per Alabi et al. 2026, but could be customized as needed.
    '''

    # check to ensure water_year in ds coords
    if 'water_year' not in ds.coords:
        ds = add_water_year(ds)

    # initialize list of new features
    new_features = {}
    
    for days in num_days_list:
        # Pass the function name to .map() without parentheses to prevent eager execution
        new_features[f'tmin_roll{days}_c'] = ds['tmin'].groupby('water_year').map(roll_mean_safe, num_days=days)
        new_features[f'tmax_roll{days}_c'] = ds['tmax'].groupby('water_year').map(roll_mean_safe, num_days=days)
        new_features[f'ppt_roll{days}_mm'] = ds['ppt'].groupby('water_year').map(roll_sum_safe, num_days=days)
        
    return ds.assign(**new_features)

#----------------------------------------------------------------

def engineer_all_features(ds):
    '''
    Master function to calculate and assign features for the entire dataset.
    
    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.
    '''

    # Calculate simple tmean directly
    ds['tmean_c'] = (ds['tmin'] + ds['tmax']) / 2


    # apply feature engineering functions
    ds = add_water_year(ds)
    ds = add_day_of_water_year(ds)
    ds = add_cumulative_precip(ds)
    ds = add_rolling_features(ds, num_days_list=[3, 7])
    ds = add_degree_days(ds)
    
    return ds

#----------------------------------------------------------------

def convert_ds_to_df(ds, chunk_size, dem_df):
    '''
    Convert PRISM or MACA xarray.DataSet to a pandas.DataFrame using chunking to avoid crashing RAM.

    Args:
    -----
    ds (xarray.Dataset):
        Input dataset to assign water year values to.
    chunk_size (int):
        Number of days to process at one time.
    dem_df (pandas.DataFrame):
        Dataframe containing digital elevation model values.
    '''

    # get length of time steps in ds
    time_steps = ds.time.values

    # initialize list
    climate_dem_chunks = []

    print(f"Starting Dataset to DataFrame conversion across {len(time_steps)} time steps...")

    # loop through chunks and convert to df
    for i in range(0, len(time_steps), chunk_size):
        # Grab the specific block of dates
        time_chunk = time_steps[i : i + chunk_size]
        print(f"Processing chunk {i} to {i + len(time_chunk)}.")

        # Slice the climate dataset for just this time window
        chunk = ds.sel(time=time_chunk)

        # Convert just this small chunk to a dataframe (HDF reader handles this easily)
        climate_chunk_df = chunk.to_dataframe()

        # Join the static terrain features onto this time chunk
        # Pandas automatically matches the 'lat' and 'lon' indices
        climate_dem_chunk = climate_chunk_df.join(dem_df, how="left").dropna()

        # append
        climate_dem_chunks.append(climate_dem_chunk)

    # concatenate the chunks
    return pd.concat(climate_dem_chunks)

#----------------------------------------------------------------

def reorder_df_vars(df):
    '''
    Reorders a DataFrame to match training data order. 

    Args:
    -----
    df (pandas.DataFrame):
        Input dataframe
    '''

    # model features order
    model_features_in_order = [
        # date
        'date',
        # lat and lon
        'latitude', 'longitude', 
        # raw prism data
        'ppt_mm', 'tmin_c', 'tmax_c', 
        # topographic data
        'elevation', 'slope', 'aspect_north', 'aspect_east', 
        # lagged prism variables 7-day
        'tmin_c_roll_7d', 'tmax_c_roll_7d', 'ppt_mm_roll_7d',
        # cumulative precip and positive degree days
        'wy_cumul_precip_mm', 'wy_cumul_melt_days',
        # day of water year
        'dowy']

    # reorder
    return df[model_features_in_order]

#----------------------------------------------------------------