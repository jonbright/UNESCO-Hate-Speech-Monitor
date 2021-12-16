import pandas as pd

#also convert keywords with spaces into a joined up version
def space_repl(kws):
    newkws = []
    for kw in kws:
        if ' ' in kw:
            newkw = kw.replace(' ', '')
            newkws.append(newkw)

    for newkw in newkws:
        kws[newkw] = {
            'kw': newkw,
            'type' : kws[kw]['type']
        }
    return(kws)

def haiti_keywords():
    indf = pd.read_excel(data_store_folder() + 'haiti keywords.xlsx', engine='openpyxl')
    kws = {}

    for _, row in indf.iterrows():
        kw = row['Expression'].lower()
        if not kw in kws:
            kws[kw] = {
                'kw': kw.strip(),
                'type' : row['Type']
            }
    return(space_repl(kws))


def cameroon_keywords():
    inkws = ['terrorist', 'anglo-fou', 'graffi', 'cam no go', 'ambazonia', 'ambazozo', 'amba', 'two cubes of sugar in a basin of water', 
    'bamenda', 'franco-frog', 'rat', 'dog', 'biafra', 'black leg', 'bamileke', 'sardinard', 'tontinard', 'wadjo', 'mouton', 'bayangi', 'nkwa', 'toupouri', 'gadamayou', 'francofou']

    kws = {}
    for kw in inkws:
        kws[kw] = {
            'kw': kw,
            'type' : ''
        }
        
    return(space_repl(kws))

def keywords_readable(kws):
    return [kw for kw in kws]

#function should return a list of all countries being monitored
#as well as a list of all the keywords for that country
#and a list of where the country's data is stored
#could eventually be stored in an input file
def create_country_lists():
    countries = {
        'Haiti' : {
            'keyword_list' : haiti_keywords(),
            'keyword_list_readable' : keywords_readable(haiti_keywords()),
            'keyword_hate_data' : data_store_folder() + 'Haiti - Hate Perc.csv',
            'cc_twoletter' : 'ht',
            'datastore' : data_store_folder() + 'Haiti Data Store.jsons',
            'processed_data' : data_store_folder() + 'Haiti Processed.xlsx'
        },
        'Cameroon' : {
            'keyword_list' : cameroon_keywords(),
            'keyword_list_readable' : keywords_readable(cameroon_keywords()),
            'keyword_hate_data' : data_store_folder() + 'Cameroon - Hate Perc.csv',
            'cc_twoletter' : 'cm',
            'datastore' : data_store_folder() + 'Cameroon Data Store.jsons',
            'processed_data' : data_store_folder() + 'Cameroon Processed.xlsx'
        }
    }

    return(countries)


def data_store_folder():
    return 'basis_data/'

def page_data_folder():
    return 'pages/'

def graphics_folder():
    return page_data_folder() + 'graphics/'

def model_data_folder():
    return 'model_data/'

def country_graphics_folder(country):
    return graphics_folder() + country + '/'

def country_models_folder(country):
    return model_data_folder() + country + '/'

if __name__ == '__main__':
    print(haiti_keywords())