"""This file contains the collaborative filtering recommender model for Twitch users.

The model is a Factorization Machine built with the package RankFM.
"""

from rankfm.rankfm import RankFM
from features import user_item_interactions
from interactions import HEAD
import pickle
import requests
from pprint import pprint

URL = 'https://api.twitch.tv/helix'


def item_features_matrix(file):
    """This function opens a pickled item/feature matrix.
    """
    pkl_file = open(file, 'rb')

    try:
        data = pickle.load(pkl_file)
    except EOFError:
        raise

    pkl_file.close()
    return data


def model(interactions, item_features, factors, max_samples, epochs):
    """Builds a Factorization Machine recommendation model.

    Args:
        interactions: A dataframe of user/item interactions.
        item_features: A dataframe of item features matrix.
        factors: The latent factor rank (hyperparameter).
        max_samples: The maximum number of negative samples to draw for WARP loss (hyperparameter).
        epochs: Number of training epochs.

    Returns:
        model: A RankFM model object.
    """

    model = RankFM(factors=factors,
                   loss='warp',
                   max_samples=max_samples,
                   alpha=0.01,
                   sigma=0.1,
                   learning_rate=0.1,
                   learning_schedule='invscaling')

    model.fit(interactions, item_features=item_features, epochs=epochs, verbose=True)
    return model


def get_channel_info(user_id):
    """Retrieves channel information from a specific user ID on Twitch.
    """
    global URL
    url = URL + '/users?id={}'

    try:
        r = requests.get(url=url.format(user_id), headers=HEAD)
        return r.json()

    except Exception:
        print('Unable to get the info for id {}'.format(user_id))
        raise


def give_recommendations(model, user, n_items):
    """Provides the top 10 recommendations based on the model.
    """
    return model.recommend(user, n_items=n_items, filter_previous=True, cold_start='drop')


def main(users):
    """Main function for this file that returns recommendations.
    """
    interactions = user_item_interactions('user_item_interactions.pkl')
    item_features = item_features_matrix('item_features.pkl')
    recommender = model(interactions, item_features, 30, 30, 30)
    recs = give_recommendations(recommender, users, n_items=10)
    for rec in list(recs.values[0]):
        pprint(get_channel_info(rec))


if __name__ == '__main__':
    main()
