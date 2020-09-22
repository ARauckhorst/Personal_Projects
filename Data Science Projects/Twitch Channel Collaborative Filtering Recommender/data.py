"""Gathers user/channel interactions for all of the followers of a specific Twitch channel.

This file gathers all of the followers of an initial Twitch channel. It then finds all of
the channels that each of those users follow themselves. The result is pickled as a list of tuples
and any users that raised an issue. during the API calls are also pickled as a list of users.

This file calls the Twitch public API with multiple threads. Full documentation on the API
can be found here: https://dev.twitch.tv/docs/api/.

Note: In this doc, the phrase "user relationships" is often used when describing an input/output of
a function. These user relationships are stored as tuples like the following example:

(user1, user2)
(user1, user3)
(user2, user3)

For each tuple, the first user follows the second user. So in the example above, user1 follows both user2 and user3.
And user2 follows user3.
"""

import time
import requests
import threading
from collections import deque
import pickle

# Global API credentials

URL = URL
CLIENT_ID = CLIENT_ID
AUTH = AUTH_TOKEN
INITIAL_USER = 'kindafunnygames'
HEAD = {'Client-ID': CLIENT_ID,
        'Authorization': AUTH
        }

# Global stats variables for print_stats() function

LAST_TIME_CALLED = 0.0
SLEEP_TIMES = deque()
START_TIME = time.time()
TOTAL_SLEEP_TIME = 0.0
DONE = False
LAST_EXECUTION = 0.0
NUM_REMAINING_THREADS = 0.0
TOTAL_THREADS = 0.0
NOT_PROCESSED = []


class Consumer:
    """Thread worker class.

        Attributes:
            id: The id of the thread worker (0 - 12)
            follows: A list of users and channels followed that the consumer collects
    """
    def __init__(self, id, follows):
        """Inits Consumer class"""
        self.id = id
        self.follows = follows


def get_initial_user_id(name):
    """Returns the Twitch ID of a channel specified.

    Args:
        name: The name of the channel.

    Returns:
        A user ID string.

    Raises:
        Exception: Unable to get the ID of this user.
    """
    global HEAD
    url = 'https://api.twitch.tv/helix/users?login=' + str(name)

    try:
        r = requests.get(url=url, headers=HEAD)
        return r.json()['data'][0]['id']
    except Exception:
        print('Unable to get the ID of this user')
        raise


def get_followers_of(user_id):
    """Returns the followers of a user.

    This function returns a generator object that yields user/channel relationships.

    Args:
        user_id: The ID of the user on Twitch.

    Yields:
        followers: A generator object that stores tuples of two users.
        The second value in each tuple is the ID passed into this function.
        For example:

        [('22222', '11111')
        ('33333', '11111')]
    """
    followers = []
    pag_key, total = fetch_page(user_id, followers, 'to_id={}')
    num_pages = total // 100 if total % 100 != 0 else (total // 100) - 1
    for _ in range(0, num_pages):
        pag_key, _ = fetch_page(user_id, followers, 'to_id={}', pag_key)

    yield followers


def get_user_follows(user_id):
    """Returns the everyone a user follows.

    This function returns a generator object that yields user/channel relationships.

    Args:
        user_id: The ID of the user on Twitch.

    Yields:
        follows: A generator object that stores tuples of two users.
        The first value in each tuple is the ID passed into this function.
        For example:

        [('22222', '11111')
        ('22222', '33333')]
    """
    follows = []
    pag_key, total = fetch_page(user_id, follows)
    num_pages = total // 100 if total % 100 != 0 else (total // 100) - 1
    for _ in range(0, num_pages):
        yield num_pages
        pag_key, _ = fetch_page(user_id, follows, pag_key=pag_key)

    yield follows


def fetch_page(user_id, user_pairs, param='from_id={}', pag_key=None):
    """Calls the Twitch API to get a page of user data.

    This function calls the Twitch API and continues to append tuples of users
    to a list passed in. It is a helper function to the get_user_follows()
    and get_follows_user() functions.

    Args:
        user_id: The ID of the user on twitch.
        user_pairs: A list of tuples generated from either the
            get_user_follows or get_follows_user functions.
        param: Specifies whether we are getting followers of a user
            or who a user follows.
        pag_key: A pagination key from a previous call.

    Returns:
        pag_key: The pagination key for a user's data (if needed).
        total: A variable set to zero to pass back to the get_user_follows()
            or get_follows_user() functions which will break out of those functions.
    """
    global HEAD, URL, LAST_TIME_CALLED, NOT_PROCESSED

    url = URL + param + '&first=100'

    if pag_key:
        url = url + '&after=' + pag_key
    try:
        LAST_TIME_CALLED = time.time()
        r = requests.get(url=url.format(user_id), headers=HEAD)

        if not r.json()['data']:
            return None, 0

        for item in r.json()['data']:
            user_pairs.append((item['from_id'], item['to_id']))
        pag_key = r.json()['pagination']['cursor']
        total = r.json()['total']

    except Exception as e:
        LAST_TIME_CALLED = time.time()
        NOT_PROCESSED.append(user_id)
        print('Unable to get followers for user_id={}, pag_key={}, exception={}'.format(user_id, pag_key, str(e)))
        pag_key, total = None, 0
    return pag_key, total


