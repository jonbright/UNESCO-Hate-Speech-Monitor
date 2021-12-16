#This script generates one static page for each country of interest

import jinja2
import HATE_common
import json
import pandas as pd


#GLOB - common settings across all pages
TAB_TITLE = 'UNESCO / OII Hate Speech Monitor'
STATIC_PAGE_DIR = 'pages/'


print('Reading in country data')
countries = HATE_common.create_country_lists()

for country in countries:
    print(country)
    graphics_dir = HATE_common.country_graphics_folder(country)
    models_dir = HATE_common.country_models_folder(country)

    #make the paths relative to the first level of the static page dir
    graphics_dir = graphics_dir.replace(STATIC_PAGE_DIR, '')

    #read meta info
    meta_info_filename = 'meta info ' + country + '.json'
    meta_info = json.loads(open(models_dir + meta_info_filename, 'r', encoding='utf-8').read())

    #read in hate perc infor
    hate_perc = pd.read_csv(countries[country]['keyword_hate_data'])

    #initialise rendering dictionary with meta info
    #and info for the about section
    render_dict = {
        'country' : country,
        'tab_title' : TAB_TITLE,
        'period' : meta_info['period_start_date'] + ' to ' + meta_info['period_end_date'],
        'last_update' : meta_info['updated_on'],
        'keywords' : countries[country]['keyword_list'],
        'keyword_graphic' : graphics_dir + 'Keyword Perc Hate ' + country + '.png'
    }

    #add early warning graphics
    render_dict['ew_graphics'] = {
        'summary_graphic' : graphics_dir + 'Basic_Summary_Statistics ' + country + '.png',
        'detailed_summary_graphic' : graphics_dir + 'Detailed_Summary_Statistics ' + country + '.png',
        'summary_per_keyword' : graphics_dir + 'Basic_Summary_Statistics_per_Keyword ' + country + '.png',
        'summary_per_keyword_reaction' : graphics_dir + 'Basic_Reaction_Statistics_per_Keyword ' + country + '.png',
    }

    #add keyword specific graphics and topics , one for each keyword
    render_dict['kw_graphics'] = []
    #sort in alphabetical order
    kw_list = sorted(countries[country]['keyword_list'])
    for kw in kw_list:

        #add keyword meta data
        kw_summary = 'Basic_Summary_Statistics_per_Keyword ' + country + '.csv'
        df = pd.read_csv(models_dir + kw_summary)
        #print(df.columns)
        df = df[(df['searched_keyword'] == kw) & (df['measure'] == 'hitCount')]

        if len(df) == 0:
            hitCount = 0
        else:
            hitCount = list(df['value'])[0]
        

        #find also the hate perc
        hate_perc_kw = hate_perc[hate_perc['searched_keyword'] == 'kw']
        hate_perc_kw = list(hate_perc_kw['perc_hate'])

        if len(hate_perc_kw) == 0:
            hate_perc_kw = 'undefined'
        else:
            hate_perc_kw = hate_perc_kw[0]

        #add topic model data
        topic_model = json.loads(open(models_dir + 'topic model ' + country + ' ' + kw + '.json', 'r', encoding='utf-8').read())

        #add graphics summary data
        kw_line = {
            'keyword' : kw, 
            'num_posts' : hitCount,
            'hate_perc_kw' : hate_perc_kw,
            'keyword_usage_over_time' : graphics_dir + 'Post count time series - ' + country + ' ' + kw + '.png',
            'keyword_reaction_over_time' : graphics_dir + 'Post reac time series - ' + country + ' ' + kw + '.png',
            'keyword_copresence' : graphics_dir + 'Collocations -  ' + country + ' ' + kw + '.png',
            'topic_model' : topic_model['topics']
        }

        render_dict['kw_graphics'].append(kw_line)

    #add static about section for this page 


    #Finally load template and render
    template = jinja2.Environment( 
                loader=jinja2.FileSystemLoader('./'),
                undefined=jinja2.StrictUndefined      
                ).get_template('page_templates/HATE_static_final.j2')
    rendered_page = template.render(render_dict)
                

    #output static page
    outputfile = country + ' hate speech summary.html'
    f = open(STATIC_PAGE_DIR + outputfile,'w') 
    f.write(rendered_page)
    f.close()