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



-------------------------------------------------------------
AI Workplan Draft
# Capstone Project Workplan
## GEOG-730/900: Earth Analytics Applications

**Student:** Raini Helmstadter
**Instructor/Advisor:** Lilly Jones  
**Date:** June 5, 2026

---

## Project Title

**Modeling Future Snow Drought Impacts on Peak Snowpack in the Northern Rockies Under Climate Change**

---

## Research Questions

1. How well can a machine learning model trained on historical climate observations predict peak Snow Water Equivalent (SWE) magnitude and timing across the Northern Rockies, using SNOTEL station records, PRISM gridded climate data, and terrain variables as inputs?

2. Under projected mid-century climate scenarios (RCP4.5), how will peak SWE amounts and peak timing shift across the Gallatin and Madison Ranges of southwestern Montana?

3. How will the frequency of warm snow droughts — characterized by precipitation efficiency loss rather than precipitation deficits — change relative to dry snow droughts under future climate conditions?

---

## Background and Motivation

Snowpack in the western United States functions as a critical natural reservoir, with peak Snow Water Equivalent (SWE) directly determining summer water availability for agriculture, municipal supply, and ecosystem function. Recent decades have documented accelerating changes in snowpack dynamics driven by warming temperatures: earlier melt timing, reduced peak SWE, and a growing prevalence of winter precipitation falling as rain rather than snow, even at elevation.

Two distinct snow drought regimes create different hazard profiles. *Dry droughts* result from precipitation deficits and reduce total water input to the snowpack. *Warm droughts* occur when above-normal temperatures cause precipitation to fall as rain, or drive early melt, even under near-normal precipitation totals — effectively reducing the efficiency with which precipitation is converted into stored snow. The ratio of peak SWE to total winter precipitation (the Snow-to-Precipitation ratio, or SWE efficiency) serves as a diagnostic for distinguishing these regimes: a low ratio under normal precipitation indicates a warm drought; a low ratio coincident with low precipitation indicates a dry drought.

Warm droughts are particularly concerning because they produce acute hazards beyond simple water supply reduction. Rain-on-snow events trigger rapid runoff and catastrophic flooding — as seen in the 2022 Yellowstone Basin floods — while simultaneously eliminating the slow, sustained snowmelt release that downstream ecosystems and water managers depend on. Understanding how the frequency and intensity of warm snow droughts will evolve under future climate scenarios is therefore both scientifically urgent and practically important for water resource management throughout the region.

This project is motivated in part by direct observation. As a ski instructor at Big Sky Resort during the 2025–2026 season, I observed a striking and unusual frequency of precipitation events that fell as rain rather than snow at mid-mountain elevations, a phenomenon consistent with warm drought dynamics. This project builds a rigorous quantitative framework around that observation and asks: how much more common will winters like this become, and what will the consequences be for regional snowpack?

---

## Data Sources

| Dataset | Purpose | Access Method |
|---|---|---|
| SNOTEL station records (NRCS) | Historical daily SWE time series (training labels) | NRCS AWDB web API |
| PRISM gridded climate data (~800m) | Historical temperature and precipitation at SNOTEL sites (training features) | PRISM Climate Group API |
| USGS 3DEP Digital Elevation Model | Elevation, slope, aspect at SNOTEL sites and across study grid (spatial features) | USGS 3DEP API / `elevation` Python package |
| MACA v2 downscaled climate data (~4km) | Future temperature and precipitation projections for model application | MACA Thredds server via OPeNDAP/API |

**Note on data compatibility:** MACA v2 is statistically downscaled from CMIP5 general circulation models and uses RCP emissions scenarios rather than the CMIP6/SSP framework. This project will use the RCP4.5 moderate mitigation scenario. All predictive features will be constructed exclusively from variables available in both PRISM (training period) and MACA (projection period) — namely daily maximum temperature, minimum temperature, and precipitation — to ensure full compatibility between training and application pipelines. This constraint will be documented explicitly during the data acquisition phase (Week 2). CMIP6-downscaled products such as LOCA2 represent a natural extension of this work as those datasets mature.

---

## Methods

### Overview

