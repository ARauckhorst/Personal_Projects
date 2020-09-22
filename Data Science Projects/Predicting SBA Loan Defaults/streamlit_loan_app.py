"""
This file is a Streamlit application that can be run to
predict whether or not a loan will default based on
user entered information.
"""

import streamlit as st
import pickle
from loan_mapping import map_sector_default, map_state_default, cols
import numpy as np
import pandas as pd
import time

my_model = pickle.load(open("final_model.pkl", "rb"))
st.title('Are you approved for an SBA loan?')
st.text('\n')
st.text('The United States SBA was founded in 1953 to promote small \n'
        'business access to information and credit. Small businesses are an economic \n'
        'engine for innovation and job growth so it is important that credit be accessible \n'
        'to help these companies thrive! \n'
        '\n'
        'Please enter some information below to determine if you qualify for an SBA loan.')

gross = st.slider('What is the requested amount for the loan (USD)?',
                  min_value=500,
                  max_value=200000,
                  value=50000,
                  step=100)
term = st.slider('How long does this customer need the loan (months)?',
                 min_value=6,
                 max_value=360,
                 value=36,
                 step=6
                 )

state = st.selectbox('What state is the business located in?',
                     ("AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                      "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                      "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                      "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                      "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"))

sector = st.selectbox('What sector is this business in?',
                      ('Agriculture, forestry, fishing and hunting',
                       'Mining, quarrying, and oil and gas extraction',
                       'Utilities',
                       'Construction',
                       'Manufacturing',
                       'Wholesale trade',
                       'Retail trade',
                       'Transportation and warehousing',
                       'Information',
                       'Finance and insurance',
                       'Real estate and rental and leasing',
                       'Professional, scientific, and technical services',
                       'Management of companies and enterprises',
                       'Administrative and support and waste management and remediation services',
                       'Educational services',
                       'Health care and social assistance',
                       'Arts, entertainment, and recreation',
                       'Accommodation and food services'))

bank = st.selectbox('Which bank will this loan be authorized through?',
                    ('Capital One National', 'Chase', 'PNC Bank',
                     'US Bank National', 'Wells Fargo', 'Bank of America'))

employees = st.slider('How many employees does the business have?',
                      min_value=0,
                      max_value=500,
                      value=10,
                      step=1)

jobs_created = st.slider('How many jobs will this loan help create (if any)?',
                         min_value=0,
                         max_value=500,
                         value=10,
                         step=1)

jobs_retained = st.slider('How many jobs will this loan help retain (if any)?',
                          min_value=0,
                          max_value=500,
                          value=10,
                          step=1)

new_existing = st.radio('Is this a new or existing business?', ('New', 'Existing'))

franchise = st.checkbox('The business is a franchise.')

urban_or_rural = st.checkbox('The business is located in an urban area.')

rev_cred = st.checkbox('The customer needs a revolving line of credit.')

user_inputs = [term, employees, new_existing, jobs_created, jobs_retained, franchise, urban_or_rural,
               rev_cred, gross, state, sector, bank]


def loan_approved(inputs, model=my_model, cols=cols):
    loan_term = float(inputs[0])
    num_employee = float(inputs[1])
    new_exist = 1.0 if inputs[2] == 'New' else 0.0
    create = float(inputs[3])
    retained = float(inputs[4])
    is_franchise = float(inputs[5])
    is_urban = float(inputs[6])
    rev_credit = float(inputs[7])
    low_doc = 1.0 if term < 25000 else 0.0
    value = inputs[8]
    real_estate = 0
    state_default_avg = map_state_default[inputs[9]]
    sector_avg_default = map_sector_default[inputs[10]]
    capital_one = 1 if inputs[11] == 'Capital One National' else 0
    citizens_bank = 0
    chase_bank = 1 if inputs[11] == 'Chase' else 0
    other_bank = 0
    pnc_bank = 1 if inputs[11] == 'PNC Bank' else 0
    us_bank = 1 if inputs[11] == 'US Bank National' else 0
    wells_fargo_bank = 1 if inputs[11] == 'Wells Fargo' else 0
    state_times_sector = state_default_avg * sector_avg_default

    input_df = pd.DataFrame(np.array([loan_term, num_employee, new_exist, create, retained, is_franchise,
                                      is_urban, rev_credit, low_doc, value, real_estate, state_default_avg,
                                      sector_avg_default, capital_one, citizens_bank, chase_bank,
                                      other_bank, pnc_bank, us_bank, wells_fargo_bank, state_times_sector])).T

    input_df.columns = cols

    pred = model.predict(input_df)

    if pred == 0:
        st.balloons()
        st.success("You're approved for your SBA loan!")
    else:
        st.warning("Unfortunately, this loan cannot be approved at this time.")


approve = st.button('Check if loan is approved...')

if approve:
    with st.spinner('Wait for it...'):
        time.sleep(3)
        loan_approved(user_inputs)
