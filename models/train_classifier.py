import sys
import os
import nltk
import string
import numpy as np
nltk.download(['punkt', 'wordnet','stopwords'])
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.wordnet import WordNetLemmatizer
import pandas as pd
from sqlalchemy import create_engine
import re
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.multioutput import MultiOutputClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer 
from sklearn.metrics import precision_recall_fscore_support,classification_report, f1_score, make_scorer
from sklearn.tree import DecisionTreeClassifier
from sklearn.base import BaseEstimator, TransformerMixin
import pickle

# Get results and add them to a dataframe.
def get_results(y_test, y_pred):
    results = pd.DataFrame(columns=['Category', 'f_score', 'precision', 'recall','accuracy'])
    num = 0
    for cat in y_test.columns:
        precision, recall, f_score, support = precision_recall_fscore_support(y_test[cat], y_pred[:,num], average='weighted')
        results.set_value(num+1, 'Category', cat)
        results.set_value(num+1, 'f_score', f_score)
        results.set_value(num+1, 'precision', precision)
        results.set_value(num+1, 'recall', recall)
        results.set_value(num+1, 'accuracy', round((y_pred[:,num]==y_test[cat]).sum() / len(y_pred[:,num]), 3))
        num += 1

    return results,results['f_score'].mean(),results['precision'].mean(),results['recall'].mean(),results['accuracy'].mean()

def load_data(database_filepath):
	'''
	Load 'messages' table from a database and extract X and Y values and 
	category names.

	Parameters

	----------

	database_filepath : string

	    location of the database file from NLP pipeline


	Returns

	-------

	X, y: pandas.DataFrame

	    The message and target dataframes

	category_names
			
		Names of 36 categories of a message		    

	'''
	engine_location = 'sqlite:///' + database_filepath
	engine = create_engine(engine_location)
	df = pd.read_sql_table('Disaster_Response', engine)
	X = df['message']
	y = df[df.columns[4:]]
	category_names = y.columns
	return X, y, category_names


def tokenize(text):
    '''
    Tokenizes text after standardizing text, removing punctuation and stop words

    by lemmatizing verbs, and stemming, using nltk's WordNetLemmatizer

    and PorterStemmer.
    '''
    text = "".join([word.lower() for word in text if word not in string.punctuation])
    tokens = re.split('\W+', text)
    text = [nltk.PorterStemmer().stem(word) for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    lemmed = [WordNetLemmatizer().lemmatize(word) for word in text]
    lemmed = [WordNetLemmatizer().lemmatize(word, pos='v') for word in lemmed]
    return lemmed

def build_model():
	'''
	Create a multi-output Random Forest classifier machine learning pipeline 
	 
	with tdidf, word_count, character_count, noun_count, and verb_count features.

	Default paramas are max_df=0.5, max_features=5000, ngram_range=(1, 2), use_idf=False

	for tfidf feature and min_samples_split=25, max_depth=500, n_estimators=300 for the classifier.

	Returns:
	    Fitted Random Forest classifer.
	'''

	moc = MultiOutputClassifier(RandomForestClassifier(n_jobs=-1, verbose=5,random_state=42, min_samples_split=25, n_estimators=300, max_depth=500))
	pipeline = Pipeline([
		('vect', TfidfVectorizer(tokenizer=tokenize,max_features=5000,ngram_range=(1,2),use_idf=False)),
		('clf', moc)
	])

	# hyper-parameter grid
	parameters = {'clf__estimator__max_depth': (300,500)}

	# create model
	model = GridSearchCV(estimator=pipeline,
	        param_grid=parameters,
	        verbose=3,
	        cv=2)

	print('Training model...')
	return model



def evaluate_model(model, X_test, Y_test, category_names):
	y_pred = model.predict(X_test)
	results_rf,f,p,r,a = get_results(Y_test, y_pred)
	print('F-score: {} / Precision: {} / Recall: {} / Accuracy: {}'.format( round(f, 3), round(p, 3),round(r,3),round(a,3)))
	print(results_rf)

def save_model(model, model_filepath):
    '''
    Pickle model in specified location.
    '''
    # Assume maximum depth of one directory for location
    if model_filepath.find('/'):
        folder_name = model_filepath.split('/')[0]
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    
    with open(model_filepath, 'wb') as file:
        pickle.dump(model, file)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()