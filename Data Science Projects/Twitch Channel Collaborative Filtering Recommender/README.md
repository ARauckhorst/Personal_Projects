## Collaborative Filtering for Twitch Channel Recommendations

### Summary

In this project, I built a collaborative filtering recommender using data gathered 
from the Twitch public API.

I built a data pipeline using multi-threading to gather data on hundreds of thousands
of users and channels. This data was then used to build a Factorization Machine model 
using a python package called [RankFM](https://rankfm.readthedocs.io/en/latest/home.html).  

For my pipeline, I utilized multi-threading to gather data on users that follow the
Twitch channel [Kinda Funny Games](https://twitch.tv/kindafunnygames). I gathered user/item interactions, 
the main component of collaborative filtering, finding all of the users who follow Kinda
Funny Games, and then finding all of the other channels each of those users follow. I also
gathered data on the individual channels themselves to make my model more robust.

### Data

Data gathered was from the the Twitch public API.

### Files

- data.py - Gathers user/channel interaction data.
- features.py - Gathers channel feature data.
- model.py - Contains RankFM model for collaborative filtering.
