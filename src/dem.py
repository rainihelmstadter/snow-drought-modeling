"""
This script contains functions that are used to download specific SRTM DEM tiles and calculate topographic information.

It contains the following X functions:
* download_srtm_tiles: Downloads SRTM tiles for a specific area
* merge_srtm_tiles: Merges tiles into one xarrray.DataArray
* calculate_aspect: Calculates aspect for area
* calculate_slope: Calculates slope
* process_srtm_data: Uses all previous functions to process 
and plot SRTM topographic data
"""
#----------------------------------------------------------------

# Library Imports

# file management
from glob import glob

# data access
import earthaccess

# manage data of various types
import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray as rxr
import rioxarray.merge as rxrmerge
from rioxarray.merge import merge_arrays
import xrspatial


#----------------------------------------------------------------

def download_srtm_tiles(site_gdf, site_topo_dir, site_srtm_pattern):
    '''
    Searches for and downloads SRTMGL3 elevation data if not already present.

    Args:
    =====
    site_gdf (geopandas.GeoDataFrame): Study area boundary
    site_topo_dir (str/Path): Directory to save downloaded .hgt files
    site_srtm_pattern (str): Glob pattern (e.g., "data/topo/*.hgt") to check for existing data

    Returns:
    ========
    list: List of file paths for the SRTM data
    '''

    # study area
    site_elevation_bounds = site_gdf.total_bounds

    # add buffer
    buffer = 0.025
    xmin, ymin, xmax, ymax = site_gdf.total_bounds
    site_bounds_buffered = (xmin - buffer, ymin - buffer,
                            xmax + buffer, ymax + buffer)

    # open files if they have already been downloaded
    existing_files = glob(site_srtm_pattern)

    # look at results
    if not glob(site_srtm_pattern):

        # search for elevation data
        site_srtm_search = earthaccess.search_data(
            short_name = 'SRTMGL3',
            bounding_box = site_bounds_buffered
        )

        # download elevation data
        site_srtm_results = earthaccess.download(
            site_srtm_search,
            site_topo_dir
        )

        return site_srtm_results

    else:
        # site_srtm_results = open files
        print("SRTM Files have already been downloaded!")

        return existing_files

#----------------------------------------------------------------

# function to process elevation tiles
def merge_srtm_tiles(site_srtm_pattern, site_gdf):
    '''
    Merge downloaded SRTM tiles into one DA.

    Args:
    =====
    site_srtm_pattern (str):
        Helps define file paths to tiles.
    site_gdf (GeoDataFrame):
        Defines study area boundary for clipping

    Returns:
    ========
    site_srtm_da (DataArray):
        DA of merged srtm tiles
    '''
    
    # initialize list
    site_srtm_da_list = []

    # study area
    site_elevation_bounds = site_gdf.total_bounds

    # add buffer
    buffer = 0.025
    xmin, ymin, xmax, ymax = site_gdf.total_bounds
    site_bounds_buffered = (xmin - buffer, ymin - buffer,
                            xmax + buffer, ymax + buffer)

    # loop through tiles 
    for srtm_path in glob(site_srtm_pattern):
        tile_da = rxr.open_rasterio(srtm_path, mask_and_scale = True).squeeze()
        srtm_cropped_da = tile_da.rio.clip_box(*site_bounds_buffered)
        srtm_clip_da = srtm_cropped_da.rio.clip(site_gdf.geometry)
        site_srtm_da_list.append(srtm_clip_da)

    # merge the tiles
    site_srtm_da = merge_arrays(site_srtm_da_list)
    
    return site_srtm_da

#----------------------------------------------------------------

