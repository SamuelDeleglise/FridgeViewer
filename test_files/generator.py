#In[]
import pandas as pd
import numpy as np
import struct as st
import time

def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

path = r"C:\Users\YIFAN\Documents\GitHub\LOGS\Interference\data\2019\19-06-19\new_channel 19-06-19.chan"

def data_update(path): 
    f = open(path, 'rb')
    log = follow(f)

    for line in log:
            print(line)
            len(line)
            a = np.frombuffer(line)
            print(a[1::2])
            
    

#%%
