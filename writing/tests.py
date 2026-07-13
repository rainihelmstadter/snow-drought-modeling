# Examples of tests in my codebase

# Example #1
#--------------------

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

# This code has multiple tests included. 
# 
# - First, there is an if statement that checks for existing files, 
# and if there are, prints a warning and continues to the next iteration of the loop. 
# This usage prevents unnecessary queries to the server, lets the user know that a file already exists, and
# skips to the next iteration of the for loop so that no extraneous time is wasted.

# - Second, the download process is wrapped in a try/except block, which allows the code to 
# query the PRISM server while remaining resilient to potential interruptions or issues. 
# This is because the 'try' code can handle certain exceptions (which have been specified) 
# and proceed with the next file to download. 
# 
# - Further, the except blocks are configured to print the error messages received from the 
# PRISM server, along with the specific date that failed. This feature provides the user 
# with additional context on what query failed, and why.

# Example #2
#--------------------

# get max train and min test year
max_train_year = stations_train_df['water_year'].max()
min_test_year = stations_test_df['water_year'].min()

# check that the split worked
if max_train_year >= min_test_year:
    print(f'Train/Test split unsuccessful. Train and Test datasets share year: {max_train_year}')
else:
    print('Train/Test split successful! Train and Test datasets do not overlap')

# This test is much simpler, but provides important information to the user. It tests if the 
# train/test datasets share a year, or if they've been successfully temporally split. 

# This test is important, because training and testing datasets need to be split apart to ensure 
# that a machine learning algorithm can be applied.
 
# Because the year can be set programmatically, it is resilient to changing train/test splits.

# In addition, it prints some useful information. If the split was successful, there's a 
# message that indicates that. If the split wasn't successful, the overlapping year is indicated 
# to the user.

# Future additions
#--------------------

# Part of my data processing includes calculating some additional features into my timeseries datasets. 
# For example, one of these features is a 'day of water year'; however, I don't actually have full years 
# of data downloaded, so the 'day of water year' only counts through part of the year before resetting. 
# In the future, I'd like to add additional test to make sure features like this have been calculated 
# properly.