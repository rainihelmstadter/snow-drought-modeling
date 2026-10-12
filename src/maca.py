'''
This script contains functions to download and process MACAv2 climate data. It contains the following functions:
* download_maca_data: Utilizes variables to access specific sections of the MACA dataset, download, preprocess, and save data to file.
'''

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
    NEED TO ENSURE KELVIN CONVERSION HAPPENS HERE TOO
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
    total_steps = len(models)

    # make a bounding box
    xmin, ymin, xmax, ymax = site_gdf.total_bounds

    # convert lon to 0-360 to match MACAv2 data standards
    min_lon_360 = xmin + 360
    max_lon_360 = xmax + 360

    # set fixed catalog years for the MACA url
    catalog_years = "1950_2005" if rcp_value == "historical" else "2006_2099"

    # download and process files
    with tqdm(total=total_steps, desc=f"Processing {site_name}") as pbar:
        # loop through models
        for model in models:
            for variable in variables:
                opendap_url = (f'http://thredds.northwestknowledge.net:8080/thredds/dodsC/'
                            f'agg_macav2metdata_{variable}_{model}_r1i1p1_{rcp_value}'
                            f'_{catalog_years}_CONUS_daily.nc')

                # set filename and path for model results
                file_name = f'maca_{variable}_{model}_{site_name}_{rcp_value}_{start_date}_{end_date}_CONUS_daily.nc'
                maca_path = os.path.join(maca_dir, file_name)   

                # Download or open file
                if not os.path.exists(maca_path):

                    # Send progress warning
                    print(f"{variable}, {model}, {start_date}_{end_date}, {rcp_value} has not been downloaded.")

                    # Load metadata for dataset
                    lazy_ds = xr.open_dataset(opendap_url, mask_and_scale = True)

                    # subset dataset on the server before downloading
                    subset_ds = lazy_ds.sel(
                        time = slice(start_date, end_date),
                        lon = slice(min_lon_360, max_lon_360),
                        # select lat regardless of direction it's counted
                        lat = slice(ymin, ymax)) if lazy_ds.lat[0] < lazy_ds.lat[-1] else slice(ymax, ymin)

                    # compute request and download subset to RAM
                    maca_360_ds = subset_ds.compute()

                    # Standardize MACA ds lon back to -180 to 180
                    maca_ds = maca_360_ds.assign_coords(lon=((maca_360_ds.lon + 180) % 360) - 180).sortby('lon')

                    # Set spatial dims, CRS, and NaNs
                    maca_ds.rio.write_crs('EPSG:4326', inplace=True)
                    maca_ds.rio.set_spatial_dims(x_dim = 'lon', y_dim = 'lat', inplace=True)
                    # ensure NaNs are read as NaNs
                    if var in maca_ds.data_vars:
                        maca_ds[var].rio.write_nodata(np.nan, inplace=True)

                    # Save MACA data to raw data dir
                    maca_ds.to_netcdf(maca_path)

                    # Progress notification
                    print(f"{variable}, {model}, {start_date}_{end_date}, {rcp_value} has been downloaded!.")
                else:
                    # Notification
                    print(f"{variable}, {model}, {start_date}_{end_date}, {rcp_value} already exists.")

                # append MACA path to results so the datasets can be opened easily
                result_paths.append(maca_path)

                # update pbar
                pbar.update(1)

    return result_paths