'''
This script houses a variety of functions for performing data analysis on predicted PRISM and MACA SWE values.

It contains:
- 
'''

# Import Libraries
from pathlib import Path
from typing import Dict, Optional, Union
import matplotlib.pyplot as plt
import holoviews as hv
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import xarray as xr

# Functions

def add_water_year_dowy_coords(ds, date_dim):
    '''
    This function adds 'water_year' and 'dowy' (day of water year) coords to a given dataset.

    Args:
    -----
    ds (xarray.DataSet):
        Input dataset to have coords added.
    date_dim (str):
        Dimension or coord holding date values within the ds.
    '''

    # Calculate water year and assign
    wy_vals = ds[date_dim].dt.year + (ds[date_dim].dt.month >= 10).astype(int)
    ds = ds.assign_coords(water_year = wy_vals)

    # Calculate DOWY and assign
    # Calculate elapsed days relative to the minimum date in each water year group
    dowy_vals = (ds[date_dim].groupby('water_year')
            .map(lambda group: (group - group.min()).dt.days + 1))
    ds = ds.assign_coords(dowy=dowy_vals)

    return ds

# --------------------------------------------------------------------------------
# Basin Volume Plot: Helper and wrapper functions

# Helper
def _calculate_daily_basin_volume_df(
        ds, swe_var = 'swe_pred', 
        spatial_dims = ['latitude', 'longitude'], pixel_area_km2 = 16.0):
    '''
    Calculate water volume across the entire watershed for each day. 
    Reports volume in km^3.
    
    Args:
    -----
    ds (xarray.Dataset):
        Input dataset containing swe in mm and time coords
    swe_var (str):
        Name of data var containing swe. Defaults to 'swe_pred'.
    spatial_dims (tuple):
        Names of spatial dimension coords. Defaults to 'latitude', 'longitude'.
    pixel_area_km2 (float):
        Area of grid pixel; defaults to 16 km^2

    Returns:
    --------
    pandas.DataFrame
        DataFrame of daily basin volume.
    '''

    # da of volume
    vol_da = (
        # unit conversion:
        # volume (km^3) = depth (mm) * 1e-6 (mm -> km) * pixel_area (km^2)
        (ds[swe_var] * 1e-6 * pixel_area_km2)
        # add up every pixel
        .sum(dim = list(spatial_dims), skipna = True)
        .compute()
    )

    # make a simple df of volume for later plotting
    df = pd.DataFrame({
      'water_year': vol_da['water_year'].values,
      'dowy': vol_da['dowy'].values,
      'volume_km3': vol_da.values,
    })

    return df

# --------------------------------------------------------------------------------

# helper func for panel
def _plot_single_basin_panel(df, title, mean_color, y_max):

    '''
    Builds a single interactive hydrograph panel with individual lines for 
    each wy and a colored mean line.

    Args:
    -----
    df (pd.DataFrame):
        Dataframe from basin volume function.
    title (str):
        Subplot title.
    color (str):
        Subplot mean line color.
    y_max (float):
        Max y value shared by all subplots.

    Returns:
    --------
    '''

    # individual water year lines
    annual_lines = df.hvplot.line(
        x='dowy',
        y='volume_km3',
        by='water_year',
        color='gray',
        alpha=0.25,
        line_width=1.0,
        hover_cols=['water_year', 'date'],
        legend=False,
    )

    # make mean df
    mean_df = (
        df.groupby('dowy')['volume_km3']
        .mean()
        .reindex(range(1, 246))
        .dropna()
        .reset_index()
    )
    # plot mean line
    mean_line = mean_df.hvplot.line(
        x='dowy',
        y='volume_km3',
        color=mean_color,
        line_width=2.8,
        label='Mean Basin Volume'
    )#.opts(legend_position = 'top_left')

    # April 1 reference line (DOWY 183)
    apr1_line = hv.VLine(183).opts(
        color='black', line_dash='dotted', line_width=1.2
    )

    panel = (annual_lines * mean_line * apr1_line).opts(
        title=title,
        xlabel='Day of Water Year',
        ylabel='SWE Volume (km³)',
        ylim=(0, y_max),
        xlim=(1, 245),
        width=420,
        height=320,
    ).opts(legend_position = 'top_left')
    return panel

