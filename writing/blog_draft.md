# Predicting Snow-Water Equivalent at Watershed Scale using Machine Learning on SNOTEL and PRISM datasets

## 1: Introduction

Last winter was one of the strangest I can remember in my career as a ski instructor in Montana. Over the entire Christmas break - typically a cold, snowy period - it rained for almost my entire commute. Instead of the ground disappearing under a blanket of white, as it usually does for months, the grass in my yard was visible almost the entire winter. Among my peers, the conversation invariably included some version of "This is so strange." and "What bad will the summer be?" Indeed, this is a pressing question for people across the Rocky Mountain region of the US. Many places just had one of the warmest winters ever recorded, with extremely low snowpack. Now, as summer hits, water resources are dwindling, and forests across the Rockies are drying out and catching flame.

As climate changes progresses, there are expected changes to snowpack dynamics in the Rockies. The 2025-2026 winter was perhaps a peak into the future; one where precipitation falls more as rain than snow, snow melts earlier, and the water flowing into streams and reservoirs comes at different times or with different amounts. These potential changes are paramount to understand for stakeholders who depend on snow - municipalities whose drinking water comes from snowpack, ski resorts, wildland firefighters, or infrastructure engineers are just a few examples. In reality, almost anyone living in the mountainous Rockies might be impacted by changes to snowpack.

However, data on snowpack dynamics isn't necessarily easy to access, and yet small changes could have major impacts. For instance, climate models are typically run at such low resolution that their findings have diminished relevance in mountainous regions, and they don't include snowpack data as output variables. There is the SNOTEL dataset, which is a historical record of climate and snowpack data. However, the SNOTEL dataset is comprised of a network of stations. While this is certainly helpful data, point records like SNOTEL only record what's happening at that location, not across an entire watershed.

Assuming that water is mainly stored as snowpack, gaining clarity on snowpack dynamics across a region is crucial to understanding the available water resources. Given that snowpack-derived water users likely come from a variety of backgrounds, understanding of snowpack must be fairly accessible and easy to update. Models or forecasts that can be run on a personal computer are advantageous relative to models that require high-performance computing.

This study is informed by the context surrounding snowpack dynamics in the Rockies. In order to bridge the gap between SNOTEL records and regional models, either hind-cast or future-looking, this study proposes the use of machine learning (ML) to predict snowpack data based on easily available temperature and precipitation data. This project will develop such a ML model that can predict snow-water equivalent (SWE) across a spatial area based on precipitation and temperature data. Once trained and validated on historical data, the ML model could be applied to future climate projections.

## 2: Data and Methods

#### 2.1: Machine Learning and Snowpack

This study is hardly the first to utilize machine learning in efforts to model snowpack; many other researchers have tackled this issue. Machine learning has shown promise in capturing snowpack dynamics. Researchers have used a variety of methods. Duan et al. 2024 employed deep learning models, finding sufficient performance to capture snowpack dynamics. Steele et al. 2024 used a hybrid model approach, comparing neural networks, a physical model, and a statistical snow density model. Ouyang et al. 2026 employed eight different models, including XGBoost, CatBoost, and Random Forests, to model SWE, finding that LightGBM had the highest performance. Alabi et al. 2026 used a variety of decision tree-based models, including Random Forests, XGBoost, and CatBoost algorithms. In addition, a Master's Thesis from Montana State University utilized an ensemble of ML algorithms - XGBoost, LightBoost, and CatBoost - to predict SWE (O'Flaherty 2025). 

