"""
This script loads data from Postgres SQL in AWS EC2
into a Pandas DataFrame. It then cleans the data
and applies feature engineering based on information
collected during exploratory data analysis.

This script outputs a CSV of cleaned data with feature
engineered columns.
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np

banks = ['BANK OF AMERICA NATL ASSOC',
         'WELLS FARGO BANK NATL ASSOC',
         'JPMORGAN CHASE BANK NATL ASSOC',
         'CITIZENS BANK NATL ASSOC',
         'U.S. BANK NATIONAL ASSOCIATION',
         'PNC BANK, NATIONAL ASSOCIATION',
         'CAPITAL ONE NATL ASSOC']


# Load data into DataFrame
def get_data_from_aws(query):
    """Connects to Postgres SQL on AWS and returns a dataframe
    of the queried data.

    Args:
        query--SQL query
    """
    cnx = create_engine('postgresql://ubuntu@54.67.29.114:5432/loans')
    df = pd.read_sql_query(query, cnx)
    return df


def import_data():
    """Returns a DataFrame with the loan data.
    """
    sba_data = get_data_from_aws('''SELECT * FROM loan_records''')
    return sba_data


# Clean the data
def data_cleaning(df, options=[1, 0], banks=banks):
    """Returns a DataFrame with columns cleaned up for feature engineering.
    """

    # Dropping columns
    df.drop(['loan_num', 'biz_name', 'chg_off_date'], axis=1, inplace=True)

    # Dropping nulls
    df.dropna(axis=0, inplace=True)

    # Cleaning dollar value columns
    df['disbursement_gross'] = df['disbursement_gross'].str.replace('$', '').str.replace(',', '').astype(float)
    df['gross_approve'] = df['gross_approve'].str.replace('$', '').str.replace(',', '').astype(float)
    df['sba_approve'] = df['sba_approve'].str.replace('$', '').str.replace(',', '').astype(float)
    df['balance_gross'] = df['balance_gross'].str.replace('$', '').str.replace(',', '').astype(float)
    df['chg_off_gross'] = df['chg_off_gross'].str.replace('$', '').str.replace(',', '').astype(float)

    # Changing column values to binary
    df['new_exist'].replace((1, 2), (0, 1), inplace=True)
    df['rev_line_cr'].replace(('Y', 'N', '0'), (1, 0, 0), inplace=True)
    df['low_doc'].replace(('Y', 'N', '0'), (1, 0), inplace=True)
    df = df[df['rev_line_cr'].isin(options)]
    df['rev_line_cr'] = df['rev_line_cr'].astype(int)
    df = df[df['low_doc'].isin(options)]
    df['low_doc'] = df['low_doc'].astype(int)
    df['franchise_code'] = df['franchise_code'].replace(1, 0)
    df['franchise_code'] = np.where((df['franchise_code'] != 0), 1, df['franchise_code'])

    # Consolidating bank options to top banks or else 'other'
    df['bank'] = df['bank'].apply(lambda x: x if x in banks else 'OTHER')

    # Mapping sector to NAICS code and filling in nulls
    df['sector'] = df['naics'].astype('str').apply(lambda x: x[:2])
    df['sector'] = df['sector'].map({
        '00': 'No sector',
        '11': 'Ag/For/Fish/Hunt',
        '21': 'Min/Quar/Oil_Gas_ext',
        '22': 'Utilities',
        '23': 'Construction',
        '31': 'Manufacturing',
        '32': 'Manufacturing',
        '33': 'Manufacturing',
        '42': 'Wholesale_trade',
        '44': 'Retail_trade',
        '45': 'Retail_trade',
        '48': 'Trans/Ware',
        '49': 'Trans/Ware',
        '51': 'Information',
        '52': 'Finance/Insurance',
        '53': 'RE/Rental/Lease',
        '54': 'Prof/Science/Tech',
        '55': 'Mgmt_comp',
        '56': 'Admin_sup/Waste_Mgmt_Rem',
        '61': 'Educational',
        '62': 'Healthcare/Social_assist',
        '71': 'Arts/Entertain/Rec',
        '72': 'Accom/Food_serv',
        '81': 'Other_no_pub',
        '92': 'Public_Admin'})
    df['sector'].fillna('No sector')

    # Removing 1976A from year column
    df['approv_year'] = df['approv_year'].replace('1976A', '1976')
    df['approv_year'] = df['approv_year'].astype(int)

    # Creating target column
    df['default'] = df['mis_status'].replace(('P I F', 'CHGOFF'), (0, 1))

    return df


# Feature engineering for the data
def feature_engineering(df):
    """Returns a DataFrame with columns added for
    real estate collateral, default rates for state and sector,
    and one-hot encoding for banks.
    """

    # Add column for real estate
    df['real_estate'] = df['term'].apply(lambda x: 1 if x > 240 else 0)

    # Add column for state default rates gathered from training set
    map_state_default = dict(train.groupby(['state'])['default'].mean())
    df['state_default_avg'] = df['state'].map(map_state_default)

    # Add column for sector default rates gathered from training set
    map_sector_default = dict(df.groupby(['sector'])['default'].mean())
    df['sector_default_avg'] = df['sector'].map(map_sector_default)
    df['sector'] = df['sector'].fillna('Not given')
    df['sector_default_avg'] = df['sector_default_avg'].fillna(df['sector_default_avg'].mean())

    # Create dummy columns for bank
    df = df.join(pd.get_dummies(df['bank'], drop_first=True))

    # Create interaction term column for state default times sector default
    df['state_times_sector_default'] = df['state_default_avg'] * df['sector_default_avg']

    return df


def main():
    """Loads the SBA loan dataset, performs data cleaning and feature engineering,
    and saves the dataset as a csv file.
    """
    # Loading the data
    sba_data = import_data()

    # Cleaning and feature engineering
    sba_data = data_cleaning(sba_data)
    sba_data = feature_engineering(sba_data)

    # Export DataFrame to a CSV
    sba_data.to_csv('sba_data.csv')


main()