The project follows a three-phase pipeline: (1) data acquisition and feature engineering, (2) machine learning model development and validation, and (3) future climate application and synthesis. The core ML model takes a winter's worth of summarized climate and terrain inputs for a given location and predicts two targets: peak SWE magnitude and peak SWE timing (day of water year). These targets are extracted from SNOTEL daily time series during training (`max()` and `argmax()`) — the model predicts summary statistics rather than daily values, which keeps the problem tractable and the results directly interpretable.

### Phase 1 — Data Acquisition and Feature Engineering (Weeks 1–3)

**Site selection:** Approximately 25–40 SNOTEL stations will be selected across western Montana, spanning a broad range of elevations, aspects, and mountain ranges (including the Bitterroot, Bridger, Tobacco Root, Gallatin, and Madison ranges) to maximize terrain diversity in the training sample. The Gallatin and Madison ranges will serve as the primary analysis and visualization focus area, while the broader western Montana training domain improves model generalization.

**Predictor variables (features):** All features will be computed from the water year (October 1 start) through the date of peak SWE.

- *Accumulation features:* Total precipitation since October 1; cumulative estimated snow precipitation (precipitation × snow fraction, where snow fraction is estimated from daily temperature using a threshold function); number of days below freezing since October 1
- *Temperature history features:* Seasonal mean temperature anomaly relative to 1981–2010 baseline; 30-day rolling mean temperature at peak season; number of days above 0°C in the 60 days preceding peak SWE
- *Terrain features (static):* Elevation, slope, and aspect derived from USGS 3DEP DEM
- *Temporal features:* Approximate day of water year of potential peak (used in iterative approaches if needed)

**Target variables:** Peak SWE magnitude (mm) and peak SWE timing (day of water year), both extracted from SNOTEL daily records.

**Drought classification:** Following Harpold et al. (2017) and Dierauer et al. (2019), each station-year will be classified post hoc as: *normal, dry drought* (below-normal total precipitation), or *warm drought* (near-normal precipitation but anomalously low SWE-to-precipitation ratio). This classification will be used as a diagnostic and interpretive lens on model outputs, not as a model input.

### Phase 2 — Model Development and Validation (Weeks 3–5)

A **Random Forest** regression model will be trained to simultaneously predict peak SWE magnitude and timing. Random Forest is well-suited to this problem: it handles nonlinear interactions between terrain and climate variables, produces feature importances that are physically interpretable, and is robust to the moderate training sample size available from SNOTEL records.

**Cross-validation strategy:** Two complementary validation approaches will be used:
- *Temporal cross-validation:* Leave-one-year-out; tests whether the model generalizes to years not seen during training, including drought years
- *Spatial cross-validation:* Leave-one-site-out; tests whether the model generalizes to locations not seen during training — the more critical test for spatial extrapolation

Both validation dimensions must show acceptable performance (target RMSE and Nash-Sutcliffe Efficiency) before the model is applied to the spatial grid or to future projections.

**Stretch goal:** If time permits after Random Forest validation (Week 5), XGBoost will be explored as an alternative model, using the same feature set and validation framework.

**Known limitation:** SNOTEL sites are preferentially located in snow-accumulating terrain positions (sheltered basins, mid-to-upper elevations). Spatial extrapolation to the full grid therefore extrapolates beyond the training distribution in exposed or low-elevation pixels. This limitation will be explicitly acknowledged as a source of uncertainty.

### Phase 3 — Spatial Application and Future Climate Projection (Weeks 5–6)

The validated model will be applied to generate gridded SWE estimates in two steps:

1. **Historical spatial application:** Apply model to all PRISM grid cells in the Gallatin/Madison focus area using co-registered DEM terrain variables. Validate spatial patterns against known topoclimatic expectations (e.g., higher SWE on north-facing slopes, strong elevational gradients) before proceeding to future projections.

2. **Future climate application:** Apply model to MACA RCP4.5 projections for mid-century (2040–2069) and late-century (2070–2099) periods, relative to a historical baseline (1981–2010). Analyze: (a) changes in peak SWE magnitude, (b) changes in peak SWE timing, and (c) changes in the frequency and spatial distribution of warm vs. dry drought years based on projected SWE efficiency.

