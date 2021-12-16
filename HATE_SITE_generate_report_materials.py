#This file runs after the 'process data' script has been run
#It will generate all the graphics and data required for the update of the website
import HATE_common
import HATE_SITE_get_collocations
import HATE_SITE_topic_model
import subprocess
import pandas as pd
import datetime
import json


print('Reading in country data', flush=True)
countries = HATE_common.create_country_lists()

for country in countries:
    print(country)
    out_graphics = HATE_common.country_graphics_folder(country)
    out_models = HATE_common.country_models_folder(country)

    #execute the R code for the Early Warning graphics
    #this code will also save the interpretation for each graphic
    print('Producing Early Warning Graphics', flush=True)
    subprocess.run(['Rscript', 
 				'/dcms-data/unesco_hate/website/HATE_ew_graphics.r',
 				countries[country]['processed_data'],
                country,
                out_graphics, out_models])

    #extract interpretations and meta information
    print('Extracting meta info', flush=True)
    basic_summary = 'Basic_Summary_Statistics ' + country + '.csv'
    df = pd.read_csv(out_models + basic_summary)

    period_end_date = list(df['endDate'])[0]
    period_start_date = datetime.datetime.strptime(period_end_date, "%Y-%m-%d") - datetime.timedelta(days=7)
    period_start_date_formatted = period_start_date.strftime("%Y-%m-%d")

    meta_info = {
        'updated_on' : datetime.datetime.now().strftime("%Y-%m-%d"),
        'period_end_date' : period_end_date,
        'period_start_date' : period_start_date_formatted
    }

    meta_out = open(out_models + 'meta info ' + country + '.json', 'w', encoding='utf-8')
    meta_out.write(json.dumps(meta_info))
    meta_out.close()

    #Execute for R code the keyword analysis graphics
    #We run the script once per keyword
    print('Producing KW specific graphics')
    for kw in countries[country]['keyword_list']:
        print(kw, end=' ', flush=True)
        subprocess.run(['Rscript', 
 				'/dcms-data/unesco_hate/website/HATE_kw_graphics.r',
 				countries[country]['processed_data'],
                country, kw, out_graphics])
    
    #Get the bigram collocations
    #need to filter the datastore to just this week
    #one collocations file per week
    print('\nFinding bigrams', flush=True)
    collocations_outfilename = out_models + 'collocations ' + country + '.xlsx' 
    HATE_SITE_get_collocations.get_collocations(countries[country]['keyword_list'], countries[country]['datastore'], period_end_date, collocations_outfilename)

    #Visualise bigram collocations for each keyword
    print('Visualising bigrams', flush=True)
    for kw in countries[country]['keyword_list']:
        print(kw, end=' ', flush=True)
        subprocess.run(['Rscript', 
 				'/dcms-data/unesco_hate/website/HATE_SITE_bigram_vis.r',
 				collocations_outfilename,
                country, kw, out_graphics])

    #Execute for the keyword topic models 
    print('\nCreating topic models', flush=True)
    for kw in countries[country]['keyword_list']:
        print(kw, end=' ', flush=True)
        num_topics = 3
        topic_outfilename = out_models + 'topic model ' + country + ' ' + kw + '.json' 
        HATE_SITE_topic_model.create_topic_model(kw, countries[country]['datastore'], topic_outfilename, country, period_end_date, num_topics)

    print('\nReport materials complete!', flush=True)