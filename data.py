#In[]
import pandas as pd
import glob
import ntpath
import re
import numpy as np
from datetime import timedelta, date, time, datetime
#########################################################
# Settings

path_data = r'LOGS\DummyFridge\data'
# Date range
MIN_DATE_ALLOWED = datetime(2018, 8, 5)
MAX_DATE_ALLOWED = datetime.today()
INITIAL_MONTH = datetime.today()
TODAY_DATE  = datetime.today()
TEST_MODE = False

path_test = r'C:\Users\YIFAN\Documents\GitHub\FridgeViewer\LOGS\DummyFridge\data\2019\19-04-13'
path_test2 = r'C:\Users\YIFAN\Documents\GitHub\FridgeViewer\LOGS'
########################################################




###############################################################
# Time range 
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

def get_file(path):
    """ The original format of data is 'date,time,value',
        This function returns a pandas format with frames 'Date', 'Time', 'Value',
        Their types are 'object', 'datetime64[ns]', 'float64' accordingly.
    """
    df = pd.read_csv(path, sep=r",", names=['Date','Time','Value'], engine='python')
    df.Time = pd.to_datetime(df.Date +' '+ df.Time, format=r' %d-%m-%y %H:%M:%S')
    # delete the 'Date', 'Time' has the information 
    df = df.drop('Date', 1)
    return df

def get_file_str(path):
    """ The original format of data is 'date,time,value',
        This function returns a pandas format with frames 'Date', 'Time', 'Value',
        Their types are 'string'.
    """
    df = pd.read_csv(path, sep=r",", names=['Date','Time','Value'], engine='python')
    df.Time = pd.to_datetime(df.Date +' '+ df.Time, format=r' %d-%m-%y %H:%M:%S')
    # delete the 'Date', 'Time' has the information 
    df = df.drop('Date', 1)
    return df


def get_data_str(start_date, end_date, channels, path_data):
    """start_time and end_time require the type 'timedate'
       channels requires the type 'list'
       
    """
    df_full = pd.DataFrame()
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        
        path = path_data + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime(r"%y-%m-%d") + '\\'
        # for different channels, their data are saved in an object
        df_channel = pd.DataFrame()
        
        for chan in channels:
            file_name = chan + ' ' + single_date.strftime(r"%y-%m-%d") + r'.log'

            # get the data from a file
            df = get_file_str(path + file_name)

            # delete the 'Date', 'Time' has the information 
            df = df.rename(columns={'Value': chan})
            df = df.rename(columns={'Time': 'Time_'+chan})
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.concat([df_channel, df], axis=1)
        
        if df_full.empty:
            df_full = df_channel
        else: df_full = pd.concat([df_full, df_channel], axis=0)
        
        df_full = df_full.astype(str)
    return df_full

# By defaut, it gets the data of today
def get_data_simple(start_date, end_date, channels, path_data):
    """start_time and end_time should be the type 'timedate'
    """
    df_full = pd.DataFrame()
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        
        path = path_data + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime("%y-%m-%d") + '\\'
        # for different channels, their data are saved in an object
        df_channel = pd.DataFrame()
        for i, chan in enumerate(channels):
            file_name = chan + ' ' + single_date.strftime("%y-%m-%d") + r'.log'

            # get the data from a file
            df = get_file(path + file_name)

            # delete the 'Date', 'Time' has the information 
            df = df.rename(columns={'Value': chan})
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.merge(df_channel, df, how='outer', on='Time')
        
        if df_full.empty:
            df_full = df_channel
        else: df_full = pd.concat([df_full, df_channel], axis=0)
    return df_full

def get_data(start_date, end_date, channels, path_data):
    """start_time and end_time require the type 'timedate'
       channels requires the type 'list'
    """
    df_full = pd.DataFrame()
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        
        path = path_data + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime(r"%y-%m-%d") + '\\'
        # for different channels, their data are saved in an object
        df_channel = pd.DataFrame()
        
        for chan in channels:
            file_name = chan + ' ' + single_date.strftime(r"%y-%m-%d") + r'.log'

            # get the data from a file
            df = get_file(path + file_name)

            # delete the 'Date', 'Time' has the information 
            df = df.rename(columns={'Value': chan})
            df = df.rename(columns={'Time': 'Time_'+chan})
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.concat([df_channel, df], axis=1)
        
        if df_full.empty:
            df_full = df_channel
        else: df_full = pd.concat([df_full, df_channel], axis=0)
    return df_full


# test mode data
test_data = get_data(datetime(2019, 4, 13), datetime(2019, 4, 14), ['CH1 T', 'CH2 T'], path_data)
test_data2 = get_data(datetime(2019, 4, 13), datetime(2019, 4, 14), ['CH1 P'], path_data)