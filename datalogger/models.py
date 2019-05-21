from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from pyinstruments.datastore.settings import MEDIA_ROOT
import time
from datetime import datetime
import pandas
import h5py
import os.path
import numpy as np
import pyinstruments

NaN = float('NaN')

class Sensor(models.Model):
    name = models.CharField(max_length = 255)
    description = models.CharField(max_length = 2047, blank=True)
    
    def __unicode__(self):
        return self.name

class MeasurementPoint(models.Model):
    
    def __unicode__(self):
        return str(self.sensor) + ':'+ str(self.value)
    
    sensor = models.ForeignKey(Sensor,
                               related_name='measurement_points', \
                               blank=True)
    value = models.FloatField()
    time = models.FloatField(db_index=True)
    
    class Meta: 
        ordering = ['time']
        get_latest_by = 'time'

    @property
    def sensor_name(self):
        return self.sensor.name
    
    @sensor_name.setter
    def sensor_name(self, name):
        try:
            self.sensor = Sensor.objects.get(name=name)
        except ObjectDoesNotExist:
            new_sensor = Sensor(name=name)
            new_sensor.save()
            self.sensor = new_sensor
        return name

# all data to be logged are to be derived objects from SensingDevice, 
# which provides basic functionality such as storing and retrieving data   

class SensingDevice(object):
    def __init__(self, name, timeout = 30, description = '', minval = 0.0, maxval = 100000.0, raw=False):
        sense = Sensor.objects.get_or_create(name = name)
        self.sensorlog = sense[0]
        if description != ''  :
            self.sensorlog.description = description
            self.sensorlog.save()
        self.MINVAL = minval
        self.MAXVAL = maxval
        self.val = NaN
        self.active = False
        self.timeout = timeout
        self.name = self.sensorlog.name
        self.raw = raw

    @staticmethod
    def now():
        return time.time()
    
    def datetime_to_time(self, datetime):
        return time.mktime(datetime.timetuple())

    def time_to_datetime(self, time):
        return datetime.fromtimestamp(time)
    
    def log(self, value, mtime = -1.):
        if mtime == -1.:
            mtime = self.now()
        self.lastpoint = MeasurementPoint(sensor = self.sensorlog,\
                                                 value = value, \
                                                 time = mtime)
        if value >= self.MINVAL and value <= self.MAXVAL:
            self.lastpoint.save()
        else:
            print("Measurement Error: value " + str(value) + " of sensor "+\
                    self.sensorlog.name + " lies out of defined range. \n")
        return self.lastpoint
    
    #return last point as pandas Series
    #def getlastpoint(self):
    #    return self.toSeries(\
    #        [MeasurementPoint.objects.filter(sensor = self.sensorlog).latest()])
    
    #return last point as tuple
    def create_point(self,value,mtime):
        try:
            v = MeasurementPoint.objects.get(\
                                sensor = self.sensorlog, time=mtime)
        except ObjectDoesNotExist:
            self.log(value,mtime)
            return True
        else:
            if not v.value == value:
                raise ValueError("Trying to overvrite an existing datapoint with a different value for "+\
                                self.name+" at time "+str(mtime)+"!")
            return False
        
    
    def getlastpoint(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        return {'value': val.value, \
                'time': val.time, \
                'age': self.now()-val.time  }

    def getlastvalue(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        return val.value
    
    def getlastgoodvalue(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        if self.now()-val.time < self.timeout:
            return val.value
        else:
            return NaN
    
    def getallpoints(self):
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog)) 

    def getallpoints_raw(self):
        return self.toSeries_raw(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog)) 

    def getallpointssince(self, sincetime):
        if type(sincetime)==datetime:
            sincetime=self.datetime_to_time(sincetime)
        if sincetime <0:
            sincetime+=self.now()
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                                    time__gt = sincetime)) 

    def getallpointsrange(self, starttime, stoptime=NaN):
        if type(starttime)==datetime:
            starttime=self.datetime_to_time(starttime)
        if type(stoptime)==datetime:
            stoptime=self.datetime_to_time(stoptime)
        if stoptime == NaN:
            stoptime = self.now()
        if starttime < 0:
            starttime+=self.now()
            stoptime+=self.now()
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                      time__range = (starttime,stoptime))) 

    def getmeanaround(self, atime = NaN, offset = 60):
        sel = self.getallpointsaround(atime, offset)
        if len(sel)>0:
            return sel.mean()
        else:
            return NaN
 
    def getallpointsaround(self, atime = NaN, offset = NaN):
        if type(atime)==datetime:
            atime=self.datetime_to_time(atime)
        if np.isnan(offset):
            offset = self.timeout
        if np.isnan(atime):
            atime=self.now()
        elif atime <= 0:
            atime+=self.now()
        starttime = atime-offset
        stoptime = atime+offset
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                      time__range = (starttime,stoptime))) 
         
    def toSeries(self, res):
        if self.raw:
            return self.toSeries_raw(res)
        else:
            return pandas.Series(data = [i.value for i in res],\
                index = [datetime.fromtimestamp(k.time) for k in res],\
                name = self.sensorlog.name)

    def toSeries_raw(self, res):
        return pandas.Series(data = [i.value for i in res],\
                index = [k.time for k in res],\
                name = self.sensorlog.name)
    
    def plot(self,lastseconds=-1.):
        if lastseconds == -1:
            since = 0
        else:
            since = self.now()-lastseconds
        df = pandas.DataFrame(self.getallpointssince(since))
        df.plot(style ='k.')


    def makeCurve(self,atime=0, offset = NaN, name = None, format="raw"):
        data = self.getallpointsaround(atime, offset)
        if format == "raw":
            min = self.datetime_to_time(data.index.min())
            data = pandas.Series(data.values, index = [self.datetime_to_time(d)-min for d in data.index])
        curve = pyinstruments.CurveDB()
        if name is None:
            name = self.name
        curve.name = name
        curve.date = datetime.now()
        curve.set_data(data)
        curve.save()
        return curve