# --------------------------------------------------------------------------------

# Wrapper for hvplot function
# this will be saved as a .html
def plot_basin_volume_grid( panel_configs,
                           sup_title, 
                           output_path = None,
                           swe_var = 'swe_pred',
                           pixel_area_km2 = 16.0,
                           ):

    '''
    Plots a 3x2 grid of panel of watershed basin volume comparing 
    daily values across years, and includes an average trend. Optionally
    saves using a path.

    Args:
    -----
    panel_configs (dict):
        dictionary containing titles, datasets, and preferred line colors.
    sup_title (str):
        Title of plot to be used.
    output_path (str):
        Path to use to save resulting plot. Defaults to None so panel can be tested first.
        File must be saved as a .html.
    swe_var (str):
        Name of var containing swe. Must be consistent between prism and maca. 
        Assumed to be 'swe_pred'.
    pixel_area_km2 (float):
        Area of pixel in prism or maca grids. Defaults to 16 km^2

    Returns:
    pn.Column
    '''

    # initialize dataframes and determine shared y-limit
    dfs_and_configs = []
    max_vol = 0.0

    for title, ds, color in panel_configs:
        df = _calculate_daily_basin_volume_df(ds, pixel_area_km2=pixel_area_km2)
        # Ensure dowy and water_year are numeric
        df['dowy'] = pd.to_numeric(df['dowy'], errors='coerce')
        df['water_year'] = pd.to_numeric(df['water_year'], errors='coerce')
        dfs_and_configs.append((title, df, color))
        max_vol = max(max_vol, df['volume_km3'].max())

    # set y limit w/ 5% padding
    y_max = max_vol * 1.05

    # make each panel
    plots = [
        _plot_single_basin_panel(df, title, color, y_max)
        for title, df, color in dfs_and_configs
    ]

    # assemble panels into a 2-column linked layout
    grid = hv.Layout(plots).cols(2)

    # set title
    plot_title = pn.pane.Markdown(f"# {sup_title}", align="center")

    # save plot if output path provided
    if output_path:
        hv.save(grid, output_path)
    
    # return the panel with title and subplots
    return pn.Column(plot_title, grid)

# --------------------------------------------------------------------------------

