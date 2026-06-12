# Notes from work process

## 6/8/26
Conversation with Claude yielded some interesting finds. Watersheds seem like the best way to delineate the study area (I like it - I'm thinking about snow as a water resource, ultimately.)
  
Interesting python package to check out - pygeohydro. Investigate this further.

#### Preliminary study area: Upper Missouri Headwaters Watersheds

<u> Core ranges (definitely include): </u>

- Pioneer Mountains
- Tobacco Root Mountains
- Gravelly Range
- Madison Range
- Gallatin Range
- Bridger Range
- Absaroka-Beartooth (western portion — Absaroka Range and Beartooth Plateau)

<u>Secondary ranges (include if SNOTEL sites exist):</u>

- Centennial Mountains (MT/ID border — southern edge of domain)

Need to check if HUC8 boundaries that cover Centennials and Abs/Bt drain into Yellowstone or into Wyoming. Maybe clip @ Montana border?

#### SNOTEL Access Notes
https://wcc.sc.egov.usda.gov/awdbRestApi/swagger-ui/index.html#/Reference%20Data/getReferenceData
This API lets you play around with requests and see the output. Really helpful for determining how to shape requests and what variables are available. Use the reference data to explore available parameters. Need to explore which temp var. to use (TOBS, TAVG) Also explore 'SNRR' - Snow-Rain Ratio. Can search via HUCs - need to update metadata search block to reflect

<u> Potential Variables </u>
- WTEQ: Snow Water Equivalent
- WTEQV: Average SWE
- SNRR: Snow Rain Ratio
- PREC: Precipitation Accumulation
- TAVG: avg air temp
- TMIN: min air temp
- TMAX: max air temp

Filter SNOTEL variables via vars available from PRISM/MACA - Claude rec. So, TMAX, TMIN, PREC

## 6/10/26
Found an incredible thesis from an MSU student who used machine learning to predict SWE and Snow Depth in the Beartooths. Need to figure out who her advisor was. She also used an ensemble of models (XGBoost, LightBoost, and CatBoost) to improve error. Might be worth looking into.

Kling-Gupta scores for assessing hydrologic model performance

metloom for SNOTEL access? see Alabi et al.'s GitHub
- snowmodels.utils

Given the time I have, I think leaving hyperparameter tuning, error stats and potentially ML ensembles out will likely be a good idea.

When pulling data using watershed boundaries, make sure to leave a buffer so that pixels/sites on the edge don't get left out


## 6/12

Got the sites filtered with a buffered and clipped boundary!
Snotel Station Triplets: 
916:MT:SNTL ,  318:MT:SNTL ,  328:MT:SNTL ,  347:MT:SNTL ,  355:MT:SNTL ,  365:MT:SNTL ,  381:MT:SNTL ,  385:MT:SNTL ,  403:MT:SNTL ,  436:MT:SNTL ,  448:MT:SNTL ,  487:MT:SNTL ,  1287:MT:SNTL ,  568:MT:SNTL ,  578:MT:SNTL ,  590:MT:SNTL ,  603:MT:SNTL ,  609:MT:SNTL ,  656:MT:SNTL ,  722:MT:SNTL ,  929:MT:SNTL ,  753:MT:SNTL ,  754:MT:SNTL ,  1286:MT:SNTL ,  813:MT:SNTL ,  924:MT:SNTL ,  858:MT:SNTL ,  384:WY:SNTL 

Can query a set beginning date (i.e. 10/01/1990) and the SNOTEL API will return anything past that

Redo notebooks. Make notebook 1 just site selection and SNOTEL download. Notebook 2 DEM, PRISM access (maybe make that two notebooks even?). Start working on using SRC for funcs with climate stuff and DEM.