def datalogger_backup(filename='default'): 
    "saves all datalogger data to filename"
    written = 0
    if filename=='default':
        filename = os.path.join(MEDIA_ROOT,'datalogger.h5')
    metadata = dict()
    data=dict()
    sensors = Sensor.objects.all()
    if sensors is None:
        raise ValueError("No sensors in datalogger!")
    for sens in sensors:
        metadata[sens.name]=sens.description
        sd = SensingDevice(name=sens.name)
        data[sens.name]=sd.getallpoints_raw()
    with pandas.get_store(filename) as store:
        for sens in sensors:
            store[sens.name] = data[sens.name]
            written+=len(data[sens.name])
    with h5py.File(filename) as the_file:
        try:
            params = the_file["params"]
        except KeyError:
            params = the_file.create_group("params")
        for key, value in metadata.items():
            try:
                params[key]
            except KeyError:  
                params.create_dataset(key, data=value)
            else:
                del params[key]
                params.create_dataset(key, data=value)
    print("Backup finished! "+str(written)+" MeasurementPoints written to "
                                           ""+filename)

def datalogger_recovery(filename='default'):
    "loads the curves at filename into the datalogger"
    if filename=='default':
        filename = os.path.join(MEDIA_ROOT,'datalogger.h5')
    metadata = dict()
    written = 0
    with h5py.File(filename) as the_file:
        try:
            meta = the_file["params"]
        except KeyError:
            print("No descriptions available, no import will be done.")
        else:
            for key, value in meta.items():
                metadata[key] = value
    if metadata is {}:
        raise ValueError("No sensors in datalogger backup file!")
    old_sensors = Sensor.objects.all()
    if old_sensors.count()==0:
        print("No sensors configured, importing data without consistency "
              "checks...")
        with pandas.get_store(filename, "r") as store:
            for sensorname in metadata:
                sens = Sensor(name=sensorname,description=metadata[sensorname])
                sens.save()
                data = store[sensorname]
                for (i,v) in data.items():
                    mp=MeasurementPoint(sensor=sens,\
                                        value = v, \
                                        time = i)
                    written+=1
    else:
        with pandas.get_store(filename, "r") as store:
            for sensorname in metadata:
                sd = SensingDevice(name=sensorname, description=metadata[sensorname])
                data = store[sensorname]
                for (i,v) in data.items():
                    if sd.create_point(v, i):
                        written+=1
    print("Datalogger import finished. Wrote "+str(written)+" "
                                                            "MeasurementPoints. ")
    return written    
