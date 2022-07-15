#collect a week's worth of data for all the countries that are currently being monitored
#add the data to the data store of historical data for that country
#should be set up in cron to run once per week

import datetime
import json
import requests 
import time
import HATE_common
import sys
import HATE_api_token_personal

#FUNC
print('Initialising')

#GLOB
#Set up API
ENDPOINT = 'https://api.crowdtangle.com/posts/search'
API_TOKEN = HATE_api_token_personal.token()

#Timing
period_end_date = datetime.datetime.now()
period_start_date = period_end_date - datetime.timedelta(days=7)
period_start_date_formatted = period_start_date.strftime("%Y-%m-%d")
period_end_date_formatted = period_end_date.strftime("%Y-%m-%d")

print('Reading in country data')
countries = HATE_common.create_country_lists()

print('Collecting data for', len(countries), 'countries')
print('For time period', period_start_date_formatted, 'to', period_end_date_formatted)

for country in countries:

    kws_list = countries[country]['keyword_list']
    cc_twoletter = countries[country]['cc_twoletter']
    outfile = open(countries[country]['datastore'], 'a', encoding='utf-8')#append to the existing country datastore 
    
    #get weekly data for country
    for i, kw in enumerate(kws_list):
        kw_entry = kws_list[kw]
        print(kw_entry['kw'], flush=True, end=' ')
        print(round(i/len(kws_list),2), flush=True, end=' ')

        params = {
                'token' : API_TOKEN, 
                'searchTerm' : '"' + kw_entry['kw'] + '"', #make sure to quote the keyword
                'includeSummary' : 'true',
                'startDate' : period_start_date_formatted,
                'endDate' : period_end_date_formatted,
                'count' : 100, #we actually need posts for the week to do the collocations and topic model
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

        #add in search meta data
        obj['searched_keyword'] = kw_entry['kw']
        obj['searched_keyword_type'] = kw_entry['type']
        obj['startDate'] = period_start_date_formatted
        obj['endDate'] = period_end_date_formatted
        obj['query_date'] = period_end_date_formatted

        outfile.write(json.dumps(obj))
        outfile.write('\n')

        #two calls per minute allowed
        time.sleep(40)

    print('Country complete')
    outfile.close()