One challenge of utilizing ML to model SWE is algorithm selection. Hybrid models, such as those presented by Steele et al. 2024 and ____ show promise, as they combine the algorithmic power of ML with physics-bound calculation. Deep learning or neural network algorithms also show strong performance. However, hybrid model and deep learning/neural networks require significant computing power to run, limiting the applicability outside academic or large-scale corporate use. Decision-tree models, on the other hand, are easily deployed on personal computer-scale equipment, increasing their potential use, and show similar or better performance than computationally expensive approaches. In addition, the strength of decision-tree algorithms can be supplemented by using an ensemble approach. Ensemble approaches seem to be particularly robust, as the strengths and weaknesses inherent in each algorithm can be combined to better capture the full dynamics of snowpack (O"Flaherty 2025, Alabi et al. 2026).

#### 2.2: Study Region

The Missouri Headwaters (MHW) HUC6 watershed was chosen as the study region. This watershed captures numerous mountain ranges as well as 28 SNOTEL stations, providing a wealth of data to use for the model.

#### 2.3: Training Datasets
| Dataset | Access |
| --- | --- |
| SNOTEL historical daily SWE, temp, precip time series | USDA AWDB API |
| BCQC SNOTEL daily dataset | [PNNL website](link here) |
| SRTM Digital Elevation Model | TNM Access API |
| PRISM gridded historical climate data | [PRISM Climate Group API](link) |

Data used in the ML model are indicated in the table above. SNOTEL data provided the target variable (SWE). PRISM data provided climate data used as predictor variables. The PRISM dataset is an interpolated dataset that excels at capturing weather patterns in complex mountainous terrain (Daly et al. 2008), and is freely available at 4km resolution; given the aim of this study, PRISM was the ideal option to provide climate data. Climate data included daily minimum temperature, maximum temperature, and precipitation; rolling windows of weather patterns as well as temporal variables were engineered from the PRISM data. A SRTM digital elevation model (DEM) was used to provide topographic data to the model, supplementing the PRISM data. DEM data included elevation, slope, and aspect; the DEM (30 arcsecond resolution) was upscaled to match the PRISM data (4km resolution). Upscaling methodology was guided by Grohmann 2015: aspect and slope were calculated at native resolution, and then upscaled to the 4km grid. Further, given that aspect is a continuous variable that the ML algorithm can't parse, aspect was expanded to aspect northness and eastness.

The SNOTEL dataset offers a few distinct advantages and disadvantages. The dataset is long - records began in the 1970s - which increases the data available for training. Within the MHW study area, there are 26 SNOTEL stations, 25 of which started recording data by 1996. Given that the PRISM dataset is available until 2020, the SNOTEL dataset offered 25 years of daily data, which was split into a 20-year training period and a 5-year testing period for the ML model. However, SNOTEL data has some notorious data error. Examples include incorrect conversion factors when converting sensor voltage to temperature data, and erroneous SWE measurements due to snow bridging and collapse. Snow bridging and collapse is a phenomena where the snow sitting on the sensor pillow melts off, while leaving a bridge of snow suspended above the pillow. This incorrectly sets the SWE measurement to zero until the bridge collapses, at which point the sensor reads a major spike in SWE. To avoid these issues, this study declined to use the raw SNOTEL dataset available from the USDA, and instead used the bias-corrected and quality-controlled dataset (the BCQC SNOTEL dataset) created by Sun et al. 2018 and provided by the Pacific Northwest National Laboratory. This dataset corrected major errors found from known issues, as described above, easing the cleaning process required in this study. No-data values in the BCQC SNOTEL dataset were fixed with linear interpolation where possible, and dropped if no-data gaps were too big to interpolate.

#### 2.4: Feature Engineering

Various studies (Alabi et al. 2026, ...) found that engineering additional features into the climate dataset improved ML algorithm performance. For instance, Alabi et al. 2026 found that day of water year, as well as rolling 7-day windows of mean temperature and total precipitation, helped improve the algorithm accuracy significantly. This is because temporally dependent. A given day's SWE is dictated by everything that's happened in a winter up to that day; just giving a ML model a day's weather data isn't enough for the model to predict with any accuracy. Guided by these findings, this study engineered the following features:
- Day of Water Year: how many days after October 1 a given day is. This offers the model some temporal grounding and is a proxy for different accumulation/melt processes throughout the year.
- Cumulative Positive Degree Days: This adds all of the temperature readings that are above freezing, giving the model some sense of how much heat has been added to the snowpack throughout the year.
- Cumulative Precipitation: This tells the model how much precipitation has already fallen at any given day.
- Rolling 7-day Windows of Mean Minimum/Maximum Temperature: Gives the model some memory of antecedent temperature; this can help the model determine if the snowpack is stable or melting.
- Rolling 7-day Window of Total Precipitation: Gives the model some memory of antecedent precipitation; this helps the model know if the snowpack is growing or stable.

#### 2.5: Machine Learning Approach

Informed by the literature on ML and snowpack, this study uses Random Forests (a decision-tree algorithm) to predict SWE. A decision-tree algorithm was chosen for two main reasons: ease of deployment, and demonstrated skill in predicting SWE based on climatic variables. Decision-tree algorithms seem to have similar levels of skill in predicting SWE as more computationally expensive algorithms, but are deployable on a variety of computing equipment. Given the focus on developing a model that could be used by a variety of stakeholders, decision-tree algorithms are the obvious choice. Random Forests was chosen as a simple starting point. There are more advanced decision-tree algorithms (such as gradient boosting algorithms like XGBoost or CatBoost), but Random Forests has been shown to be a dependable algorithms (Alabi et al. 2026), while remaining easy to use. When used in Python, Random Forests accepts common data formats like Pandas DataFrames, and requires just a few lines of code from the scikit-learn package to set up and fit the model. Further, validation functions often built in and user-friendly.

The ML algorithm used climate data derived from PRISM data as the predictor variables, and SWE data from the SNOTEL dataset as the target variable. To train the model, timeseries data from PRISM was selected at each grid cell that contained a SNOTEL site. Thus, each row of the training dataset had a SWE measurement (from the SNOTEL station) and climate data for the grid cell. Actual SWE across the grid cell would obviously be much more heterogeneous than this representation, but this approach is the best possible with the data that's available.

A train/test split was completed temporally, in order to preserve the cohesion of data for SWE prediction. Water years 1995-2015 were used for training, and water years 2016-2020 were used for testing. Three rounds of hyperparameter tuning were performed to find the ideal parameters for the Random Forests model. Hyperparameter tuning was completed using Randomized and Grid Search functions from scikit-learn.

## 3:Results

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/winter_1997_swe_animation_embed.html" height="600" width="800">

Results from model training are promising! The Random Forests algorithm was successfully used to train a machine learning model to predict SWE at the SNOTEL stations, and then across the study area. The animation above shows predicted SWE across the study area throughout Winter 1997 (the biggest snow year on record in the dataset). Employing the ML model to predict SWE across the Missouri Headwaters watershed reveals interesting patterns. First, the model is able to capture topographic effects - SWE is lower in the valleys and low elevation regions of the area, and much higher in mountainous, high elevation areas. This implies that there is enough range in the SNOTEL dataset to adequately train the model. Second, the model shows an interesting divergence in how SWE accumulates and melts. At lower elevations, SWE begins to decrease in April and May, while SWE continues to increase in mountainous regions until late May. This result is interesting in the context of the typical April 1 assumption for max SWE; perhaps the standard day for measuring max SWE could vary by elevation.

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/max_vol_plot.html" height="600" width="800">

An annual view of maximum SWE in the entire watershed reveals further findings. First, there is a slight positive trend in accumulation across the entire study period, and a fairly wide range in maximum SWE: 6-9 $km^3$. However, examining the day of year when the maximum SWE in the entire watershed is reached is revelatory. As indicated by the color of each point in the plot above, there is a trend in maximum SWE being reached earlier in the year (0.655 days/year). Put together, these findings suggest that more precipitation is falling in the watershed each winter, but melting is beginning earlier. Further, if we assume that the increased precipitation trend is steady across the whole winter, and maximum SWE is reached earlier, a major threshold is implied: it is likely that more precipitation in early spring is falling as rain rather than snow. This finding is exactly why this study was conducted. The pattern change indicated here will require shifts in management procedures and implies potential issues later in the summer.

## 4:Discussion

#### 4a: Model Validation

| Statistic | Value |
| --- | --- |
| Average Bias | 2.072mm |
| RMSE | 116.297mm |
| $R^2$ | 0.735 |

Preliminary statistics on model performance suggest good reliability. Average bias across the entire dataset (comparing observed and predicted SWE at each station and timestep) is quite low, at 2.072 mm. $R^2$ is 0.735, meaning the model explains about three-fourths of the variance. While this statistic could certainly be improved, this is a strong starting point for a Random Forests algorithm.

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/annual_hydrograph_plot.html" height="600" width="800">

Root Mean Squared Error (RMSE) stands out as a concerning value. 116.297mm is a large error value, especially when the peak SWE value across the watershed may only reach 400-500mm in a given water year. However, as shown in the plot above, the model is able to predict SWE accumulation and peak fairly accurately. The greatest errors are at the beginning of each winter season, when observed SWE is sometimes much greater than the predicted SWE. Predicted SWE is able to catch back up fairly quickly once the winter begins. The accuracy gap is likely due to an artificial cutoff in the dataset: I only included data from October 1 - June 1 of each water year. However, snow can easily begin to fall and accumulate before October 1 in Montana; because of this, observed SWE might already be positive on Oct 1 when the model has almost no information to work on, which makes it extremely difficult for the model to predict. This accuracy gap is likely the source of the high RMSE, and means that the model is still fairly accurate. Including additional data would also likely improve model accuracy.

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/spatial_station_error.html" height="600" width="800">

Finally, there are distinct stations that introduce more error to the model than others. For example, as seen in the plot above, station 436 on the far west of the study area has over double the mean bias error as the next worst performing station. This station is located very close to the Continental Divide at high elevation; however, the plot below shows that elevation is not associated with higher error. This station may be affected by some climate pattern that the rest of the dataset is not, or there might be an error in the station record, as another station nearby performs well. Regardless of the reason, dropping the lowest performing station could help improve model performance.

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/station_scatter.html" height="600" width="800">

#### 4b: Feature Engineering

<embed type="text/html" src="./projects/predicting_swe_with_machine_learning/feature_importance_plot.html" height="600" width="800">

As shown in the plot above, there are four features that are distinctly more important in the model than others. Interestingly, none are the raw PRISM data. Cumulative precipitation is by far the most important, followed by cumulative degrees above freezing (labeled cumulative melt days in the graph). These features accord with common understanding of snowpack; the cumulative precipitation and heat have a major impact on a snowpack throughout a winter. Interestingly, the rolling 7-day windows highlighted by Alabi et. al 2026 were not particularly important to the model.

#### 4c: Limitations

There are important limitations to recognize in this study. First, the use of SNOTEL sites introduces a number of points of bias. SNOTEL stations are located in specific areas - typically flat subalpine meadows or clearings. These sites are subject to very different weather patterns than other parts of the study area (alpine zones, ridgelines, cirques, etc.). Thus, the underlying relationship between SWE and the climatic and temporal drivers that the ML model identifies might not translate to other areas within the study area. The application of the ML model to the entire study area is highly dependent on the assumption that the aforementioned relationship is static; obviously, this is a major assumption. However, gathering suitable data to drive the model from more heterogeneous areas remains a significant challenge to snow science, and the SNOTEL dataset doesn't currently have a suitable competitor.

In addition, the use of SNOTEL data in the ML model assumes that the SNOTEL dataset contains adequate range to model SWE across the study area. That is, I assume that the SNOTEL dataset captures adequate magnitude (e.g. snow or heat events, total snowfall, etc) to teach the ML model a range of possible outcomes such that it can adequately model SWE across the whole range. Of course, due to the aforementioned station bias inherent to the SNOTEL dataset, this may not necessarily be the case. Regions in the study area that are not represented in the SNOTEL dataset could, theoretically, have different properties that the model might not capture.

The complex mountainous terrain present in the study area is another important factor to consider. This factor primarily arises through the resolution of the PRISM dataset and the use of ML versus a physical model. I chose to use the freely available 4km dataset, which, in terms of climate modeling, is fairly high resolution, but, in terms of physical geography, still fails to fully capture the complexity of the mountainous terrain in the study area. There could be small areas of terrain that the model doesn't capture, but have a significant impact on SWE in the region. This is a major challenge of snowpack modeling; micro-terrain features and processes (e.g. wind drifting, wind removal of snow, albedo changes, etc.) aren't captured in the model. However, given the watershed-scale approach, this study assumes that the potential error due to losing these features is likely negligible. In addition, using the ML model is significantly less computationally expensive, which may outweigh the loss of physically-driven variables.

Additional feature engineering could be helpful as well. Rain-on-snow events can be extremely damaging to snowpack, so flagging days with positive maximum temperature and precipitation could indicate that SWE should be decreasing to the model.

## 5: Conclusion

The goal of this project was to develop a machine learning model that was capable of predicting snow-water equivalent. If successful, this model could be used to better understand trends - historic and future - in how water is stored in the Rocky Mountains as snow. As shown, the project was largely successful. A Random Forests algorithm was trained using SNOTEL records and PRISM reanalysis to develop a model that is capable of predicting SWE across the Missouri Headwaters watershed. While some error statistics are not ideal, the model has been shown to be fairly accurate in predicting SWE. Further, it is quite likely that the issues highlighted by the high RMSE value is largely driven by the artificial cutoff in the dataset. Future work should extend the training time period to help mitigate error; a period of September 1-July 1, for example, would give the model more information to train on.

There are two avenues for future work on this project. First, developing an ensemble approach could improve model accuracy and better capture the full range of snowpack dynamics. Studies such as O'Flaherty 2025 strongly suggest that this approach is preferable. Other studies have averaged results of decision tree and gradient boosting algorithms, such as CatBoost, LightBoost, and XGBoost; the differences inherent in the algorithms could help capture more of the variance of the SNOTEL dataset. Once data has been prepared, adding more ML algorithms won't be very time-intensive. 

Second, the ML  model could be applied to future climate model data, such as MACA data. This project was intentionally designed with application to the MACA dataset in mind. MACA downscaled models share the same grid resolution as the PRISM data, which should make for an easy application. Now that the model has been developed, the only barrier to this step is acquiring and preparing the MACA data. However, applying the ML model to MACA data would be reliant on some assumptions, such as assuming that the relationship between climate drivers and SWE in the Missouri Headwaters is stationary. Employing the ML model developed in this project to gain insight on future SWE trends would be hugely valuable, and give insight on how snowpack will continue to evolve in the Missouri Headwaters as climate change progresses.

## 6: References

- Alabi, I. O., Marshall, H.-P., Mead, J., & Trujillo, E. (2026). A Machine Learning Model for Estimating Snow Density and Snow Water Equivalent from Snow Depth and Seasonal Snow Climate Classes. Artificial Intelligence for the Earth Systems, 5(2). https://doi.org/10.1175/AIES-D-25-0021.1

- Daly, C., Halbleib, M., Smith, J. I., Gibson, W. P., Doggett, M. K., Taylor, G. H., Curtis, J., & Pasteris, P. P. (2008). Physiographically sensitive mapping of climatological temperature and precipitation across the conterminous United States. International Journal of Climatology, 28(15), 2031–2064. https://doi.org/10.1002/joc.1688

- Duan, S., Ullrich, P., Risser, M., & Rhoades, A. (2024). Using Temporal Deep Learning Models to Estimate Daily Snow Water Equivalent Over the Rocky Mountains. Water Resources Research, 60(4), e2023WR035009. https://doi.org/10.1029/2023WR035009

- Grohmann, C. H. (2015). Effects of spatial resolution on slope and aspect derivation for regional-scale analysis. Computers & Geosciences, 77, 111–117. https://doi.org/10.1016/j.cageo.2015.02.003

- O’Flaherty, M. (2025). ADVANCED MACHINE LEARNING APPLICATIONS FOR SNOWPACK AND SWE PREDICTION IN THE ABSAROKA–BEARTOOTH WILDERNESS, MONTANA [Master of Science, Montana State University]. https://scholarworks.montana.edu/server/api/core/bitstreams/9947cdce-776a-484e-a108-b5b82093cd04/content

- Ouyang, Z., Wu, A., Chen, S., & Li, K. (2026). Combining Causal Inference with Machine Learning for Reconstructing Mountain Snow Water Equivalent Data. Water, 18(10), 1243. https://doi.org/10.3390/w18101243

- Steele, H., Small, E. E., & Raleigh, M. S. (2024). Demonstrating a Hybrid Machine Learning Approach for Snow Characteristic Estimation Throughout the Western United States. Water Resources Research, 60(6), e2023WR035805. https://doi.org/10.1029/2023WR035805

- Sun, N., Yan, H., Wigmosta, M. S., Leung, L. R., Skaggs, R., & Hou, Z. (2019). Regional Snow Parameters Estimation for Large-Domain Hydrological Applications in the Western United States. Journal of Geophysical Research: Atmospheres, 124(10), 5296–5313. https://doi.org/10.1029/2018JD030140

- Yan, H., Sun, N., Wigmosta, M., Skaggs, R., Hou, Z., & Leung, R. (2018). Next-Generation Intensity-Duration-Frequency Curves for Hydrologic Design in Snow-Dominated Environments. Water Resources Research, 54(2), 1093–1108. https://doi.org/10.1002/2017WR021290

- Yan, H., Sun, N., Wigmosta, M., Skaggs, R., Leung, L. R., Coleman, A., & Hou, Z. (2019). Observed Spatiotemporal Changes in the Mechanisms of Extreme Water Available for Runoff in the Western United States. Geophysical Research Letters, 46(2), 767–775. https://doi.org/10.1029/2018GL080260

- Zhang, J., Yang, M., Dong, N., & Wang, Y. (2025). Machine-Learning-Based Ensemble Prediction of the Snow Water Equivalent in the Upper Yalong River Basin. Sustainability, 17(9), 3779. https://doi.org/10.3390/su17093779