**Resolution note:** MACA data (~4km) is coarser than PRISM (~800m). A resampling strategy will be determined and documented during data acquisition (Week 2).

---

## Expected Outputs and Results

- Gridded maps of historical peak SWE across the Gallatin/Madison focus area
- Gridded maps of projected peak SWE change (mid- and late-century vs. historical baseline)
- Projected shifts in peak SWE timing (earlier melt signal)
- Frequency analysis of warm vs. dry drought years under future scenarios
- Feature importance analysis identifying dominant climate and terrain controls on SWE

---

## Deliverables

| Deliverable | Description | Due |
|---|---|---|
| **Workplan** | This document | June 5, 2026 |
| **GitHub Repository** | Fully documented, reproducible Python notebook pipeline with README | July 28, 2026 |
| **Portfolio Blog Post** | Accessible write-up of methods, results, and implications | July 28, 2026 |
| **Final Presentation** | Slide-based presentation of project findings | July 28, 2026 |

---

## Project Timeline

| Week | Dates | Focus | Key Milestone |
|---|---|---|---|
| **1** | June 5–11 | Setup and data strategy | Workplan submitted; GitHub repository live; SNOTEL sites selected; remote compute access configured (VS Code SSH); PRISM/MACA variable compatibility review begun |
| **2** | June 12–18 | Data acquisition | SNOTEL, PRISM, and DEM pipelines functional; MACA access tested; PRISM/MACA resolution and variable compatibility decision documented |
| **3** | June 19–23 | ⚠️ *Pre-departure deadline* | EDA notebook complete; all features engineered; baseline Random Forest model running on training data; remote access confirmed working |
| **4** | June 26–July 2 | Model development | Random Forest fully trained; spatial and temporal cross-validation running; feature importances interpreted |
| **5** | July 3–9 | Spatial application + model lock | Model applied to historical PRISM/DEM grid; spatial SWE maps generated and validated; model frozen for future application |
| **6** | July 10–16 | Future climate application + synthesis begins | MACA RCP4.5 scenarios applied; drought frequency analysis complete; key figures drafted; writing outline started |
| **7** | July 17–23 | Writing and interpretation | Portfolio post complete; results narrative finalized; all figures publication-ready |
| **8** | July 24–28 | Presentation | Final presentation delivered July 28 |

*Note: Student will be working remotely (away from primary workstation) from June 23 onward. Remote compute access will be established and tested in Week 1.*

---

## Anticipated Challenges and Mitigations

| Challenge | Mitigation Strategy |
|---|---|
| PRISM/MACA cross-compatibility | Dedicated review in Weeks 1–2; all features constrained to variables available in both datasets; decision documented with rationale |
| SWE not directly available in GCM output | Core methodological contribution of the project — ML bridge is the explicit solution |
| SNOTEL site selection bias (non-random terrain) | Spatial cross-validation designed to test generalization; limitation explicitly discussed as uncertainty source |
| Spatial resolution mismatch (PRISM ~800m vs. MACA ~4km) | Resampling strategy determined and documented in Week 2 |
| Remote compute access after June 23 | VS Code Remote SSH + TailScale VPN configured and tested by end of Week 1 |
| ML overfitting across heterogeneous terrain | Leave-one-site-out cross-validation as primary generalization test |

---

## Selected Literature

Dierauer, J.R., Allen, D.M., & Whitfield, P.H. (2019). Snow drought risk and susceptibility in the western United States and southwestern Canada. *Water Resources Research*, 55(4), 3076–3091.

Harpold, A.A., Dettinger, M., & Rajagopal, S. (2017). Defining snow drought and why it matters. *Eos*, 98.

Abatzoglou, J.T. & Brown, T.J. (2012). A comparison of statistical downscaling methods suited for wildfire applications. *International Journal of Climatology*, 32(5), 772–780.

*Additional literature on PRISM methodology (Daly et al.), Random Forest applications in snow hydrology, and SNOTEL network representativeness to be incorporated during Weeks 1–2.*

---

*Repository:* [GitHub URL — to be added upon repo creation]
