# Import packages
import logging
import pandas as pd
from pandas.io.sql import DatabaseError
import numpy as np
from datetime import date, datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Configure python logging
logging.basicConfig(filename='app.log', filemode='w',level=logging.INFO)


def fetch_data():
    '''
    Function to detch data form COVID ActNow API
    '''

    api_key = 'YOUR_API_KEY_HERE'
    states_url = 'https://api.covidactnow.org/v2/states.timeseries.csv?apiKey='+api_key
    US_url = 'https://api.covidactnow.org/v2/country/US.timeseries.csv?apiKey='+api_key 
    US_data = pd.read_csv(US_url)
    states_data = pd.read_csv(states_url)
    logging.info(states_data['state'].unique())
    return US_data, states_data

def process_data(data):
    '''
    Function to perform preprocessing and calculate rolling 7-day means for some covid metrics.
    '''
        
    #data = data[data['date'] != str(date.today())]
    data['metrics.meanNewCases'] = data['actuals.newCases'] .rolling(window=7).mean()
    data['metrics.meanIcuCapacityRatio'] = data['metrics.icuCapacityRatio'].rolling(window=7).mean()
    data['metrics.meanTestPositivityRatio'] = data['metrics.testPositivityRatio'].rolling(window=7).mean()
    return data

def main():
    '''
    Main function that will:
        1. Fetch data
        2. Preprocess data
        3. Save data
    '''

    US_data, states_data = fetch_data()
    logging.info("data download completed at {}".format(datetime.now(tz=None)))

    US_data = process_data(US_data)
    states_data = process_data(states_data)
    logging.info("data processing completed at {}".format(datetime.now(tz=None)))

    US_data.to_csv('data/US_data.csv')
    states_data.to_csv('data/states_data.csv')
    logging.info("data save completed at {}".format(datetime.now(tz=None)))

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    main()
    scheduler.add_job(main, 'interval', seconds =60*60*6) # fetch data every 6 hours
    scheduler.start()