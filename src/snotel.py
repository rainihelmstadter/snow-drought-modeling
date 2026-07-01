'''
This script contains functions that are used to download and select SNOTEL station datasets
that fall into or adjacent to a prescribed study area.

It contains the following X functions:
* get_snotel_metadata: 
* get_snotel_data:
* parse_snotel_to_xarray:
* build_snotel_dataset:
'''

#----------------------------------------------------------------

# Library imports

# File management
import glob
from pathlib import Path

# Downloading
from tqdm.notebook import tqdm # progress bar
import requests # for SNOTEL API access
import time
import zipfile

# Data Management
import pandas as pd
import rioxarray as rxr
import xarray as xr

#----------------------------------------------------------------
#----------------------------------------------------------------

# Functions

def get_snotel_metadata(state, variables):
    '''
    Download SNOTEL station metadata via API
    
    Args:
    -----
    state (str):
        State abbreviation for state of interest (i.e. 'MT')
    variables (str, list):
        Variables required from station

    Returns:
    --------
    stations (list):
        Metadata for all eligible stations in list format
    '''

    ### From Claude:
    # this downloads station metadata for all the stations in MT

    # Get station metadata for Montana
    url = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations"
    params = {
        "stationTriplets": f"*:{state}:SNTL", # all SNOTEL stations in state
        "elements": variables    # filter for stations measuring SWE, precip, tmin, and tmax
    }
    # Query server
    response = requests.get(url, params=params)
    # Get the station list
    stations = response.json()

    return stations

#----------------------------------------------------------------

def get_snotel_data(station_triplet, variables, duration, begin_date=None, end_date=None):
    '''
    Download SNOTEl time series data.
    
    Args:
    -----
    station_triplet (str):
        Single station triplet for query e.g. 916:MT:SNTL
    variables (list):
        Variable to return (i.e. WTEQ, PREC)
    duration (str):
        Data frequency. Could be DAILY, HOURLY, MONTHLY, SEMIMONTHLY
    begin_date / end_date (str):
        Time period defined by begin and end. Optional 
        Requires YYYY-MM-dd or MM-dd-YYYY.

    Returns:
    --------
    api_response (json):
        Data produced by API query in flat JSON format.
    '''
    # set url
    url = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data"
    
    # set parameters
    params = {
        "stationTriplets": station_triplet,
        "elements": variables,
        "duration": duration,
        "beginDate": begin_date,
        "endDate": end_date,
        "periodRef": "END"   # standard convention per NRCS docs
    }

    # query server
    response = requests.get(url, params=params)
    response.raise_for_status() # flag server error codes
    api_response = response.json()

    return api_response

#----------------------------------------------------------------

# Parse SNOTEL data from JSON/list to xarray DataSet
# I used Gemini to help me structure this function

def parse_snotel_to_xarray(api_response):
    '''
    Parses the raw SNOTEL REST API response into an xarray.Dataset
    for a single station.

    Args:
    -----
    api_response (json):
        Data produced by SNOTEL API query
    
    Returns:
    --------
    site_ds (xarray.Dataset):
        SNOTEL data packaged in structured Dataset
    '''
    # quick check for data; won't break a for loop
    if not api_response or 'data' not in api_response[0]:
        return None
    
    station_data = api_response[0]
    station_triplet = station_data['stationTriplet']
    
    # Dictionary to hold the timeseries for each variable
    variable_dict = {}
    
    # Loop through each weather element (e.g., PREC, WTEQ)
    for element in station_data['data']:
        var_name = element['stationElement']['elementCode']
        values_list = element['values']
        
        # Extract dates and values using list comprehensions
        dates = [item['date'] for item in values_list]
        values = [item['value'] for item in values_list]
        
        # Create a pandas Series with a datetime index
        variable_dict[var_name] = pd.Series(values, index=pd.to_datetime(dates))
        
    # Combine individual variables into a single DataFrame
    df = pd.DataFrame(variable_dict)
    df.index.name = 'time'
    
    # Convert to an xarray Dataset
    site_ds = df.to_xarray()
    
    # Expand dimensions to include the station triplet
    site_ds = site_ds.expand_dims(station=[station_triplet])
    
    return site_ds

#----------------------------------------------------------------

