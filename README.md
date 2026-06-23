# snow-drought-modeling

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20752419.svg)](https://doi.org/10.5281/zenodo.20752419)

### Overview

Water resources in the Mountain West region of the United States are, at the best of times, a tumoltuous topic. In the arid landscape of the mountain west, access to adequate water supplies are crucial to myriad stakeholders. For much of the region, water is stored primarily as snowpack in mountain ranges, where it accumulates over the winter, and then melts slowly, releasing water into surrounding ecosystems and draining into managed watersheds, where it is then used for a variety of applications.

As climate change progresses, this paradigm of water management may undergo significant change. Last winter (2025-2026) presented a perfect example of potential challenges approaching the mountain west. Some parts of the Rocky Mountains received lower than average precipitation, and some received relatively normal precipitation; however, across the regions, temperatures were abnormally high, such that snowpack failed to accumulate in normal patterns. These phenomena are known as 'dry' or 'warm' snow droughts, and both may pose serious future risks to water resources in the mountain west.

This project will use machine learning to model snow-water equivalent (SWE) across the Missouri Headwaters HUC6 watershed region given temperature, precipitation, and topographic constraints. The goal is to develop a model that can predict SWE, and by extension, snowpack, across a region, given temperature and precipitation variables. If the model is successful, it will be applied to future climate projections in order to better understand how snowpack will change in the region. Climate models don't natively output snowpack variables, but for stakeholders in the mountain west, understanding future snowpack dynamics is paramount to management decisions. The model developed in the project should help close that gap. In addition, this tool can be applied in the context of monitoring future dry or warm snow drought years, adding important context to help stakeholders understand the full scope of future impacts to snowpack.

### Data Sources

| Dataset | Access | Resolution | Time Period |
| --- | --- | --- | --- |
| SNOTEL historical daily SWE, temp, precip time series | USDA AWDB API | point location | 1991-2020 |
| USGS Digital Elevation Model | TNM Access API | unknown resolution now | stationary data |
| PRISM gridded historical climate data | PRISM Climate Group API | 4km | 1991-2020 |
| MACAv2 downscaled future climate data | MACA Thredds server | 4km | 2035-2065 |

### Usage

This repository contains a few important features:
- environment.yml: use this to create Python environment suitable for working through the notebooks.
- src folder: stores functions and constants used across the notebooks
- notebooks (in code folder): designed to be worked through in numerical order

Notebooks:
- 01: Used to define a geographic study area and download SNOTEL data that accords to the study area. I selected the HUC6 Missouri Headwaters watershed, but a different watershed could be downloaded instead.
- 02: Used to download PRISM daily rasters and extract data that falls into the study area.
- 03: Used to download a Digital Elevation Model
- further notebooks are in development 

A few notes on usage: 
- the file structure listed for the data directories is applicable to my machines; you may want to update to fit yours. 
- all packages should be included in the environment.yml file, but for those using an Earth Analytics kernel, you might need to install a package or two. Code for those packages are below the import block in a notebook; uncomment the code and run it to install the necessary packages.
- The repository is currently in a transition to using a src architecture; Notebook 1 does not use it yet, but later notebooks do.
- Downloading the PRISM dataset used in this notebook takes a long time (~20 hours), and the PRISM server is sensitive to repeated requests; plan accordingly.

### Citations

- Alabi, I. O., Marshall, H.-P., Mead, J., & Trujillo, E. (2026). A Machine Learning Model for Estimating Snow Density and Snow Water Equivalent from Snow Depth and Seasonal Snow Climate Classes. Artificial Intelligence for the Earth Systems, 5(2). [https://doi.org/10.1175/AIES-D-25-0021.1]

- Burns, M. C., & Maxwell, R. M. (2026). Comparing Snow Water Equivalent Estimations From Long Short-Term Memory Networks and Physics-Based Models in the Western United States. Water Resources Research, 62(2), e2025WR041178. [https://doi.org/10.1029/2025WR041178]

- Cowherd, M., Mital, U., Rahimi, S., Girotto, M., Schwartz, A., & Feldman, D. (2024). Climate change-resilient snowpack estimation in the Western United States. Communications Earth & Environment, 5(1), 337. [https://doi.org/10.1038/s43247-024-01496-3]

- Crumley, R. L., Bachand, C. L., & Bennett, K. E. (2024). Snow Distribution Patterns Revisited: A Physics-Based and Machine Learning Hybrid Approach to Snow Distribution Mapping in the Sub-Arctic. Water Resources Research, 60(9), e2023WR036180. [https://doi.org/10.1029/2023WR036180]

- Daly, C., Halbleib, M., Smith, J. I., Gibson, W. P., Doggett, M. K., Taylor, G. H., Curtis, J., & Pasteris, P. P. (2008). Physiographically sensitive mapping of climatological temperature and precipitation across the conterminous United States. International Journal of Climatology, 28(15), 2031–2064. [https://doi.org/10.1002/joc.1688]

- Duan, S., Ullrich, P., Risser, M., & Rhoades, A. (2024). Using Temporal Deep Learning Models to Estimate Daily Snow Water Equivalent Over the Rocky Mountains. Water Resources Research, 60(4), e2023WR035009. [https://doi.org/10.1029/2023WR035009]
Harpold, A. A., & Brooks, P. D. (2018). Humidity determines snowpack ablation under a warming climate. Proceedings of the National Academy of Sciences, 115(6), 1215–1220. [https://doi.org/10.1073/pnas.1716789115]

- Jennings, K. S., Winchell, T. S., Livneh, B., & Molotch, N. P. (2018). Spatial variation of the rain-snow temperature threshold across the Northern Hemisphere. Nature Communications, 9(1), 1148. [https://doi.org/10.1038/s41467-018-03629-7]

- Marshall, A. M., Abatzoglou, J. T., Link, T. E., & Tennant, C. J. (2019). Projected Changes in Interannual Variability of Peak Snowpack Amount and Timing in the Western United States. Geophysical Research Letters, 46(15), 8882–8892. [https://doi.org/10.1029/2019GL083770]

- Molotch, N. P., & Bales, R. C. (2005). Scaling snow observations from the point to the grid element: Implications for observation network design. Water Resources Research, 41(11). [https://doi.org/10.1029/2005WR004229]

- O’Flaherty, M. (2025). ADVANCED MACHINE LEARNING APPLICATIONS FOR SNOWPACK AND SWE PREDICTION IN THE ABSAROKA–BEARTOOTH WILDERNESS, MONTANA [Master of Science, Montana State University]. [https://scholarworks.montana.edu/server/api/core/bitstreams/9947cdce-776a-484e-a108-b5b82093cd04/content]

- Ouyang, Z., Wu, A., Chen, S., & Li, K. (2026). Combining Causal Inference with Machine Learning for Reconstructing Mountain Snow Water Equivalent Data. Water, 18(10), 1243. [https://doi.org/10.3390/w18101243]

- Siirila-Woodburn, E. R., Rhoades, A. M., Hatchett, B. J., Huning, L. S., Szinai, J., Tague, C., Nico, P. S., Feldman, D. R., Jones, A. D., Collins, W. D., & Kaatz, L. (2021). A low-to-no snow future and its impacts on water resources in the western United States. Nature Reviews Earth & Environment, 2(11), 800–819. [https://doi.org/10.1038/s43017-021-00219-y]

- Steele, H., Small, E. E., & Raleigh, M. S. (2024). Demonstrating a Hybrid Machine Learning Approach for Snow Characteristic Estimation Throughout the Western United States. Water Resources Research, 60(6), e2023WR035805. [https://doi.org/10.1029/2023WR035805]
