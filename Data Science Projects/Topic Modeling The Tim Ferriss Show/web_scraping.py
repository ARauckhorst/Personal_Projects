"""
This script scrapes episodes of The Tim Ferriss show from the blog that they are housed
(tim.blog) and creates and pickles a DataFrame of the episode text.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://tim.blog/2018/09/20/all-transcripts-from-the-tim-ferriss-show/"


def extract_text(url):
    """Extracts episode text from a URL on tim.blog.

    Args:
        url -- (str) a url to scrape episode text from
    """
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    episode_text = soup.findAll("div", {"class": "entry-content"})[0].text
    return episode_text


def extract_urls(base_url):
    """Takes in a base url to the page where all of the TFS transcript links are
    housed and extracts the links on that page. Returns a list of extracted
    links.

    Args:
        base_url -- (str) the base url to extract episode links from
    """
    urls_page_page = urlopen(base_url)
    soup_urls_page = BeautifulSoup(urls_page_page, "html.parser")
    extracted_url_all = soup_urls_page.findAll("div", {"class": "entry-content"})[0].findAll('a', href=True)
    extracted_urls = []
    for a in extracted_url_all:
        extracted_urls.append(a['href'])
    return extracted_urls


def podcast_urls(extracted_urls):
    """Extracts the podcast transcript urls from a list of links.
    """
    podcast_urls = []
    for url in extracted_urls:
        if 'transcripts' in url or 'transcript' in url:
            podcast_urls.append(url)
    # pop the first link since it is just a link to his blog
    podcast_urls.pop(0)
    return podcast_urls


def text_to_list(urls):
    """Extracts the text for the podcast transcript from a list of links
    to each transcript.
    """
    text_list = []
    for url in urls:
        extract = extract_text(url)
        text_list.append(extract)
    return text_list


def create_corpus(podcast_urls, transcripts):
    """Creates a DataFrame with the text of each transcript and the link
    to the corresponding episode. Pickles the DataFrame after.
    """
    df = pd.DataFrame([podcast_urls, transcripts]).transpose()
    df.columns = ['episode', 'transcript']
    df = df.reset_index().drop(['index'], axis=1)
    df.to_pickle('tfs_transcripts.pkl')


def main():
    """Calls all internal functions to create a pickled DataFrame of
    Tim Ferriss Show episode text.
    """

    extracted_urls = extract_urls(BASE)
    podcasts = podcast_urls(extracted_urls)
    transcripts = text_to_list(podcasts)
    create_corpus(podcasts, transcripts)


main()
