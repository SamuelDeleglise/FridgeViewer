from datetime import timedelta, date, time, datetime

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date.today()
end_date = date.today()

CHANNELS = ['CH1 T', 'CH2 T', 'CH5 T', 'CH6 T']
PATH_DATA = 'LOGS\\DummyFridge\\data'
for single_date in daterange(start_date, end_date+timedelta(days=1)):
    print(type(single_date.strftime("%y-%m-%d")))
    path = PATH_DATA + '\\'+ single_date.strftime("%Y")+ '\\'+ single_date.strftime("%y-%m-%d") +'\\'
    for i, chan in enumerate(CHANNELS):

        file_name = chan + ' '+ single_date.strftime("%y-%m-%d") + r'.log'
        print(path+file_name)
        
        
(end_date - start_date).days

a = date(2019, 4, 23)
b = time(12, 34, 45)
c = datetime(2019, 4, 23, 12, 34, 45)
d = 
print(type(a))
print(type(b))
print(type(c))