def calculate_aspect(site_da, site_gdf):
    '''
    Calculates aspect using SRTM elevation data

    Args:
    =====
    site_da (DataArray):
        DA of SRTM elevation data
    site_gdf (GeoDataFrame):
        Defines study area boundary for clipping

    Returns:
    ========
    site_aspect_rpj (DataArray):
        DataArray of aspect data, reprojected to EPSG: 4326
    '''

    # label
    slope_reproject = site_da.rio.reproject("EPSG: 5070")

    # label
    site_aspect = xrspatial.aspect(slope_reproject)
    
    # need to cut values off at zero
    site_aspect = site_aspect.where(site_aspect > 0)

    # reproject slope to match gdf
    site_aspect_rpj = site_aspect.rio.reproject("EPSG: 4326")

    # clip data to ensure no dead space when plotting
    xmin, ymin, xmax, ymax = site_gdf.total_bounds
    site_aspect_rpj = site_aspect_rpj.rio.clip_box(xmin, ymin, xmax, ymax)

    # # plot aspect
    # ax = site_aspect_rpj.plot(cmap = 'twilight')

    # # show site boundary
    # site_gdf.boundary.plot(ax = plt.gca(), edgecolor = 'black')
    # plt.show()

    # return a da
    return site_aspect_rpj

#----------------------------------------------------------------

# slope calculation
def calculate_slope(site_da, site_gdf):
    '''
    Calculates slope using SRTM elevation data

    Args:
    =====
    site_da (DataArray):
        DA of SRTM elevation data
    site_gdf (GeoDataFrame):
        Defines study area boundary for clipping

    Returns:
    ========
    site_slope_rpj (DataArray):
        DataArray of slope data, reprojected to EPSG: 4326
    '''

    # label
    slope_reproject = site_da.rio.reproject("EPSG: 5070")

    # calculate slope
    site_slope = xrspatial.slope(slope_reproject)

    # reproject slope to match gdf
    site_slope_rpj = site_slope.rio.reproject("EPSG: 4326")

    # clip data to ensure no dead space when plotting
    xmin, ymin, xmax, ymax = site_gdf.total_bounds
    site_slope_rpj = site_slope_rpj.rio.clip_box(xmin, ymin, xmax, ymax)

    # # label
    # ax = site_slope_rpj.plot(cmap = 'terrain')
    # site_gdf.boundary.plot(ax = plt.gca(), edgecolor = 'black')
    # plt.show()

    # return a da
    return site_slope_rpj

#----------------------------------------------------------------

# define a wrapper function
def process_srtm_data(site_name, site_gdf, site_srtm_pattern,
                      site_topo_dir, srtm_plots_dir):
    '''
    Function to download SRTM elevation tiles, process them, and calculate
    slope/aspect for study area.

    Args:
    =====
    site_name (str):
        Name of site, used for plotting and saving
    site_gdf (GeoDataFrame):
        Study area boundary, used to identify SRTM tiles and in plotting
    site_srtm_pattern (str):
        glob pattern used to identify files
    site_topo_dir (str):
        Directory to save downloaded tiles.
    srtm_plots_dir (str):
        Directory to save plots
    
    Returns:
    ========
    DataArray and plots of site elevation, slope and aspect
    '''

    # make if not statement to only process once
    
    # 1. Download tiles
    site_paths = download_srtm_tiles(site_gdf, site_topo_dir, site_srtm_pattern)

    # 2. Process tiles
    elevation_da = merge_srtm_tiles(site_srtm_pattern, site_gdf)

    # 3. Calculate aspect and slope
    aspect_da = calculate_aspect(elevation_da, site_gdf)
    slope_da = calculate_slope(elevation_da, site_gdf)

    # 4. Handle plotting
    # Dictionary to manage plotting parameters efficiently
    layers = {
        "elevation": (elevation_da, 'viridis', 'Elevation (meters)'),
        "slope": (slope_da, 'jet', 'Slope Angle (degrees)'),
        "aspect": (aspect_da, 'twilight', 'Aspect (degrees)')
    }

    # Create plots for each item
    for key, (da, cmap, cb_label) in layers.items():
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot the data
        im = da.plot(ax=ax, cmap=cmap, add_colorbar = True)
        
        # Overlay boundary
        site_gdf.boundary.plot(ax=ax, color='white', linewidth=1.5)
        
        # Labels and Titles
        ax.set_title(f"{site_name.title()} National Park {key.capitalize()}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        im.colorbar.set_label(cb_label)
        
        # Save to the specified plots directory
        plot_filename = f"{site_name}_{key}_plot.png"
        plt.savefig(os.path.join(srtm_plots_dir, plot_filename), bbox_inches='tight')

        # Show plot in Notebook
        plt.show()

        # Close figure in memory to aid performance
        plt.close(fig)
    
    return elevation_da, slope_da, aspect_da