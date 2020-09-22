"""This module is designed to scrape data from the PGA tour website. 
    
The module gathers the statistics for each player who has this information 
recorded over a range of calendar years that is specified.

The output of this module is a DataFrame that can be used for further analysis.

"""

# List of stat numbers in URL headers

from bs4 import BeautifulSoup
import requests
import pandas as pd

stats = ['120', '101', '102', '190', '199', '02674', '02675', '02564', 
         '130', '426', '119', '331', '02414', '109']
"""list: List of stats based on number from the PGA tour website."""

cols = ['scoring_avg', 'driving_dist', 'driving_acc',
        'gir_fairway','gir_other', 'sg_tee_to_green', 'sg_total', 'sg_putting', 'scrambling', 
        '3_putt_avoid', 'putts_per_round', 'prox_to_hole', 'bogey_avoidance', 
        'earnings']
"""list: List of stat names that correspond to the stat numbers."""

def get_soup(url):
    """ Takes a url string and converts to a BeautifulSoup object.
    
    Parameters
    ----------
    url : <str> A url in the form of a string.

    Returns
    -------
    soup : <soup> A BeautifulSoup object of the url input. 

    """
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page, 'lxml')
    return soup

def get_links(stats, year):
    """ Takes in a list of stat numbers for the PGA tour as well as a year 
    and returns a list of urls for each stat for for four years starting with
    year paratement.
    
    Parameters
    ----------
    stats : <list> A list of strings for stat numbers from the PGA tour.
    year : <int> The initial year to collect data on each stat.

    Returns
    -------
    urls : <list> A list of url strings.

    """
    urls = []
    #base_url = 'https://www.pgatour.com/stats/stat.'
    base_url = 'https://www.pgatour.com/stats/stat/jcr:content/mainParsys/details.'
    for stat in stats:
        # for i in range(year, year + 4):
        urls.append(base_url + stat + '.y' + str(year) + '.scontent.html')
    return urls

def get_players_on_money_list(year):
    """Takes in a year and returns a list of players who earned money on the PGA
    tour in that given year.
    
    Parameters
    ----------
    year : <int> The year to collect players from the money list.

    Returns
    -------
    <list> A list of player names.
    
    """
    url = 'https://www.pgatour.com/stats/stat/jcr:content/mainParsys/details.109.y{}.scontent.html'.format(year)
    soup = get_soup(url)
    soup = get_soup(url)
    find_players = soup.find(class_='details-table-wrap').find_all('td', class_='player-name')
    return [item.text.replace('\n', '') for item in find_players]

def add_nans_to_dict(d):
    """Adds null values to a dictionary to ensure item lists are same length."""
    
    global cols
    for k, v in d.items():
        if len(v) != len(cols):
            v.extend([None] * (len(cols)-len(v)))
    return d

def get_stats(stats, year, player_list):
    """This function returns a dictionary of players and their associated 
    statistics for a given season of golf. 
    
    Parameters
    ----------
    stats : <list> A list of stat numbers from the PGA tour website. 
    year: <int> The year to collect the stats on.
    player_list: <list> A list of player names to collect stats on.

    Returns
    -------
    stats_dict <dict> A dictionary with player names as keys and their associated
    stats in a list form as the values.
    
    Example: 
        returns {'Tiger Woods': ['70', '302.0', '64.4', '68.7']}
    
    Note that not all players will have a value for all stats, so the value lists
    may not be the same length.
    
    """
    
    urls = get_links(stats, year)
    stats_dict = {k:[] for k in player_list}
    
    for url in urls:
        players_url, stats_url = [], []
        soup = get_soup(url)
        find_players = soup.find(class_='details-table-wrap').find_all('td', class_='player-name')
        find_stats = soup.find(class_='details-table-wrap').find_all('td', class_='')
    
        for player in find_players:
            players_url.append(player.text.replace('\n', ''))
            
        for i, num in enumerate(find_stats):
            if i % 2 != 0:
                stats_url.append(num.text)
        
        d = dict(zip(players_url, stats_url))
        
        for k, v in d.items():
            if k in stats_dict:
                stats_dict[k].append(v)
                
    return stats_dict

def create_df(stats, year, players, cols):
    """This function creates a dataframe from a dictionary of player stats."""
    
    df = get_stats(stats, year, players)
    df = add_nans_to_dict(df)
    df = pd.DataFrame(df).T
    df.columns = cols
    return df

df2019 = create_df(stats, 2019, get_players_on_money_list(2019), cols).reset_index()
df2018 = create_df(stats, 2018, get_players_on_money_list(2018), cols).reset_index()
df2017 = create_df(stats, 2017, get_players_on_money_list(2017), cols).reset_index()
df2016 = create_df(stats, 2016, get_players_on_money_list(2016), cols).reset_index()
df2015 = create_df(stats, 2015, get_players_on_money_list(2015), cols).reset_index()
