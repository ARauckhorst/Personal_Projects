## Topic Modeling The Tim Ferriss Show 

### Summary

In this project, I scraped transcripts of one of my favorite podcasts, the Tim 
Ferriss Show.  

I then used topic modeling via LDA (Latent Dirichlet Allocation), a natural language processing technique, to identify
high level themes for the podcast. The themes I discovered were:

- **Business/Investing/Entrepreneurship**
- **Physical Training**
- **Arts/Creativity**
- **Mental Health**

I then used the topic weighting scores for these topics to build a simple 
episode recommender based on collaborative filtering and using cosine similarity
to determine like episodes.

### Data

Data gathered was from the website tim.blog where episode transcripts published
by Tim Ferriss are housed.

### Files

- web_scraping.py - Scrapes episode text
- data_cleaning.py - Cleans and processes text
- model.py - Contains LDA model and simple recommender

### Contact Me

| Contact Method |  |
| --- | --- |
| Email | adamr@hey.com |
| LinkedIn | https://www.linkedin.com/in/adamrauckhorst/ |
