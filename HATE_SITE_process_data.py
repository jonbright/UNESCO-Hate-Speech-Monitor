#This file should be run once per week, perhaps the day after the data is collected
#It will process all the existing datastores into a formatted dataset
#Which can be used to make the graphics 

import json
import pandas as pd
import HATE_common
import sys

print('Reading in country data')
countries = HATE_common.create_country_lists()

#A list of stats to produce time series for
stats = ['shareCount', 'loveCount', 'careCount', 'wowCount', 'sadCount', 'angryCount', 
    'thankfulCount', 'likeCount', 'hahaCount', 'commentCount']

for country in countries:
    print('Processing', country)
    infile = open(countries[country]['datastore'], 'r', encoding='utf-8')

    outline_keywords = []

    #each line in the infile is a query to crowdtangle for a specific week 
    #for a specific keyword
    #we are just going to parse the nested dictionary into a csv format
    for line in infile:
        obj = json.loads(line.strip())

        #check the result is correctly formatted 
        try:
            if not 'hitCount' in obj['result']:
                obj['result']['hitCount'] = 0
        except:
            print(obj)
            sys.exit()
            
        #create a new blank outline for this keyword
        outline_kw = {
            'searched_keyword' : obj['searched_keyword'],
            'searched_keyword_type' : obj['searched_keyword_type'],
            'startDate' : obj['startDate'],
            'query_date' : obj['query_date'],
            'endDate' : obj['endDate'],
            'hitCount' : obj['result']['hitCount'] 
        }
        
        #now add in the total statistics
        #need to first add 0 values if they aren't there 
        if not 'facebook' in obj['result']['summary']:
            obj['result']['summary']['facebook'] = {}
        for key in stats:
            if not key in obj['result']['summary']['facebook']:
                obj['result']['summary']['facebook'][key] = 0 

        #now add the values in to our output line
        for key in obj['result']['summary']['facebook']:
            outline_kw[key] = obj['result']['summary']['facebook'][key]

        outline_keywords.append(outline_kw)

    #Write out the resulting data
    print('Data for', len(outline_keywords), 'keyword weeks found')

    #This will overwrite last week's dataset
    df = pd.DataFrame(outline_keywords)
    writer = pd.ExcelWriter(countries[country]['processed_data'], engine='xlsxwriter')
    df.to_excel(writer, sheet_name='data')
    writer.save()