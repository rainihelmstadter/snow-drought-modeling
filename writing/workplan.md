# Capstone Project Workplan
## GEOG-730/900: Earth Analytics Applications

**Student:** Raini Helmstadter
**Instructor/Advisor:** Lilly Jones  
**Date:** June 5, 2026

### Project Summary

I am investigating how future snowpacks and water storage as snow will change under climate change. Specifically, I'm curious to see if the phenomena of a 'warm snow drought' - conditions where there is relatively normal winter precipitation, but low snowpack due to precipitation falling as rain and warm temperatures driving melt. In addition, I'm also curious to see if I can build a model that can predict peak snow-water equivalent (SWE) amount and timing across an area using machine learning to do this.

Because I'm not currently affiliated with anyone in the snow hydrology/climate science field outside of this class, I don't have a specific partner that I'm answering this question for. However, the question of future snowpack across the western US is deeply important to a myriad of stakeholders, like municipalities, water resource managers, wildland firefighters, ski resorts, etc. I'm hoping that this project could help inform the community if shared. 

Further, this project is motivated in part by direct observation. As a ski instructor in Montana this winter, I observed a striking and unusual frequency of precipitation that fell as rain rather than snow - this was a stark example of a warm drought. My project will build a quantitative respone to that observation and asks: how much more common will winters like this become, and what will the consequences be for regional snowpack?

There are three successful outcomes I envision for this project: a model that can predict SWE across a spatial area based on precipitation and temperature data, an understanding of how peak SWE timing and amount will evolve in my study area, and a prediction of how the frequency and severity of warm/dry snow droughts will change in the future.

### Data Sources

| Dataset | Access | Concerns | Obtainment |
| --- | --- | --- | --- |
| SNOTEL historical daily SWE, temp, precip time series | USDA AWDB API | No major concerns | Not yet obtained |
| USGS Digital Elevation Model | TNM Access API | Spatial Resolution | Used last semester, should be able to find in notes |
| PRISM gridded historical climate data | PRISM Climate Group API | PRISM/MACA compatibility | Unfamiliar with this API |
| MACAv2 downscaled future climate data | MACA Thredds server | Uses CMIP5 models, not CMIP6 | Used last semester, familiar with access |

I plan to train the model on PRISM data, but will use the MACA data for future research. I might run into issues using two different datasets with different grids and potentially different variables, and I'll have to evaluate if this becomes an issue. Further, there are some well-known issues in the SNOTEL dataset. Because SNOTEL sites have some significant requirements - they're sited in flat clearings, typically not at relatively high or low altitudes within the mountain environment - the SNOTEL dataset has some important biases that might mess up my model's ability to predict SWE in locations that are significantly different from where SNOTEL sites are located. I think I should be able to get around that issue by incorporating a digital elevation model, but this could be a significant issue and require some methodological redesign.

### Preliminary Methods

The project will involve three major steps: 1. data acquisition, 2. machine learning model development and validation, and 3. ML model application to future climate models. I have previously worked with some of the data sources (MACAv2 and the Digital Elevation Model), but not the PRISM or SNOTEL data. Once the data have been acquired, I will use the SNOTEL data, topographic data, and the PRISM data to build a model that can predict peak SWE timing and amount for a winter season based on a winter's worth of calculated snow accumulation, based on the temperature, precipitation, and topographic data. Based on conversations with my AI project partner, I plan to first use a Random Forests algorithm, and will try to upgrade that to an XGBoost algorithm if time allows. Based on some literature review, there are other ML methods researchers have used to predict SWE (deep learning, neural networks, etc), but I may be limited by the computational power of my personal computers.

I'm not yet super familiar with ML techniques, though we discussed Random Forests in class last semester. My motivation for using these tools is two-fold. First, climate models don't provide a SWE variable, but it's likely one of the more important variables to consider for stakeholders and managers, as it's an indication of how much water is actually stored in the snowpack. Second, selfishly, I am quite interested in machine learning techniques, both professionally and personally, and this project presents a nice way to pursue that interest. 

