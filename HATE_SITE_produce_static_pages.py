#This script generates one static page for each country of interest

import jinja2
import HATE_common
import json


#GLOB - common settings across all pages
TAB_TITLE = 'UNESCO / OII Hate Speech Monitor'
GRAPHICS_DIR = 'graphics/'
STATIC_PAGE_DIR = 'pages/'


print('Reading in country data')
countries = HATE_common.create_country_lists()

for country in countries:
    print(country)

    #read meta info
    meta_info_filename = 'meta info' + country + '.json'
    meta_info = json.loads(open(GRAPHICS_DIR + meta_info_filename, 'r', encoding='utf-8').read())

    template = jinja2.Environment( 
                loader=jinja2.FileSystemLoader('./')      
                ).get_template('page_templates/HATE_static_page_template_table_tabs.html')
                
    rendered_page = template.render(
        country=country,
        tab_title = TAB_TITLE,
        period = meta_info['period_start_date'] + 'to' + meta_info['period_end_date'],
        last_update = meta_info['updated_on'],
        summary_graphic = GRAPHICS_DIR + 'Basic_Summary_Statistics ' + country + '.png',
        detailed_summary_graphic = GRAPHICS_DIR + 'Detailed_Summary_Statistics ' + country + '.png',
        summary_per_keyword = GRAPHICS_DIR + 'Basic_Summary_Statistics_per_Keyword ' + country + '.png',
        summary_per_keyword_reaction = GRAPHICS_DIR + 'Basic_Reaction_Statistics_per_Keyword ' + country + '.png',
        keyword_usage_over_time = 'Post count time series - gang.png',
        keyword_reaction_over_time = 'Post reac time series - gang.png',
        keyword_copresence = 'Collocations - bamenda.png'
        )
                

    outputfile = country + 'static page.html'
    f = open(STATIC_PAGE_DIR + outputfile,'w') 
    f.write(rendered_page)
    f.close()