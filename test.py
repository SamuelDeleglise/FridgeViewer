import json
import os
from data import*


def update_jsonfile(path, key, value, valuetype=str):
    # if not exist, create an empty json file 
    if not os.path.isfile(path):
        with open(path, 'w',  encoding='utf-8') as jsonfile:
            jsonfile.write(json.dumps({}))
    
    # Open the JSON file for reading
    with open(path, 'r+',  encoding='utf-8') as jsonfile:
        data = json.load(jsonfile) 
        # update data
        
        if key in data.keys():
            if valuetype is str:
                if value not in data[key]:
                    data[key].append(value)
            elif valuetype is dict:
                data[key].update(value)
            elif valuetype is list:
                for ele in value:
                    if ele not in data[key]:
                        data[key].extend(ele)
        else:
            if valuetype is dict:
                data.update({key: value})
            elif valuetype is str:
                data.update({key: [value]})
            elif valuetype is list:
                data.update({key: value})
        jsonfile.seek(0)  # rewind
        jsonfile.write(json.dumps(data, indent=4))
        # this deals with the case where the new data is smaller than the previous.
        jsonfile.truncate()
    return None

def write_channels_config(path):
    try:
        date_list = get_folder_names(all_folder_paths(path))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the year list')
    else:

        i = 0
        for single_date_str in date_list: 
            channels_update = set()
            try:
                path_log = all_file_paths(path + '\\'+ single_date_str, '.log')
                log = get_channels(path_log)
                channels_update.update(set(log))
            except:
                print('No log files')
            try:
                path_chan = all_file_paths(path + '\\'+ single_date_str, '.chan')
                chan = get_channels(path_chan)
                channels_update.update(set(chan))
            except:
                print('No chan files')
            
            i = i+1
            try:
                update_jsonfile(path + r'\channels.json', single_date_str, list(channels_update), valuetype=list)
            except:
                print(i)
                print(single_date_str)
            
    return None

def write_info(path_lab):
    try:
        experiment_update = get_folder_names(all_folder_paths(path_lab))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the experiment list')
    else:
        for exp in experiment_update:
            update_jsonfile(path_lab + r'\exp_info.json', 'experiments', exp)
    
            try:
                years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
            except FileNotFoundError as error:
                print(error)
                print('Cannot get the year list')
            else:
                temp = {}
                temp[exp] = years_update
                update_jsonfile(path_lab + r'\exp_info.json', 'years', temp, valuetype= dict)  
    return None    
     