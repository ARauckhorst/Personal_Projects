"""
This file contains an LDA model for topic modeling episodes of The Tim Ferriss Show.
Topics are then used to build a simple recommender based on collaborative filtering
to find similar episodes.

"""

import pandas as pd
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim import matutils, models, corpora
import scipy.sparse
import random


def stop_words():
    """Adds additional stop words found during modelling to the standard
    nltk english stop word list.
    """
    stop_words = nltk.corpus.stopwords.words('english')
    add_stop_words = ['tim', 'ferriss', 'just', 'really',
                      'think', 'pron', 'thing', 'people',
                      'yeah', 'say', 'go', 'like', 'get',
                      'ryan', 'holiday', 'peter', 'attia',
                      'kevin', 'rose', 'kelly', '-PRON-',
                      'joe', 'paul', 'david', 'john', 'bill'
                      'chip', 'michael', 'chip', 'scott', 'richard'
                      'josh', 'bill', 'mark', 'jim',
                      'oh', 'matt', 'mullenweg', 'mike', 'james',
                      'robin', 'dr', 'dude', 'robbin']

    stop_words.extend(add_stop_words)
    return stop_words


def doc_term_matrix(df, stop_words, min_df, max_df):
    """Creates a term-document matrix using the DataFrame of episode text for
    the Tim Ferriss Show.

    Args:
        df -- (DataFrame) a DataFrame of text for transcripts of the Tim Ferriss Show
        stop_words -- (list) a list of stop words to be removed from the corpus
        min_df -- (float) the minimum document frequency for CountVectorizer
        max_df -- (float) the maximum document frequency for CountVectorizer

    Returns:
        tdm (DataFrame) -- a term-document matrix of episode text
        id2word (dictionary) a dictionary of terms used for LDA modelling
    """

    cv = CountVectorizer(stop_words=stop_words, min_df=min_df, max_df=max_df)

    # Fit to the DataFrame column to create Document-Term Matrix
    data_cv = cv.fit_transform(df['transcript_nouns'])
    dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
    dtm.index = df['episode']

    # Transpose to create Term-Document Matrix
    id2word = dict((v, k) for k, v in cv.vocabulary_.items())
    return dtm, id2word


def create_corpus(dtm):
    """Creates a word corpus from a document term matrix.
    """
    tdm = dtm.transpose()
    sparse_counts = scipy.sparse.csr_matrix(tdm)
    corpus = matutils.Sparse2Corpus(sparse_counts)
    return corpus


def lda_model(df, stop_words, min_df, max_df, num_topics, passes):
    """Takes in a DataFrame of text for transcripts from The Tim Ferriss Show and
    returns an LDA model fit to that text that can be used for Topic modeling.
    """
    dtm, id2word = doc_term_matrix(df, stop_words, min_df, max_df)
    corpus = create_corpus(dtm)

    model = models.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics, passes=passes)
    return model, corpus


def topics_df(model, corpus):
    """Maps topics back to episodes in a DataFrame with their respective weights.
    Adds zero weighting for topics that do not apply to a certain episode in order to
    fill in all rows/columns for the DataFrame.
    """

    corpus_transformed = model[corpus]
    topics_by_ep = dict(zip(df['episode'], list(corpus_transformed)))

    for k, v in topics_by_ep.items():
        if len(v) < 4:
            topics = [item[0] for item in v]
            if 0 not in topics:
                v.append((0, 0.0))
            if 1 not in topics:
                v.append((1, 0.0))
            if 2 not in topics:
                v.append((2, 0.0))
            if 3 not in topics:
                v.append((3, 0.0))
            v.sort(key=lambda x: x[0])

    df = pd.DataFrame(topics_by_ep)
    df = df.transpose()
    return df


def recommend_episode(episode_url):
    """Takes in a data frame and an episode_url and returns a recommended episode
    by taking the five most similar episodes based on cosine similarity
    and choosing a random option.
    """

    episodes = []
    episode_idx = df[df['episode'] == episode_url].index.values.astype(int)[0]
    topics = df.drop(['episode'], axis=1)
    for i in range(df.shape[0]):
        dist = cosine_similarity(topics.iloc[[episode_idx, i]])[0][1]
        episodes.append((i, dist))

    episodes = sorted(episodes, key = lambda x: x[1], reverse=True)
    top_five = episodes[0:5]
    rec_idx = random.choice(top_five)[0]
    rec_url = df.iloc[rec_idx]['episode']
    print("I recommend you listen to the episode here next!: \n {}".format(rec_url))
