"""
This script cleans and processes the text data for the Tim Ferriss Show
transcripts and pickles the cleaned DataFrame.
"""

import re
import string
import pandas as pd
from nltk import word_tokenize, pos_tag
import spacy


def clean_text(text):
    """Cleans a document of text with a variety of pre-processing techniques.
    """
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[\n]', ' ', text)
    text = re.sub('[\xa0]', '', text)
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('[-]', '', text)
    return text


def lemmatize(text):
    """Takes in a document of text and lemmatizes each word using the
    SpaCy english lemmatizer.
    """
    nlp = spacy.load('en', disable=['parser', 'ner'])
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc])


def nouns(text):
    """Tokenize a text document and pull out only the nouns.
    """
    is_noun = lambda pos: pos[:2] == 'NN'
    tokenized = word_tokenize(text)
    all_nouns = [word for (word, pos) in pos_tag(tokenized) if is_noun(pos)]
    return ' '.join(all_nouns)


def main():
    """Uses all helper functions to take the DataFrame of episode text from web_scraping.py
    and clean the text before pickling the cleaned DataFrame.
    """
    df = pd.read_pickle('tfs_transcripts.pkl')
    df['transcript'] = df['transcript'].apply(clean_text)
    df['transcript'] = df['transcript'].apply(lemmatize)
    df['transcript_nouns'] = df['transcript'].apply(nouns)
    df.to_pickle('tfs_transcripts_cleaned.pkl')


main()
