#A script that will generate the 'basis' data for any new monitor micro site
#The basis data is a year long time series of data which is used to compute historical averages. 
#This script only needs to be run once, when setting up a new site 
#The regular script will progressively add data to the basis data store
#NOTE - make sure to exclude countries if you do not want to regenerate all the data stores 
#NOTE - be conscious not to run while main script is also running

import HATE_common
import datetime
import json
import requests
import sys
import time
import HATE_api_token

print('Initialising')

#GLOB
ENDPOINT = 'https://api.crowdtangle.com/posts/search'
API_TOKEN = HATE_api_token.token()
EXCLUDES = ['']

#set up timing data
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")


print('Reading in country data')
countries = HATE_common.create_country_lists()

print('Getting country data')
for country in countries:
    #timing data each time
    final_cutoff = now - datetime.timedelta(days=365)
    current_end = now
    current_start = current_end - datetime.timedelta(days=7)
    
    print(country)
    if country in EXCLUDES:
        print('Skipping')
        continue

    kws_list = countries[country]['keyword_list']
    cc_twoletter = countries[country]['cc_twoletter']
    outfile = open(countries[country]['datastore'], 'w', encoding='utf-8')#create new datastore here 


    while True:
        if current_start < final_cutoff:
            break

        current_start_f = current_start.strftime("%Y-%m-%d")
        current_end_f = current_end.strftime("%Y-%m-%d")

        print('\n\n')
        print('Analysing time period:', current_start_f, current_end_f, 'for', country)

        #collect data - one slice per keyword 
        #check documentation for AND, OR and NOT searching
        #https://github.com/CrowdTangle/API/wiki/Search
        
        for i, kw in enumerate(kws_list):
            kw_entry = kws_list[kw]
            print(kw_entry['kw'], flush=True, end=' ')
            print(round(i/len(kws_list),2), flush=True, end=' ')

            params = {
                    'token' : API_TOKEN, 
                    'searchTerm' : '"' + kw_entry['kw'] + '"', #make sure to quote the keyword
                    'includeSummary' : 'true',
                    'startDate' : current_start_f,
                    'endDate' : current_end_f,
                    'count' : 5,
                    'platforms' : 'facebook',
                    #'language' : kw_entry['language'], do we need lang specification if we also have country?
                    'sortBy' : 'date',
                    'pageAdminTopCountry' : cc_twoletter
                }

            resp = requests.get(ENDPOINT, params=params)
            try:
                obj = json.loads(resp.content)
            except:
                print('Malformatted JSON')
                print(resp.content)
                sys.exit()

            #delete posts - we don't actually need them, just the metadata
            del(obj['result']['posts'])

            #add in search meta data
            obj['searched_keyword'] = kw_entry['kw']
            obj['searched_keyword_type'] = kw_entry['type']
            obj['startDate'] = current_start_f
            obj['endDate'] = current_end_f
            obj['query_date'] = date

            outfile.write(json.dumps(obj))
            outfile.write('\n')

            #two calls per minute allowed
            time.sleep(40)

        #update timing to step back 7 days
        current_end = current_start
        current_start = current_end - datetime.timedelta(days=7)

    outfile.close() #end of loop for individual country