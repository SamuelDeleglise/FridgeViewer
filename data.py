#In[]
import pandas as pd
import glob
import ntpath
import re
import numpy as np
from datetime import timedelta, date, time, datetime
#########################################################
# Settings for test

path_data = r'LOGS\DummyFridge\data'
MIN_DATE_ALLOWED = datetime(2018, 8, 5)
MAX_DATE_ALLOWED = datetime.today()
INITIAL_MONTH = datetime.today()
TODAY_DATE  = datetime.today()
TEST_MODE = False

########################################################
def path_leaf(path):
    """ Remove / or \ from a path
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def all_file_paths(path, filetype='.log'):
    """ Transfer the path of folder and return all paths of .log files in the same 
    """
    all_files = glob.glob(path + '/*'+filetype)
    return all_files

def all_folder_paths(path):
    """ Transfer the path of folder and files and return all paths of inner folders  
    """
    all_folders = glob.glob(path + '/*')
    return all_folders

def get_folder_names(folder_paths):
    """ Transfer a list of paths and return all folder names as a list
    """
    folders = []
    # remove the file type
    pattern = re.compile(r'\.\w+')
    for item in folder_paths:

        list_name = path_leaf(item)
        # exclude the files
        if  re.search(pattern, list_name) == None:
            folders.append(list_name)
        else: pass
    return folders

def get_files_names(files_paths_list):
    """ Transfer a list of paths and return all files names as a list
    """
    files = []
    pattern = re.compile(r'\.\w+')
    for item in files_paths_list:

        list_name = path_leaf(item)
        if  re.search(pattern, list_name) != None:
            files.append(re.sub(pattern, '', list_name))
        else: pass
    return files


def get_effect_channels(file_paths_list):
    """ Transfer a list of paths and return all effective channels as a list
    """
    names = []
    new_names = []
    pattern = re.compile(r'(\s|\_)\d+\-\d+\-\d+\.\w+')
    
    for filepath in file_paths_list:
        names.append(re.sub(pattern,'', path_leaf(filepath)))
    
    # remove the error log files
    for name in names:
        if re.match('CH', name):
            new_names.append(name)
    return new_names
###############################################################
# Fast reading
# pd.read_csv('data.csv', index_col='date', parse_dates = 'date')
# pd.read_csv('c:/tmp/test.csv', parse_dates=['date', 'dt2'], index_col=0)
# pd.read_hdf('c:/tmp/test_fix.h5', 'test')

###############################################################
# Time range 
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

def datelist(start_date, end_date):
    date_list =[]
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        date_list.append(single_date)
    return date_list

# return date type
def datelist_date(start_date, end_date):
    date_list =[]
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        date_list.append(single_date.date())
    return date_list
   
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

# Get the data of single day
def get_1day_data_str(single_date, channels, path_data):
    """start_time and end_time require the type 'timedate'
       channels requires the type 'list' 
    """
    path = path_data + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime(r"%y-%m-%d") + '\\'
    
    # for different channels, their data are saved in a dataframe   
    df_channel = pd.DataFrame()
    for chan in channels:
        file_name = chan + ' ' + single_date.strftime(r"%y-%m-%d") + r'.log'

        # get the data from a file
        df = get_file_str(path + file_name)

        # delete the 'Date', 'Time' has the information
        try:
            df = df.rename(columns={'Value': chan})
            df = df.rename(columns={'Time': 'Time_'+chan})
        except KeyError as error:
            print(error)
            print('The aggregation of different channel data fails.')
            print('The channel nay have different data format.')
        else: 
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.concat([df_channel, df], axis=1)
    
    df_channel = df_channel.astype(str)
    return df_channel


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


