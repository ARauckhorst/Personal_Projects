## Predicting SBA Loan Defaults using Classification 

### Summary

In this project, I used classification to predict whether or not a small
business loan would default. I tested models including Random Forest, Logistic Regression, KNN, Naive Bayes, and XGBoost.

I measured the success of my model with an F-beta score weighted towards recall, as the cost of approving a loan that will default (recall) was much higher than passing on a loan that would have paid-in-full (precision).

Finally, I then created a Streamlit application where a user can answer questions
and determine whether or not they are approved for an SBA loan
based on the classification model.

### Data

Data gathered was from Kaggle user Mirbek Toktogaraev and can 
be found here:

https://www.kaggle.com/mirbektoktogaraev/should-this-loan-be-approved-or-denied

### Files

- data_cleaning.py - Cleans data and applies feature engineering
- model.py - Trains and pickles a final production model
- loan_mapping - Mapping variables for project-3-streamlit.py
- project-3-streamlit.py - A Streamlit application utilizing the final
production model

### Contact Me

| Contact Method |  |
| --- | --- |
| Email | adamr@hey.com |
| LinkedIn | https://www.linkedin.com/in/adamrauckhorst/ |