def build_snotel_dataset(station_list, metadata_gdf, variables, duration, begin_date, end_date):
    '''
    Queries SNOTEL REST API for given list of station triplets, downloads data, and parses into an xarray dataset.

    Args:
    -----
    station_list (list):
        List of SNOTEL station triplets (i.e. 916:MT:SNTL)
    metadata_gdf (GeoDataFrame):
        GDF of SNOTEL site metadata, product of get_snotel_metadata()
    variables (list):
        Variable to return (i.e. WTEQ, PREC)
    duration (str):
        Data frequency. Could be DAILY, HOURLY, MONTHLY, SEMIMONTHLY
    begin_date / end_date (str):
        Time period defined by begin and end. Optional 
        Requires YYYY-MM-dd or MM-dd-YYYY. (can use - or / to separate)

    Returns:
    --------
    station_datasets (xarray.Dataset):
        Dataset of all station data and metadata queried from REST API
    '''

    # Create a metadata directly from the GDF
    # This sets the triplet as the index, selects the columns I want, 
    meta_lookup = metadata_gdf.set_index('stationTriplet')[
        ['latitude', 'longitude', 'elevation', 'name']
    ].to_dict('index')

    # Monitor API query size
    print(f"Fetching data for {len(station_list)} stations in one API call...")
    
    # Initialize Dataset
    station_datasets = []
    failed_datasets = []
    
    # Loop through the returned JSON list
    for triplet in tqdm(station_list, desc='Downloading and Parsing SNOTEL Site'):
        try: 
            # Query API, get data for one site
            raw_data = get_snotel_data([triplet], variables, duration,
                                    begin_date, end_date)
            
            # keep track of failed datasets
            if not raw_data:
                failed_datasets.append((triplet, 'Failed to access data'))

            # Parse this specific station into Xarray
            # (Assuming your parser can accept a single station's dictionary wrapped in a list)
            station_ds = parse_snotel_to_xarray(raw_data)

            # tack on station metadata
            if triplet in meta_lookup:
                meta = meta_lookup[triplet]
                station_ds = station_ds.assign_coords(
                    latitude=(["station"], [meta["latitude"]]),
                    longitude=(["station"], [meta["longitude"]]),
                    elevation=(["station"], [meta["elevation"]]),
                    station_name=(["station"], [meta["name"]])
            )
            else:
                print(f" Warning: No metadata found for {triplet}")
            
            # append to dataset list
            station_datasets.append(station_ds)

            # brief pause to not anger REST server
            time.sleep(0.1)
        
        # Add the missing except block to handle any crashes gracefully
        except Exception as e:
            failed_datasets.append((triplet, str(e)))
            continue
            
    # merge the datasets 
    print("Merging datasets...")
    sntl_stations_dataset = xr.concat(station_datasets, dim='station')
    return sntl_stations_dataset

#----------------------------------------------------------------

def import_bcqc_data(bcqc_dir, station_gdf):
    '''
    Load BCQC SNOTEL data into an xarray.DataArray using SNOTEL station coordinates.

    Args:
    -----
    bcqc_dir (str):
        Directory where bcqc files are stored
    station_gdf (geopandas.GeoDataFrame):
        gdf containing SNOTEL station metadata, including lat and lon coordinates

    Returns:
    --------
    bcqc_snotel_ds (xarray.Dataset):
        Dataset containing BCQC SNOTEL data for selected stations
    excluded_stations (list):
        list of SNOTEL stations in study area that were not in BCQC dataset
    '''

    # initialize vars
    bcqc_ds_list = []
    excluded_stations = []

    # loop through SNOTEL stations and determine the closest matching BCQC file
    for index, station in station_gdf.iterrows():
        
        # grab station lat and lon
        lat = station['latitude']
        lon = station['longitude']
        triplet = station['stationTriplet']

        # find the expected BCQC file
        # it looks like BCQC rounds lat and lon to 2 decimal places;
        # round station lat/lon to predict file name
        expected_file = f'bcqc_{lat:.2f}000_{lon:.2f}000.txt'
        # set file path
        exp_file_path = Path(bcqc_dir) / expected_file

        if exp_file_path.exists():
            # open file
            df = pd.read_csv(
                exp_file_path,
                # bcqc files area space delimited
                sep=r'\s+',
                header=None,
                # na values in BCQC are NaN
                na_values=['NaN'],
                names=['year', 'month', 'day', 'daily_precip_in', 'tmax_f', 'tmin_f', 'tavg_f', 'SWE']
            )

            # set df date from ymd, set as index
            df["date"] = pd.to_datetime(df[["year", "month", "day"]])
            df = df.set_index('date')
            # get rid of redundant columns
            df = df.drop(columns=["year", "month", "day"])

            # convert df to ds
            ds = xr.Dataset.from_dataframe(df)

            # set dimension to use later for concatenating
            ds = ds.expand_dims(stationTriplet=[triplet])

            # grab metadata from df
            ds = ds.assign_coords({
                "stationId": ("stationTriplet", [station['stationId']]),
                "name": ("stationTriplet", [station['name']]),
                "latitude": ("stationTriplet", [lat]),
                "longitude": ("stationTriplet", [lon]),
                "beginDate": ("stationTriplet", [station.get('beginDate')]),
                "endDate": ("stationTriplet", [station.get('endDate')])
            })

            # append to list
            bcqc_ds_list.append(ds)
            print(f"{station['name']} found in BCQC dataset")
        # collect station name in list
        else:
            excluded_stations.append(station['stationTriplet'])
            print(f"{station['name']} not found in BCQC dataset")

    # concat into one ds of all the stations
    if bcqc_ds_list:
        bcqc_snotel_ds = xr.concat(bcqc_ds_list, dim = 'stationTriplet')
    else:
        bcqc_snotel_ds = xr.Dataset()
        print("Warning: No matching BCQC files were found. Returning an empty Dataset.")

    return bcqc_snotel_ds, excluded_stations


        
    # # determine lat and lon of each file
    # for file in expected_files:
    #     # split filename apart at underscores
    #     parts = file.stem.split('_')
    #     # grab lat and lon from the two parts
    #     file_lat = float(parts[1])
    #     file_lon = float(parts[2])
    #     # append lat, lon, and file path to list
    #     bcqc_stations.append({'path'}: file, {'lat'}: file_lat, {'lon'}: file_lon)