# Wrapper for matplotlib function
# this is for a written report
def plot_basin_vol_grid_matplotlib(
        panel_configs,
        sup_title,
        output_path = None,
        swe_var = 'swe_pred',
        pixel_area_km2 = 16.0,
        ):

    '''
    Plots a 3x2 grid of panel of watershed basin volume comparing 
    daily values across years, and includes an average trend. Optionally
    saves using a path.

    Args:
    -----
    panel_configs (dict):
        dictionary containing titles, datasets, and preferred line colors.
    sup_title (str):
            Title of plot to be used.
    output_path (str):
        Path to use to save resulting plot. Defaults to None so panel can be tested first.
    swe_var (str):
        Name of var containing swe. Must be consistent between prism and maca. 
        Assumed to be 'swe_pred'.
    pixel_area_km2 (float):
        Area of pixel in prism or maca grids. Defaults to 16 km^2
    '''

    # Calculate vol dfs for each plot
    
    # init dfs and max volume val
    vol_dfs = []
    max_vol_observed = 0.0

    # loop through datasets
    for title, ds, color in panel_configs:
        # use helper func
        df = _calculate_daily_basin_volume_df(ds)
        # append val
        vol_dfs.append((title, df, color))
        # note the max volume observed so far between current and previous dfs
        # this is for the shared y-axis later
        max_vol_observed = max(max_vol_observed, df['volume_km3'].max())

    # set up 3x2 panel
    fig, axes = plt.subplots(
        nrows=3, ncols=2, figsize=(15, 14), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    # Set shared y-axis limit with 5% headroom
    y_max = np.ceil(max_vol_observed * 1.05)

    # Key hydrological calendar reference markers (non-leap year baseline)
    # DOWY 1 = Oct 1, 62 = Dec 1, 124 = Feb 1, 183 = Apr 1, 244 = Jun 1
    dowy_ticks = [1, 62, 124, 183, 244]
    dowy_labels = ['Oct 1', 'Dec 1', 'Feb 1', 'Apr 1', 'Jun 1']

    # Plot each panel
    for idx, (title, df, mean_color) in enumerate(vol_dfs):
        ax = axes_flat[idx]

        # Plot individual water year curves (translucent background lines)
        for _, group in df.groupby('water_year'):
            ax.plot(
                group['dowy'],
                group['volume_km3'],
                color='gray',
                # make the line pale
                alpha=0.25,
                linewidth=1.0,
                zorder=1,
            )

        # Calculate and plot the multi-year mean trend
        mean_curve = (
            df.groupby('dowy')['volume_km3'].mean().reindex(range(1, 246)).dropna()
        )
        ax.plot(
            mean_curve.index,
            mean_curve.values,
            # use the color in panel_configs to show mean
            color=mean_color,
            linewidth=2.8,
            label='Mean Basin Volume',
            zorder=3,
        )

        # Reference indicator for April 1 (DOWY ~183)
        ax.axvline(
            x=183, color='black', linestyle=':', alpha=0.5, linewidth=1.2, zorder=2
        )

        # Formatting
        ax.set_title(title, fontsize=12, fontweight='bold', pad=8)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_ylim(0, y_max)
        ax.set_xlim(1, 245)
        ax.set_xticks(dowy_ticks)
        ax.set_xticklabels(dowy_labels)
        ax.legend(loc='upper left', frameon=True, fontsize=9)

        # Label outer edges only
        if idx % 2 == 0:
            ax.set_ylabel(r'Total SWE Volume ($\mathrm{km}^3$)', fontsize=11)
        if idx >= 4:
            ax.set_xlabel('Date (Day of Water Year)', fontsize=11)

    fig.suptitle(
        f'{sup_title}',
        fontsize=15,
        fontweight='bold',
        y=0.995,
    )
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    return fig

# --------------------------------------------------------------------------------
# April 1 vs true peak SWE

def compute_peak_vs_apr1_df(
    ds: xr.Dataset,
    swe_var: str = "swe_pred",
    date_dim: str = "date",
    pixel_area_km2: float = 16.0,
) -> pd.DataFrame:
  """Calculates annual True Peak SWE volume, True Peak DOWY, April 1st volume,

  and the operational gap for each water year.
  """
  # 1. Calculate daily total basin volume (km³)
  daily_vol = (
      (ds[swe_var] * 1e-6 * pixel_area_km2)
      .sum(dim=["latitude", "longitude"], skipna=True)
      .compute()
  )

  # 2. Build daily lookup DataFrame
  daily_df = pd.DataFrame({
      "date": pd.to_datetime(ds[date_dim].values),
      "water_year": ds["water_year"].values,
      "dowy": ds["dowy"].values,
      "volume_km3": daily_vol.values,
  })

  records = []
  for wy, group in daily_df.groupby("water_year"):
    # True Peak: maximum volume reached anytime during that season
    max_idx = group["volume_km3"].idxmax()
    true_peak_vol = group.loc[max_idx, "volume_km3"]
    true_peak_dowy = group.loc[max_idx, "dowy"]
    true_peak_date = group.loc[max_idx, "date"]

    # April 1st snapshot
    apr1_row = group[
        (group["date"].dt.month == 4) & (group["date"].dt.day == 1)
    ]
    apr1_vol = (
        apr1_row["volume_km3"].values[0] if not apr1_row.empty else np.nan
    )

    # Volume gap: water already lost or not yet melted by April 1st
    gap_km3 = true_peak_vol - apr1_vol
    pct_lost = (
        ((true_peak_vol - apr1_vol) / true_peak_vol) * 100
        if true_peak_vol > 0
        else 0.0
    )

    records.append({
        "water_year": int(wy),
        "true_peak_vol_km3": round(true_peak_vol, 3),
        "true_peak_dowy": int(true_peak_dowy),
        "true_peak_date": true_peak_date.strftime("%Y-%m-%d"),
        "apr1_vol_km3": round(apr1_vol, 3),
        "gap_km3": round(gap_km3, 3),
        "pct_lost_by_apr1": round(pct_lost, 2),
    })

  return pd.DataFrame(records)

# --------------------------------------------------------------------------------

def plot_peak_vs_apr1_comparison(
    prism_df: pd.DataFrame,
    maca_df: pd.DataFrame,
    output_path: Optional[Union[str, Path]] = None,
) -> plt.Figure:
  """Generates a side-by-side dual-axis line plot comparing True Peak SWE volume,

  April 1st SWE volume, the operational gap, and True Peak timing (DOWY)
  between the PRISM baseline and MACA Ensemble Mean.
  """
  fig, (ax_prism, ax_maca) = plt.subplots(
      nrows=1, ncols=2, figsize=(16, 6), sharey=True
  )

  # Determine shared y-limits for volume (left axes)
  max_vol = max(
      prism_df["true_peak_vol_km3"].max(), maca_df["true_peak_vol_km3"].max()
  )
  vol_ylim = (0, np.ceil(max_vol * 1.1))

  # Determine shared y-limits for DOWY (right axes): Dec 1 (~62) to May 1 (~213)
  dowy_ylim = (80, 220)

  panels = [
      (
          ax_prism,
          prism_df,
          "PRISM Baseline (1991–2020)",
          "navy",
          "cornflowerblue",
      ),
      (
          ax_maca,
          maca_df,
          "MACA Ensemble Mean (Mid-Century)",
          "darkred",
          "lightcoral",
      ),
  ]

  for idx, (ax_vol, df, title, peak_col, apr1_col) in enumerate(panels):
    ax_dowy = ax_vol.twinx()

    # 1. Volume Lines: True Peak vs April 1st
    line_peak = ax_vol.plot(
        df["water_year"],
        df["true_peak_vol_km3"],
        color=peak_col,
        linewidth=2.4,
        marker="o",
        markersize=4,
        label="True Peak SWE Volume",
        zorder=3,
    )
    line_apr1 = ax_vol.plot(
        df["water_year"],
        df["apr1_vol_km3"],
        color=apr1_col,
        linewidth=1.8,
        linestyle="--",
        marker="s",
        markersize=4,
        label="April 1st SWE Volume",
        zorder=3,
    )

    # 2. Shaded Operational Gap (volume lost or not yet stored by April 1)
    ax_vol.fill_between(
        df["water_year"],
        df["apr1_vol_km3"],
        df["true_peak_vol_km3"],
        color=peak_col,
        alpha=0.15,
        label="Operational Volume Gap",
        zorder=2,
    )

    # 3. Peak Timing (DOWY) on Secondary Axis
    line_dowy = ax_dowy.plot(
        df["water_year"],
        df["true_peak_dowy"],
        color="darkgoldenrod",
        linewidth=1.5,
        linestyle=":",
        marker="^",
        markersize=5,
        label="True Peak Timing (DOWY)",
        zorder=4,
    )

    # Reference horizontal line for April 1 (DOWY 183)
    ax_dowy.axhline(
        y=183,
        color="gray",
        linestyle="-.",
        linewidth=1.2,
        alpha=0.7,
        label="April 1 Benchmark (DOWY 183)",
    )

    # Axis scales and formatting
    ax_vol.set_ylim(vol_ylim)
    ax_dowy.set_ylim(dowy_ylim)
    ax_vol.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax_vol.set_xlabel("Water Year", fontsize=11)
    ax_vol.grid(True, linestyle="--", alpha=0.3)

    # Left panel specifics
    if idx == 0:
      ax_vol.set_ylabel(
          r"Basin SWE Storage ($\mathrm{km}^3$)", fontsize=11, fontweight="bold"
      )
      ax_dowy.set_yticklabels([])  # Suppress inner tick labels
    else:
      ax_dowy.set_ylabel(
          "Day of Water Year (DOWY)",
          fontsize=11,
          fontweight="bold",
          color="darkgoldenrod",
      )
      ax_dowy.tick_params(axis="y", labelcolor="darkgoldenrod")

      # Unified legend on the right panel
      lines = (
          line_peak
          + line_apr1
          + [plt.Rectangle((0, 0), 1, 1, fc=peak_col, alpha=0.15)]
          + line_dowy
      )
      labels = [
          "True Peak Volume",
          "April 1st Volume",
          "Operational Gap",
          "True Peak DOWY",
      ]
      ax_vol.legend(
          lines, labels, loc="lower left", framealpha=0.9, fontsize=9
      )

  fig.suptitle(
      "Missouri Headwaters: True Peak vs. April 1st SWE Storage and Timing"
      " Decoupling",
      fontsize=14,
      fontweight="bold",
      y=1.02,
  )
  plt.tight_layout()

  if output_path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")

# --------------------------------------------------------------------------------

def print_gap_diagnostics(df: pd.DataFrame, label: str):
    mean_peak = df["true_peak_vol_km3"].mean()
    mean_apr1 = df["apr1_vol_km3"].mean()
    mean_gap = df["gap_km3"].mean()
    mean_pct_lost = df["pct_lost_by_apr1"].mean()
    mean_dowy = df["true_peak_dowy"].mean()

    print(f"=== {label} ===")
    print(f"  Mean True Peak Volume:  {mean_peak:.2f} km³")
    print(f"  Mean April 1st Volume:  {mean_apr1:.2f} km³")
    print(f"  Mean Operational Gap:   {mean_gap:.2f} km³ ({mean_pct_lost:.1f}%)")
    print(
        f"  Mean Peak Timing:       DOWY {mean_dowy:.1f} (~{mean_dowy - 183:+.1f}"
        " days relative to April 1)\n"
    )

# --------------------------------------------------------------------------------
# Spatial Plot helper and wrappers

def _make_single_swe_plot(terrain, reference, name, ds, quant_099_swe):
    '''
    Helper function to make plots.

    Args:
    -----
    terrain (hvplot.element):
        Plot of terrain in study area
    reference (hvplot.element):
        Plot of reference markers in study area
    name (str):
        Dataset name.
    ds (rioxarray.dataset)
        Dataset containing swe data
    quant_099_swe (float):
        Float of 99th percentile swe.

    Retuns:
    -------
    hvplot.image
    '''

    # make swe layer
    swe_layer = ds['swe_pred'].hvplot.image(
        geo = True,
        cmap = 'Sunset_r',
        title = f'{name}',
        xlabel = 'Longitude',
        ylabel = 'Latitude',
        clim = (0, quant_099_swe),
        colorbar = True,
        clabel = 'SWE Depth (mm)',
        alpha = 0.7,
        width = 550,
        height = 500
    )

    # overlay terrain, swe, and reference
    swe_plot = terrain * swe_layer * reference

    return swe_plot
   

def make_spatial_swe_plots(panel_configs, gdf, sup_title, output_path = None):
    '''
    Make a plot of two subplots showing spatial mean SWE on April 1 
    (or different day, depending on data preparation) for PRISM and MACA data.

    Args:
    -----
    panel_configs (dict):
        Dict containing prism and maca rioxarray.Datasets and names to be used in plotting.
    gdf (geopandas.GeoDataFrame):
        gdf of study area boundary.
    sup_title (str):
        Title of plot to be used.
    output_path (str):
        filename and path to be used to save the plot. Optional; defaults to None.

    Returns:
    --------
    pn.Column()
    '''

    # make basemaps
    terrain = hv.element.tiles.EsriTerrain()
    reference = hv.element.tiles.EsriReference()

    # get 99th percentile swe for april 1 in maca and prism
    quant_099_swe = max(float(ds['swe_pred'].quantile(0.99)) for _, ds in panel_configs)

    # make plots
    plots = [_make_single_swe_plot(terrain, reference, title, ds, quant_099_swe)
                for title, ds in panel_configs
            ]
    
    # assemble panels into a 2-column linked layout
    grid = hv.Layout(plots).cols(2)

    # set title
    plot_title = pn.pane.Markdown(f'### {sup_title}', align='center')
    layout = pn.Column(plot_title, grid)

    # save plot if output path provided
    if output_path:
        hv.save(layout, output_path)
    
    # return the panel with title and subplots
    return layout
       
        

