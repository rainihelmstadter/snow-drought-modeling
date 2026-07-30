# snow-drought-modeling

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20752419.svg)](https://doi.org/10.5281/zenodo.20752419)

### Overview

Water resources in the Mountain West region of the United States are, at the best of times, a tumultuous topic. In the arid landscape of the mountain west, access to adequate water supplies are crucial to myriad stakeholders. For much of the region, water is stored primarily as snowpack in mountain ranges, where it accumulates over the winter, and then melts slowly, releasing water into surrounding ecosystems and draining into managed watersheds, where it is then used for a variety of applications.

As climate change progresses, this paradigm of water management may undergo significant change. Last winter (2025-2026) presented a perfect example of potential challenges approaching the mountain west. Some parts of the Rocky Mountains received lower than average precipitation, and some received relatively normal precipitation; however, across the regions, temperatures were abnormally high, such that snowpack failed to accumulate in normal patterns. These phenomena are known as 'dry' or 'warm' snow droughts, and both may pose serious future risks to water resources in the mountain west.

This project will use machine learning to model snow-water equivalent (SWE) across the Missouri Headwaters HUC6 watershed region given temperature, precipitation, and topographic constraints. The goal is to develop a model that can predict SWE, and by extension, snowpack, across a region, given temperature and precipitation variables. If the model is successful, the next step will be to apply the model to future climate projections in order to better understand how snowpack will change in the region. Climate models don't natively output snowpack variables, but for stakeholders in the mountain west, understanding future snowpack dynamics is paramount to management decisions. The model developed in the project should help close that gap. In addition, this tool can be applied in the context of monitoring future dry or warm snow drought years, adding important context to help stakeholders understand the full scope of future impacts to snowpack.

### Data Sources

| Dataset | Access | Resolution | Time Period |
| --- | --- | --- | --- |
| SNOTEL historical daily SWE, temp, precip time series | USDA AWDB API | point location | 1991-2020 |
| BCQC SNOTEL Dataset | [PNNL website](https://www.pnnl.gov/projects/distributed-hydrology-soil-vegetation-model/data-products) | point location | 1991-2020 |
| SRTM Digital Elevation Model | EarthAccess API | 30 arc second | stationary data |
| PRISM gridded historical climate data | PRISM Climate Group API | 4km | 1991-2020 |

### Usage

This repository contains a few important files and folders:
- environment.yml: use this to create Python environment suitable for working through the notebooks.
- src folder: stores functions and constants used across the notebooks
- notebooks (in code folder): designed to be worked through in numerical order
- outputs: storage for plots and other important outputs
- data: sorts data into raw and cleaned folders. Data is not uploaded to GitHub.

Notebooks:
- 01: Used to define a geographic study area and download SNOTEL data that accords to the study area. I selected the HUC6 Missouri Headwaters watershed, but a different watershed could be downloaded instead.
- 02: Used to download PRISM daily rasters and extract data that falls into the study area.
- 03: Used to download a Digital Elevation Model.
- 04: Prepares PRISM, SNOTEL, and DEM data for input into machine learning model.
- 05: Uses prepared datasets to train a machine learning model, predict SWE from PRISM data, and analyze predictions.

A few notes on usage: 
- the BCQC SNOTEL dataset cannot be downloaded via API. You must download it manually and place the unzipped files into the raw data folder. The dataset is accessed [on the PNNL website](https://www.pnnl.gov/projects/distributed-hydrology-soil-vegetation-model/data-products).
- the file structure listed for the data directories is applicable to my machines; you may need to update paths to fit yours. 
- all packages should be included in the environment.yml file, but for those using an Earth Analytics kernel, you might need to install a package or two. Code for those packages are below the import block in a notebook; uncomment the code and run it to install the necessary packages.
- Downloading the PRISM dataset used in this notebook takes a long time (~20 hours), and the PRISM server is sensitive to repeated requests; plan accordingly.

### Citations

- Alabi, I. O., Marshall, H.-P., Mead, J., & Trujillo, E. (2026). A Machine Learning Model for Estimating Snow Density and Snow Water Equivalent from Snow Depth and Seasonal Snow Climate Classes. Artificial Intelligence for the Earth Systems, 5(2). [https://doi.org/10.1175/AIES-D-25-0021.1]

- Daly, C., Halbleib, M., Smith, J. I., Gibson, W. P., Doggett, M. K., Taylor, G. H., Curtis, J., & Pasteris, P. P. (2008). Physiographically sensitive mapping of climatological temperature and precipitation across the conterminous United States. International Journal of Climatology, 28(15), 2031–2064. [https://doi.org/10.1002/joc.1688]

- Duan, S., Ullrich, P., Risser, M., & Rhoades, A. (2024). Using Temporal Deep Learning Models to Estimate Daily Snow Water Equivalent Over the Rocky Mountains. Water Resources Research, 60(4), e2023WR035009. [https://doi.org/10.1029/2023WR035009]

- Grohmann, C. H. (2015). Effects of spatial resolution on slope and aspect derivation for regional-scale analysis. Computers & Geosciences, 77, 111–117. [https://doi.org/10.1016/j.cageo.2015.02.003]

- Pomarol Moya, O., Nussbaum, M., Mehrkanoon, S., Kraaijenbrink, P. D. A., Gouttevin, I., Karssenberg, D., & Immerzeel, W. W. (2026). Improving snow water equivalent modelling: A comparative study of hybrid machine learning techniques. The Cryosphere, 20(2), 1427–1444. [https://doi.org/10.5194/tc-20-1427-2026]

- O’Flaherty, M. (2025). ADVANCED MACHINE LEARNING APPLICATIONS FOR SNOWPACK AND SWE PREDICTION IN THE ABSAROKA–BEARTOOTH WILDERNESS, MONTANA [Master of Science, Montana State University]. [https://scholarworks.montana.edu/server/api/core/bitstreams/9947cdce-776a-484e-a108-b5b82093cd04/content]

- Ouyang, Z., Wu, A., Chen, S., & Li, K. (2026). Combining Causal Inference with Machine Learning for Reconstructing Mountain Snow Water Equivalent Data. Water, 18(10), 1243. [https://doi.org/10.3390/w18101243]

- Steele, H., Small, E. E., & Raleigh, M. S. (2024). Demonstrating a Hybrid Machine Learning Approach for Snow Characteristic Estimation Throughout the Western United States. Water Resources Research, 60(6), e2023WR035805. [https://doi.org/10.1029/2023WR035805]

- Sun, N., Yan, H., Wigmosta, M. S., Leung, L. R., Skaggs, R., & Hou, Z. (2019). Regional Snow Parameters Estimation for Large-Domain Hydrological Applications in the Western United States. Journal of Geophysical Research: Atmospheres, 124(10), 5296–5313. [https://doi.org/10.1029/2018JD030140]

- Yan, H., Sun, N., Wigmosta, M., Skaggs, R., Hou, Z., & Leung, R. (2018). Next-Generation Intensity-Duration-Frequency Curves for Hydrologic Design in Snow-Dominated Environments. Water Resources Research, 54(2), 1093–1108. [https://doi.org/10.1002/2017WR021290]

- Yan, H., Sun, N., Wigmosta, M., Skaggs, R., Leung, L. R., Coleman, A., & Hou, Z. (2019). Observed Spatiotemporal Changes in the Mechanisms of Extreme Water Available for Runoff in the Western United States. Geophysical Research Letters, 46(2), 767–775. [https://doi.org/10.1029/2018GL080260]

- Zhang, J., Yang, M., Dong, N., & Wang, Y. (2025). Machine-Learning-Based Ensemble Prediction of the Snow Water Equivalent in the Upper Yalong River Basin. Sustainability, 17(9), 3779. [https://doi.org/10.3390/su17093779]
