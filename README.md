# Missing-Middle

ADD PROJECT OVERVIEW 

## Required Python Packages (all available with pip)

- `numpy` 
- `pandas` 
- `zipfile`         
- `matplotlib`
- `altair`
- `seaborn`  
- `DateTime`
- `cpi`
- `six`

## File Directory:

**`zillow_data_exploration_v6.ipynb`**: - Main analysis notebook.  

Note: at the moment altair charts are not rendering in github, hopefully this bug will be fixed soon.  

- `aux_data` contains all data and an auxiliary file needed to run the notebook, except four large files noted below (all also noted inline where needed):

  - `cols_to_keep.py` - This a python file imported by the notebook that simply contains a long list of dates we want to keep in our analysis. Only seperated out for readability.  

  - `county_fips_master.csv` - detailed mapping of counties to fips codes https://github.com/kjhealy/fips-codes 

  - `msa_county_map.csv` - mapping of MSAs to counties https://catalog.data.gov/dataset/california-metropolitan-statistical-areas-msa-and-metropolitan-divisions-md-163d2/resource/580630a6-9db5-4aaf-b331-3a4b3d476c09

  - `msa.csv` - list of top MSAs in california  https://docs.fcc.gov/public/attachments/DOC-240702A2.pdf

  - `year_MSA_AMI.csv` - MSA mapping to AMI levels 

  - `year_county_AMI.csv` - Year/County Pairs 2010-2019 for California mapped to AMI levels https://www.huduser.gov/portal/datasets/il.html#2019 

###### Large data (Not hosted on github):
- `County_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_mon.csv`
- `County_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_mon.csv`
Data from here https://www.zillow.com/research/data/, using the Home Values section, select ZHVI all home low tier, and high tier, respectivley, tier time series from the drop down menu. 

HDMA data: 
- `2019 https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/2019` 
- `2010 https://www.consumerfinance.gov/data-research/hmda/historic-data/?geo=ca&records=originated-records&field_descriptions=labels`

 
### Contact info:

Contact Quinn Underriner with any questions:
underriner@berkeley.edu 