def level_order_traversal(users, depth=1):
    """Returns a list of user relationships.

    This function will output a list of users and which users they follow on Twitch.

    Args:
        users: A generator object that yields tuples of users representing a follow relationship.
    """
    global DONE, NUM_REMAINING_THREADS

    def print_stats():
        """Prints stats every 10 seconds while script is running.
        """
        nonlocal finished
        while not finished:
            try:
                print('\nNumber processed = {} \n'
                      'Number of candidates = {} \n'
                      'Number of next candidates = {} \n'
                      'Current Depth = {} \n'
                      'Time elapsed = {} \n'
                      'Time per candidate processed = {} \n'
                      'Total not processed = {} \n'.format(len(seen), len(candidates), len(next_candidates), level,
                                                           time.time() - START_TIME,
                                                           (time.time() - START_TIME) / max(1, len(seen)),
                                                           len(NOT_PROCESSED)))

            except Exception:
                pass

            time.sleep(10.0)

    def print_dots():
        """Prints a line of dots to indicate script is running.
        """
        while not DONE:
            print('.', end='')
            time.sleep(1.0)

    if depth < 0:
        raise ValueError('Invalid input {}'.format(depth))

    finished = False
    user_item = []
    level = 0

    candidates, next_candidates, seen = set(), set(), set()
    start_collecting_stats(print_stats, print_dots)
    next_candidates = set(*users)
    consumers = [Consumer(i, []) for i in range(13)]
    consumer_cv = threading.Condition()

    while next_candidates and level < depth:
        if level == 0:
            start_threads(consumers, consumer_cv, next_candidates, seen)
        level += 1
        while NUM_REMAINING_THREADS > 0:
            time.sleep(1.0)

        for consumer in consumers:
            user_item.extend(consumer.follows)
            next_candidates.update((item[1], None) for item in consumer.follows)
            consumer.follows = []

        NUM_REMAINING_THREADS = len(consumers) * 1.0
        consumer_cv.acquire()
        consumer_cv.notifyAll()
        consumer_cv.release()

    finished = True
    return user_item


def start_collecting_stats(print_stats, print_dots):
    """Starts threads to print stats and dots while level_order_traversal() function is executing.
    """
    threading.Thread(target=print_dots).start()
    threading.Thread(target=print_stats).start()


def consumer_thread(consumer_cv, queue, consumer, seen):
    """The job of each consumer thread.

    This function represents the job that each consumer will continuously perform
    in the level_order_traversal() function. The threads first check if there is
    an available job. Then, the thread takes the next user in the queue to process.
    Finally, the thread processes the user and stores the information to combine
    with the other threads after they are finished.

    Args:
        consumer_cv: A threading Condition object
        queue: A set of user relationships as tuples.
        consumer: The id of the consumer thread worker.
        seen: A set of users already processed.
    """
    global NUM_REMAINING_THREADS, TOTAL_THREADS
    user_id = None
    while not DONE:
        consumer_cv.acquire()
        while not queue and not DONE:
            NUM_REMAINING_THREADS -= 1
            consumer_cv.wait()
        while not user_id and queue:
            user_id = queue.pop()
            if user_id in seen:
                user_id = None
            else:
                seen.add(user_id)
        consumer_cv.release()
        if user_id:
            for new_follows in get_user_follows(user_id[0]):
                time.sleep(NUM_REMAINING_THREADS / TOTAL_THREADS)
                if isinstance(new_follows, list):
                    consumer.follows.extend(new_follows)
                    user_id = None
                    break


def start_threads(consumers, consumer_cv, queue, seen):
    """Starts all of the thread workers.

    This function starts all of the thread workers from the level_order_traversal() function
    and has them execute the consumer_thread() function.

    Args:
        consumers: A list of Consumers.
        consumer_cv: A threading Condition object.
        queue: A set of user relationships as tuples.
        seen: A set of users already processed.
    """
    global NUM_REMAINING_THREADS, TOTAL_THREADS
    NUM_REMAINING_THREADS = 1.0 * len(consumers)
    TOTAL_THREADS = 1.0 * len(consumers)
    for consumer in consumers:
        threading.Thread(target=consumer_thread, args=[consumer_cv, queue, consumer, seen]).start()


def main():
    """Pickles a list of user relationships and pickles a list of users not processed.
    """
    global INITIAL_USER, DONE, START_TIME, NOT_PROCESSED

    # Get the user ID for the channel Kinda Funny Games
    initial_id = get_initial_user_id(INITIAL_USER)

    # Get all of the user ids who follow Kinda Funny Games
    kf_followers = get_followers_of(initial_id)

    # Return all of the channels followed by followers of Kinda Funny Games

    result = level_order_traversal(kf_followers, depth=1)

    print('DONE!')
    with open('user_item_interactions.pkl', 'wb') as f:
        pickle.dump(result, f)
    with open('not_processed.pkl', 'wb') as f:
        pickle.dump(NOT_PROCESSED, f)
    print(time.time() - START_TIME)
    DONE = True


if __name__ == '__main__':
    main()
