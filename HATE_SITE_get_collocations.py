#get significant collocations with a set of hate speech terms
from pandas.core.indexing import convert_to_index_sliceable
import json
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
import pandas as pd
import datetime



#FUNC
def proc_text(text, stopset):

    #turn punctuation to spaces
    for c in [',', '.', '\n', '\r', ':', ';', '"', "'", '*', '(', ')', '/', "\\", '-']:
        text = text.replace(c, ' ')

    #split on spaces and remove things less than three letters
    words = text.split(' ')
    words = [w.lower() for w in words if len(w) > 3 and not w.isdigit()] #make sure not to include numbers 
    words = [w for w in words if not w in stopset]

    return(words)


def get_collocations(kws_list, filename, period_end_date, outfilename):

    #filename = 'UNESCO Hate Speech Keyword Search Data_Haiti_facebook_2021-08-05_.jsons'
    infile = open(filename, 'r', encoding='utf-8')

    #need to expand to a country specific set of stopwords at some point 
    stopset = set(stopwords.words('english'))

    #read in JSONS
    #get a corpus of words
    #find collocations 
    #filter out stop words
    #filter down to top 5 collocations per keyword, or something like this 
    #highlight y on y divergence? which collocations are becoming more likely?

    print("Processing", filename, sep = ' ')
    documents = []

    for line in infile:
        obj = json.loads(line.strip())

        #date filter here 
        if obj['endDate'] != period_end_date:
            continue

       

        for msg in obj['result']['posts']:
            if not 'message' in msg:
                continue

            #process message for stop words, punctuation
            #split into words 
            words = proc_text(msg['message'], stopset)
            documents.append(words) #documents should be a list of lists


    print('Getting bigrams for', len(documents), 'messages')
    bigram_collocation = BigramCollocationFinder.from_documents(documents)


    kw_bigrams = {}
    #https://stackoverflow.com/questions/48715547/how-to-interpret-python-nltk-bigram-likelihood-ratios
    for bigram, score in bigram_collocation.score_ngrams(BigramAssocMeasures.likelihood_ratio):
        for w in bigram:
            if w in kws_list:
                if not w in kw_bigrams:
                    kw_bigrams[w] = []
                kw_bigrams[w].append((score, bigram))

    print('Output')
    outlines = []
    #top five per keyword
    for k in kw_bigrams:
        kw_bigrams[k] = sorted(kw_bigrams[k], key=lambda x: x[0], reverse=True)

        for score, bigram in kw_bigrams[k][:5]:
            #make sure bigram has keyword first
            if bigram[0] != k:
                bigram = (bigram[1], bigram[0])
            
            outline = {
                'keyword' : k, 
                'bigram' : bigram,
                'score' : score
            }
            outlines.append(outline)

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")

    df = pd.DataFrame(outlines)
    writer = pd.ExcelWriter(outfilename, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='bigrams')
    writer.save()

    print('Done')