import time
import pickle
import json

from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer

#required imports and functions
from sklearn import metrics
from sklearn import utils
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

import pandas as pd
import csv
import sys 



#code spits lots of future warnings - let's ignore these. 
import warnings
warnings.filterwarnings("ignore")


def tfidfise(data):
	german_stop_words = stopwords.words('german')
	german_stop_words.extend(['https', 'www', 'com', 'twitter', 'status', 'youtu', 'youtube'])
	german_stop_words.extend(stopwords.words('english'))
	tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words=german_stop_words)
	tfidf = tfidf_vectorizer.fit_transform(data)
	
	return(tfidf, tfidf_vectorizer)

def create_nmf_full(data, raw_data, topics):
	
	tfidf, tfidf_v = tfidfise(data)
	#random state is set here, so we should be duplicating everything each time it is run
	nmf = NMF(n_components=topics, random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf)

	term_topic_matrix = pd.DataFrame(nmf.components_).transpose()
	term_topic_matrix['terms'] = tfidf_v.get_feature_names()
	
	topic_document_matrix = pd.DataFrame(nmf.transform(tfidf))
	#term_document_matrix = pd.DataFrame(tfidf.toarray(), columns = tfidf_v.get_feature_names())
	
	#uncomment to add terms and tweet text to the output matrices -> good for diagnostics 
	term_topic_matrix['terms'] = tfidf_v.get_feature_names()
	topic_document_matrix['text'] = raw_data 
	#term_document_matrix['text'] = data
	
	return term_topic_matrix, topic_document_matrix, nmf, tfidf_v

#bespoke filtering of tokens
def filter(token):

	for x in ['http', 't.me', 'youtu', 'html']:
		if x in token:
			return False

	if len(token) < 4:
		return False

	if token.isnumeric():
		return False  
	return True


def proc_text(text, stopset):

	#turn punctuation to spaces
	for c in [',', '.', '\n', '\r', ':', ';', '"', "'", '*', '(', ')', '/', "\\", '-']:
		text = text.replace(c, ' ')

	#split on spaces and remove things less than three letters
	words = text.split(' ')
	words = [w.lower() for w in words if len(w) > 3 and not w.isdigit()] #make sure not to include numbers 
	words = [w for w in words if not w in stopset]

	return(words)



#DATA INPUT
def create_topic_model(keyword, infilename, outfilename, country, period_end_date, num_topics):
    #filename = 'UNESCO Hate Speech Keyword Search Data_Haiti_facebook_2021-08-05_.jsons'
    infile = open(infilename, 'r', encoding='utf-8')

    #need to expand to a country specific set of stopwords 
    stopset = set(stopwords.words('english'))

    print("Processing", infilename, sep = ' ')

    #get a list of messages for each keyword 
    keyword_messages = {'messages': [], 'raw_messages' : []}

    for line in infile:
        obj = json.loads(line.strip())

        #date filter here 
        if obj['endDate'] != period_end_date:
            continue

        #bug fix here, caused by some old data with no posts in
        #shouldn't be relevant going forward 
        if not 'posts' in obj['result']:
            continue

        for msg in obj['result']['posts']:
            #one_ct_fb.write(json.dumps(msg))

            if not 'message' in msg:
                continue		

            if keyword in msg['message'].lower():
                #process message for stop words, punctuation
                words = proc_text(msg['message'], stopset)
                msgtxt = ' '.join(words)
                keyword_messages['messages'].append(msgtxt)
                keyword_messages['raw_messages'].append(msg['message'])


    print('Check stopwords in use when finalising script')
    print('Getting topic model for', keyword)

    print('Num documents:', len(keyword_messages['messages']))

    k = num_topics #number of topics 

    #check we have enough for a model
    if len(keyword_messages['messages']) > k:
        

        term_topic_matrix, topic_document_matrix, nmf, tfidf_v = create_nmf_full(keyword_messages['messages'], keyword_messages['raw_messages'], k)

        
        topic_model = {
            'keyword' : keyword,
            'country' : country,
            'date' : period_end_date,
            'enough_documents' : 1,
            'topics' : {}
        }

        for i, topic in enumerate(term_topic_matrix.columns):
            if topic == 'terms':
                continue

            #get the top 10 words per topic 
            top_terms = term_topic_matrix.nlargest(10, columns=topic, keep='first')

            topic_model['topics'][i] = {
                'topic_number' : i, 
                'top_terms' : list(top_terms['terms'])
            }
            

            
        #what about the highest rated documents per topic
        for i, topic in enumerate(topic_document_matrix.columns):
            #this is necessary, check definition of the matrix above
            if topic == 'text':
                continue
            top_docs = topic_document_matrix.nlargest(5, columns=topic, keep='first')
            topic_model['topics'][i]['top_posts'] = list(top_docs['text'])

    else:
        print('Not enough documents')
        topic_model = {
            'keyword' : keyword,
            'country' : country,
            'date' : period_end_date,
            'enough_documents' : 0,
            'topics' : {}
        }

    #topics should be a list in the end
    #no need to conserve the actual key from the dictionary
    topic_model['topics'] = [topic_model['topics'][x] for x in topic_model['topics']]

    output = open(outfilename, 'w', encoding='utf-8')
    output.write(json.dumps(topic_model))
    output.close()