Because climate models don't provide SWE, constructing a SWE variable is important, but tricky to manage spatially. The best record of SWE in the US is the SNOTEL dataset, which records weather and snowpack data at stations located throughout the country. However, the SNOTEL network is limited to specific sites, limiting its use. Machine learning presents an excellent way to use the existing dataset to make inferences across a much larger range. My model will compile a temperature and precipitation timeseries for each PRISM grid cell with a SNOTEL site in the study area, and then use the timeseries and SNOTEL data to predict peak SWE statistics, minimizing error while providing important predictions across my study area.

Once the ML model has been validated spatially and temporally, I will apply it to future climate model runs from the MACAv2 dataset, along with tabulating days above freezing and precipitation totals. These three outputs will reveal more information on how future snowpacks and their drivers will evolve.

I could certainly just calculate the statistics on how precipitation and temperature will change in my study area from the MACA datasets. However, I don't think this is the most valuable or useful product I can draw from the models. Making inferences on SWE in the future period can show some of the interplay between temperature and precipitation, and SWE is a more relevant variable to water resource managers or other stakeholders than just temp/precip. In addition, there might be other ways to calculate SWE in the future period besides using a ML model to predict peak SWE amount and timing. I plan to give other methods, like calculating daily or weekly SWE from climate data or a ML model, some consideration, but given the duration of the project, I don't want to tackle too big of a project. Thus, I'm aiming at predicting summary statistics rather than the full spatial and temporal range.

### Week-by-Week Timeline

With my AI assistant, I've created this rough schedule for myself:

| Week | Dates | Focus | Key Milestone |
|---|---|---|---|
| **1** | June 5–11 | Setup and data strategy | Workplan submitted; GitHub repository live; SNOTEL sites selected; remote compute access configured (VS Code SSH); PRISM/MACA variable compatibility review begun |
| **2** | June 12–18 | Data acquisition | SNOTEL, PRISM, and DEM pipelines functional; MACA access tested; PRISM/MACA resolution and variable compatibility decision documented |
| **3** | June 19–23 | ⚠️ *Pre-departure deadline* | EDA notebook complete; all features engineered; baseline Random Forest model running on training data; remote access confirmed working |
| **4** | June 26–July 2 | Model development | Random Forest fully trained; spatial and temporal cross-validation running|
| **5** | July 3–9 | Spatial application + model lock | Model applied to historical PRISM/DEM grid; spatial SWE maps generated and validated; model frozen for future application |
| **6** | July 10–16 | Future climate application + synthesis begins | MACA RCP4.5 scenarios applied; drought frequency analysis complete; key figures drafted; writing outline started |
| **7** | July 17–23 | Writing and interpretation | Portfolio post complete; results narrative finalized; all figures publication-ready |
| **8** | July 24–28 | Presentation | Final presentation delivered July 28 |

There are a few risks I can see in this plan. One major consideration is that I'm leaving the country for my summer job on June 23rd, which means I'll be separated from my more powerful desktop. To mitigate this, I'm planning on figuring out how to set up a remote connection so I can continue to leverage that processing power. However, if that connection doesn't work, I'll have to adapt. Luckily, I think the methods I've outlined should be flexible enough to also run on my laptop if needed; it'll just be slower. I feel confident that I'll have enough time to complete my data processing, though the synthesis might be a bit cramped in July. I've already accessed a couple of the datasets I'll use in previous projects, so it won't be hard to access those. The biggest question for me is the machine learning aspect, as I've only used it in a couple of the projects for this certificate, and there's definitely gaps in my knowledge. However, there's a lot of literature on using ML for SWE prediction, and with the help of this course and AI I think I should be able to manage it. If the ML model truly proves to be too difficult, I think I can also still achieve some interesting results just using the MACAv2 dataset to examine temperature and precipitation trends. Finally, there's a risk that the methods and datasets I've set out here won't actually be compatible, which will require a pivot. Again, because of the rich literature on the topic, I'm confident I'll have the resources to be able to pivot and adapt my methods if necessary.

### Selected Literature

Dierauer, J.R., Allen, D.M., & Whitfield, P.H. (2019). Snow drought risk and susceptibility in the western United States and southwestern Canada. *Water Resources Research*, 55(4), 3076–3091.

Harpold, A.A., Dettinger, M., & Rajagopal, S. (2017). Defining snow drought and why it matters. *Eos*, 98.

Abatzoglou, J.T. & Brown, T.J. (2012). A comparison of statistical downscaling methods suited for wildfire applications. *International Journal of Climatology*, 32(5), 772–780.
