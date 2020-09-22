"""Collects additional features on Twitch channels based on the output of data.py.

This file is meant to supplement the data.py output to collect features on all of the
followed channels which will be used as an input for the final model.
"""

import requests
import time
import pandas as pd
import pickle
from interactions import HEAD

URL = 'https://api.twitch.tv/helix'


def user_item_interactions(file):
    """Creates a dataframe of user/item interactions.

    Args:
        file: A pickled list of tuples representing user relationships.

    Returns:
        df: A dataframe with two columns. The first column is users and the second
            column represents a channel that is followed.
    """
    pkl_file = open(file, 'rb')

    try:
        data = pickle.load(pkl_file)
    except EOFError:
        raise

    pkl_file.close()
    df = pd.DataFrame(data, columns=['user', 'channel'])
    return df


def get_user_info(user_id):
    """Returns a page of information for a specific user from the Twitch API.

    Args:
        user_id: The ID of a specific Twitch user.

    Returns:
        r.json(): The API call in JSON format.

    Raises:
        'Unable to get info on this user'
    """
    global URL
    url = URL + '/users?id={}'

    try:
        r = requests.get(url=url.format(user_id), headers=HEAD)
        return r.json()

    except Exception:
        print('Unable to get info on this user')
        raise


def get_channel_features(user_id):
    """Gets information on a user's Twitch channel.

    Args:
        user_id: The ID of a specific Twitch user.

    Returns:
        broadcaster_type: The broadcaster type gathered from the JSON output of an
            API call for a Twitch user. Can be 'partner', 'affiliate', or None.
        view_count: The total view count gathered from the JSON output of an
        API call for a Twitch user.
    Raises:
        IndexError: 'Issue with this user id {}'
    """
    data = get_user_info(user_id)
    broadcaster_type, view_count = None, None

    try:
        broadcaster_type, view_count = data['data'][0]['broadcaster_type'], data['data'][0]['view_count']

    except IndexError as e:
        print('Issue with this user id {}'.format(user_id))
        print(e)

    return broadcaster_type, view_count


def get_item_features(data):
    """Returns a list of item features to be used for input into a recommender model.
    """
    item_features = []
    channels = list(data['channel'].unique())
    for channel in channels:
        try:
            broadcaster_type, view_count = get_channel_features(channel)
            item_features.append([channel, broadcaster_type, view_count])
            time.sleep(0.075)
        except IndexError:
            pass

    df = pd.DataFrame(item_features, columns=['channel', 'broadcaster_type', 'view_count'])
    return df


def view_count_range(views):
    """Function to categorize view count.
    """
    if views < 100000:
        return 'Less than 100k'
    elif views < 500000:
        return 'Between 100k and 500k'
    elif views < 1000000:
        return 'Between 500k and 1MM'
    elif views < 5000000:
        return 'Between 1MM and 5MM'
    elif views < 10000000:
        return 'Between 5MM and 10MM'
    else:
        return 'More than 10MM'


def item_feature_matrix(df):
    """Creates an item/feature matrix for input into a recommender model.
    """
    df['views'] = df['view_count'].apply(view_count_range)
    df['broadcaster_type'] = df['broadcaster_type'].replace('', 'NA')
    df.drop('view_count', axis=1, inplace=True)
    df = pd.get_dummies(df, columns=['broadcaster_type', 'views'])
    return df


def main(file):
    """Creates an item/feature matrix from a pickled file.

    Args:
        file: A pickled list of tuples representing user relationships.
    """
    # Gathers the user/item interactions into a DataFrame
    interactions = user_item_interactions(file)

    # Gathers the list of item features
    item_features_list = get_item_features(interactions)

    # Creates an item/feature matrix and pickles the output
    item_features = item_feature_matrix(item_features_list)
    with open('item_features.pkl', 'wb') as f:
        pickle.dump(item_features, f)


if __name__ == '__main__':
    main(file)
