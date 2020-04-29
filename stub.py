###     TEST STUB     ###

import requests
import ast
import json
import re
from requests.exceptions import HTTPError
import plotly
from dateutil.relativedelta import *
from collections import Counter
import isodate
import datetime
import plotly.graph_objects as go
import plotly.figure_factory as ff
import random
import pytz
import anvil.media
import sys

#var = anvil.media.from_file(filename='./timeline.png',mime_type='image/png')
#print(var)


def allBuckets():
    try:
        buckets = requests.get(hostname + bucketdir)

        # If the response was successful, no Exception will be raised
        buckets.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        bucketdict = json.loads(buckets.content)
        return bucketdict

#remain static
hostname = 'http://localhost:5600/'
bucketdir = 'api/0/buckets/'

#find the bucket names for this pc
buckets = allBuckets()
windowBucket = ''
for name in buckets:
    if re.search('window',name,re.IGNORECASE):
        windowBucket = name
webBucket = ''
for name in buckets:
    if re.search('web',name,re.IGNORECASE):
        webBucket = name

def dateClean(Date):
    return Date.replace(tzinfo=pytz.UTC)

#returns dict of all current buckets' metadata

#get bucket metadata
#pass in a string
def getBucket(bucketid):
    try:
        bucket = requests.get(hostname + bucketdir + bucketid)
        # If the response was successful, no Exception will be raised
        bucket.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        bucketdict = json.loads(bucket.content)
        return bucketdict

def getCounts(catdict):
    events = getBucketEvents('aw-watcher-window_Andress-MacBook-Pro.local')
    countlist = countCategory(catdict,events)
    return countlist

def getCategories():
    with open('categories.json', 'r') as infile:
        categories = json.load(infile)
        infile.close()
    return categories

def saveCategories(categories):
    with open('categories.json', 'w') as outfile:
        json.dump(categories,outfile)
        outfile.close()

def getTypes():
    with open('types.json', 'r') as infile:
        types = json.load(infile)
        infile.close()
    return types

#get events from a bucket
#pass in a string
#return list of events
def getBucketEvents(bucketid):
    try:
        events = requests.get(hostname + bucketdir + bucketid + '/events')

        # If the response was successful, no Exception will be raised
        events.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        eventdict = json.loads(events.content)
        return eventdict

#returns true if an event is in the specified category
#pass in event (dict), category (List)
#for use on currentwindow bucket
def inCategory(event,category):
    eventname = event['data']['app']
    inCat = False
    for appname in category:
        if re.search(appname,eventname,re.IGNORECASE):
            inCat = True
            return inCat
    return inCat

#FIXME FIXME change this before using in anvil
#maybe instead pass in dict of cat_list and return matching dict of counts
def countCategory(cat_dict, event_list):
    n = 0
    countdict = dict()
    countdict['Uncategorized'] = 0
    for cat in cat_dict:
        countdict[cat] = 0
    for event in event_list:
        #countdict[category] = 0
        n = n + 1
        categorized = False
        for category in cat_dict:
            if inCategory(event,cat_dict[category]):
                countdict[category] += 1
                categorized = True
        if not categorized:
            countdict['Uncategorized'] += 1
    return countdict

###
### MAIN CODE
###
def getEventsData():
    events_list = getBucketEvents('aw-watcher-window_Andress-MacBook-Pro.local')
    data = list()
    categories = getCategories()
    for event in events_list:
        data.append(event['data'])
        data[-1]['timestamp'] = event['timestamp']
        data[-1]['duration'] = float(event['duration'])
        data[-1]['endstamp'] = isodate.parse_datetime(data[-1]['timestamp']) + relativedelta(seconds=+data[-1]['duration'])

        categorized = False
        for category in categories:
            if inCategory(event,categories[category]):
                data[-1]['category'] = category
                categorized = True
            #else:
        if not categorized:
            data[-1]['category'] = 'Uncategorized'
    return data

def getAppTimeline():
    data = getEventsData()
    #seed = 2000
    #random.seed(seed)
    #r = lambda: random.randint(0,255)
    #colors = ['#%02X%02X%02X' % (r(),r(),r())]

    format = list()
    for i in range(len(data)):
        format.append(dict())
        format[i]['Task'] = 'Apps'
        format[i]['Start'] = data[i]['timestamp']
        format[i]['Finish'] = data[i]['endstamp']
        format[i]['Resource'] = data[i]['category']
        #colors.append('#%02X%02X%02X' % (r(),r(),r()))
        #seed = seed / 2
        #random.seed(seed)
        #colors=colors
    fig = ff.create_gantt(format,index_col='Resource',show_colorbar=True,group_tasks=True)
    return fig

def getCategoryTimeline():
    pass
#hour = 1
#start = dateClean(isodate.parse_datetime(datetime.datetime.now().isoformat()))
#end = dateClean(isodate.parse_datetime(datetime.datetime.now().isoformat()) + relativedelta(hours=-hour))
#print(start)
#print(end)
#print(start>end)
#events = allBuckets()
#print(events)
app = getBucketEvents(windowBucket)
print(app[0])
web = getBucketEvents(webBucket)
print(web[0])
#figure = getAppTimeline()
#figure.show()
#print('finished')

#countlist = countCategory(catdict,events)
#print(len(events))
#print(type(countlist))
#print(countlist)

#labels = ['work','leisure']
#vals = [countlist[0][1],countlist[1][1]]

#pie = go.Figure(data=go.Pie(labels=labels,values=vals))
#pie.show()
#print(watch)
# Using keys() + list()
# Getting first key in dictionary
#res = list(all.keys())[0]
#print(res)
#events = getBucketEvents(res)
#print(events[0])
#print(inCategory(events[0],workCat))

#evnt = getBucket(res)
#print(evnt)
#res2 = evnt['id']
#print(res2)
#print(all)
