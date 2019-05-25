#In[]
import glob
import ntpath
import re
import numpy as np
from datetime import timedelta, date, time, datetime
import os


path_data_auto = r'LOGS\DummyFridge\data'
current_address = os.path.abspath('.')


def all_file_paths(path, filetype='.log'):
    """ Argument is a  path
    Return all paths of .logf iles in one directory 
    """
    all_files = glob.glob(path + '/*'+filetype)
    return all_files

def all_folder_paths(path):
    """  Argument is a path
    Return all paths of folder in one directory 
    """
    all_folders = glob.glob(pacth + '/*')
    return all_folders

def path_leaf(path):
    """ remove / or \
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_folder(all_folders_or_files):
    """ Argument is a list of path
        Return all folder names as a list
    """
    folders = []
    pattern = re.compile(r'\.\w+')
    for item in all_folders_or_files:
        if  re.search(pattern, path_leaf(item)) == None:
            folders.append(re.sub(pattern,'', path_leaf(item)))
        else: pass
    return folders


def get_file_channels(all_files_path):
    """ Argument is a list of path 
    """
    names = []
    pattern = re.compile(r'(\s|\_)\d+\-\d+\-\d+\.\w+')
    
    for filepath in all_files_path:
        names.append(re.sub(pattern,'', path_leaf(filepath)))
    return names