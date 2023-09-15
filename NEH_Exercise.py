# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 09:11:57 2023

@author: Ben Simmons
"""

import pandas as pd

#%%

''' Step 1: Import and concatenate grant data since 2000 from NEH repository '''

df_2000s = pd.read_xml(r'C:\Users\simmo\Downloads\NEH Exercise\NEH_Grants2000s_Flat.xml')
df_2010s = pd.read_xml(r'C:\Users\simmo\Downloads\NEH Exercise\NEH_Grants2010s_Flat.xml')
df_2020s = pd.read_xml(r'C:\Users\simmo\Downloads\NEH Exercise\NEH_Grants2020s_Flat.xml')

large_df = pd.concat([df_2000s,df_2010s,df_2020s],axis=0)

''' Step 2: Create column to reflect total amount awarded in each grant (outright + matching) '''

large_df['TotalAwarded'] = large_df['AwardOutright'] + large_df['AwardMatching']

''' Step 3: Subset grants to those given to institutions in USA and reduce zip code to 5-digit format '''

large_df = large_df[large_df['InstCountry'] == 'USA']
large_df['ZipCodeShort'] = large_df['InstPostalCode'].str[:5]

''' Step 4: Import HUD zip code to county crosswalk '''

zip_to_county = pd.read_excel(r'C:\Users\simmo\Downloads\ZIP_COUNTY_032023.xlsx',converters={'ZIP':str,'COUNTY':str})

''' Step 4: Import downloaded poverty data from 2021 from US Census Bureau repository, preserving columns only for FIPS codes, zip codes, and poverty rate
            Combine state and county fips codes to create overall county FIPS codes '''

poverty_rate = pd.read_excel(r'C:\Users\simmo\Downloads\est21all.xlsx',converters={'State FIPS Code':str,'County FIPS Code':str})

poverty_rate_small = poverty_rate[['State FIPS Code','County FIPS Code','Postal Code','Name','Poverty Percent, All Ages']]

poverty_rate_small['FIPS Code'] = poverty_rate_small['State FIPS Code'].astype(str) + poverty_rate_small['County FIPS Code'].astype(str)

''' Step 5: Create lists of FIPS codes at county level and zip codes, join poverty rate and zip code to county crosswalk
            Initialize dictionary to capture poverty data in all zip codes
            Clean and reformat data as needed '''

county_fips_code_list = list(poverty_rate_small['FIPS Code'].unique())

zip_code_list = list(zip_to_county['ZIP'].unique())

zip_code_poverty_dict = {}

poverty_join = poverty_rate_small.merge(zip_to_county, left_on = 'FIPS Code', right_on = 'COUNTY', how = 'left')

poverty_join = poverty_join[poverty_join['Poverty Percent, All Ages'] != '.']
poverty_join['Poverty Percent, All Ages'] = poverty_join['Poverty Percent, All Ages'].astype(float)

''' Step 6: Run for loop to obtain calculated poverty rate for all zip codes
            This step is necessary because many zip codes lie in more than one county
            HUD crosswalk contains proportion of each zip code in each county ('TOT_RATIO)
            Convert dictionary of poverty rates for each zip code to data frame
            Merge this data frame to existing data frame of grant data from NEH 
            Subset to variables of interest, including year, organization type, discpline, etc. '''                                                                              


for zip_code in zip_code_list:
    subset = poverty_join[poverty_join['ZIP'] == zip_code]
    poverty_before = subset['Poverty Percent, All Ages']
    weight = subset['TOT_RATIO']
    poverty_rate = sum(poverty_before*weight)
    zip_code_poverty_dict[zip_code] = poverty_rate

zip_code_poverty = pd.DataFrame(zip_code_poverty_dict.items(), columns=['ZipCode','PovertyRate'])
        
large_df = large_df.merge(zip_code_poverty, left_on = "ZipCodeShort", right_on = "ZipCode", how = 'left')

large_df = large_df[['Institution', 'OrganizationType',
       'InstCity', 'InstState', 'InstPostalCode', 'InstCountry',
       'YearAwarded','PrimaryDiscipline',
       'Disciplines', 'Supplements', 'ZipCodeShort',
       'TotalAwarded', 'ZipCode_x', 'PovertyRate_x', 'ZipCode_y',
       'PovertyRate_y']]
        
large_df.to_excel('test_neh.xlsx')






    















