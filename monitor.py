import requests
import json
import re
from requests.exceptions import HTTPError
import anvil.server
import anvil.media
import isodate
import plotly
from plotly import graph_objects as go
import plotly.figure_factory as ff
import datetime
import pytz
import plotly.io as pio
import sys
from heapq import nlargest
from dateutil.relativedelta import *
# key for uplink
uplink = 'UDA2WZMHEM56YXZF7CB6UPE7-NEFSIWS76ODZ7GUB'
hostname = 'http://localhost:5600/'
bucketdir = 'api/0/buckets/'

### all these functions read and write to the files of both types of category, and their
### respective productivity types ('Productive','Neutral','Unproductive')

@anvil.server.callable
def getCategories():
    with open('categories.json', 'r') as infile:
        categories = json.load(infile)
        infile.close()
    return categories

@anvil.server.callable
def saveCategories(categories):
    with open('categories.json', 'w') as outfile:
        json.dump(categories,outfile)
        outfile.close()

@anvil.server.callable
def getTypes():
    with open('types.json', 'r') as infile:
        types = json.load(infile)
        infile.close()
    return types

@anvil.server.callable
def saveTypes(types):
    with open('types.json', 'w') as outfile:
        json.dump(types,outfile)
        outfile.close()

@anvil.server.callable
def getBrowserCategories():
    with open('browsercategories.json', 'r') as infile:
        categories = json.load(infile)
        infile.close()
    return categories

@anvil.server.callable
def saveBrowserCategories(categories):
    with open('browsercategories.json', 'w') as outfile:
        json.dump(categories,outfile)
        outfile.close()

@anvil.server.callable
def getBrowserTypes():
    with open('browsertypes.json', 'r') as infile:
        types = json.load(infile)
        infile.close()
    return types

@anvil.server.callable
def saveBrowserTypes(categories):
    with open('browsertypes.json', 'w') as outfile:
        json.dump(categories,outfile)
        outfile.close()


# Makes the timezone naive datetime object timezone aware and pops it forward
# 4 hours so it can be compared to the ActivityWatch dates
# NOTE: the hours incremented here will probably need to change if this is 
# used in a different timezone. I'm in the Eastern time zone
def dateClean(Date):
    Date = Date + datetime.timedelta(hours=4)
    return Date.replace(tzinfo=pytz.UTC)

# initializes categories and types
def fileinit():
    workCat = ['Atom','Terminal','Word','Visual','Workflowy','Notes']
    leisureCat = ['Steam','Civilization','Table','Spotify']
    browsingCat = ['Chrome']
    catdict = {
        'Work' : workCat,
        'Leisure': leisureCat,
        'Browsing' : browsingCat
    }
    saveCategories(catdict)
    windowtypes = {
        "Work": "Productive",
        "Leisure": "Unproductive",
        "Browsing": "Neutral"
    }
    saveTypes(windowtypes)

    reddit = ["reddit"]
    canvas = ['canvas','instructure']
    development = ['anvil','github']
    entertainment = ['youtube','netflix','hulu']
    webdict = {
        'reddit' : reddit,
        'canvas' : canvas,
        'development' : development,
        'entertainment' : entertainment
    }
    saveBrowserCategories(webdict)
    webtypes = {
        "reddit": "Unproductive",
        "canvas": "Productive",
        "development": "Productive",
        "entertainment": "Unproductive"
    }
    saveBrowserTypes(webtypes)

if len(sys.argv) > 1:
    if sys.argv[1] == 'init':
        fileinit()
    else:
        print('invalid command line argument, use "init" to initialize categories')
        print('running without fileinit()')


anvil.server.connect(uplink)

#returns dict of all current buckets' metadata
@anvil.server.callable
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
        bucketdict = json.loads(buckets.content)
        return bucketdict

# find the bucket names for this pc
# run on every startup
buckets = allBuckets()
windowBucket = ''
for name in buckets:
    if re.search('window',name,re.IGNORECASE):
        windowBucket = name
webBucket = ''
for name in buckets:
    if re.search('web',name,re.IGNORECASE):
        webBucket = name

#get bucket metadata
#pass in a string
@anvil.server.callable
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
        bucketdict = json.loads(bucket.content)
        return bucketdict

#get events from a bucket
#pass in a string
#return list of events
@anvil.server.callable
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
        eventdict = json.loads(events.content)
        return eventdict

#returns true if an event is in the specified category
#pass in event (dict), category (List)
#for use on currentwindow bucket
def inCategory(event,category):
    eventname = event['app']
    inCat = False
    for appname in category:
        if re.search(appname,eventname):
            inCat = True
            return inCat
    return inCat

# returns dictionary of categories along with the total duration for that category
@anvil.server.callable
def countCategory(cat_dict, event_list):
    countdict = dict()
    types = getTypes()
    countdict['Uncategorized'] = [0.0,'Neutral']
    for cat in cat_dict:
        countdict[cat] = [0.0,types[cat]]
    for event in event_list:
        categorized = False
        for category in cat_dict:
            if inCategory(event,cat_dict[category]):
                countdict[category][0] += event['duration']
                categorized = True
        if not categorized:
            countdict['Uncategorized'][0] += event['duration']
    return countdict

# wrapper function for countCategory
@anvil.server.callable
def getCounts(catdict,start,end):
    events = getEventsDataWindow(start,end)
    countlist = countCategory(catdict,events)
    return countlist

#returns true if an event is in the specified category
#pass in event (dict), category (List)
#for use on web bucket
def inBrowserCategory(event,category):
    url = event['url']
    title = event['title']
    inCat = False
    for sitename in category:
        if re.search(sitename,url,re.IGNORECASE):
            inCat = True
            return inCat
        if re.search(sitename,title,re.IGNORECASE):
            inCat = True
            return inCat
    return inCat

# takes in dictionary of browser categories = cat_dict
# list of BROWSER events to be categorized = event_list
# string of browser name = browser
# categorizes browser events, and if not categorized, uses default category
@anvil.server.callable
def countBrowserCategory(cat_dict, event_list):
    countdict = dict()
    types = getBrowserTypes()
    countdict['Other browsing'] = [0.0,'Unproductive']
    for cat in cat_dict:
        countdict[cat] = [0.0,types[cat]]
    for event in event_list:
        categorized = False
        for category in cat_dict:
            if inBrowserCategory(event,cat_dict[category]):
                countdict[category][0] += event['duration']
                categorized = True
        if not categorized:
            countdict['Other browsing'][0] += event['duration']
    return countdict

# wrapper for countBrowserCategory
@anvil.server.callable
def getBrowserCounts(catdict,start,end):
    events = getEventsDataWeb(start,end)
    countlist = countBrowserCategory(catdict,events)
    return countlist

# Unused function which gets all windowbucket events regardless of timestamp
@anvil.server.callable
def getEventsData():
    events_list = getBucketEvents(windowBucket)
    data = list()
    categories = getCategories()
    types = getTypes()
    for event in events_list:
        data.append(event['data'])
        data[-1]['timestamp'] = event['timestamp']
        data[-1]['duration'] = float(event['duration'])
        data[-1]['endstamp'] = str(isodate.parse_datetime(data[-1]['timestamp']) + relativedelta(seconds=+data[-1]['duration']))

        categorized = False
        for category in categories:
            if inCategory(event,categories[category]):
                data[-1]['category'] = category
                data[-1]['type'] = types[category]
                categorized = True
            #else:
        if not categorized:
            data[-1]['category'] = 'Uncategorized'
            data[-1]['type'] = 'Neutral'
    data[0]['timestamp']
    return data


# Version of getEventsData which only returns window events between the times specified
# by the start and end datetime objects

# Unwraps the 'data' attribute of ActivityWatch events by placing them in the same
# level as the rest of the dictionary, and adds an endstamp attribute
# returns a list of events
@anvil.server.callable
def getEventsDataWindow(start,end):
    dateClean(start)
    dateClean(end)
    events_list = getBucketEvents(windowBucket)
    data = list()
    categories = getCategories()
    types = getTypes()
    for event in events_list:
        if ((isodate.parse_datetime(event['timestamp']) > start) and (isodate.parse_datetime(event['timestamp']) < end)):
            data.append(event['data'])
            data[-1]['timestamp'] = event['timestamp']
            data[-1]['duration'] = float(event['duration'])
            endstamp = list(str(isodate.parse_datetime(data[-1]['timestamp']) + relativedelta(seconds=+data[-1]['duration'])))
            endstamp[10] = 'T'
            data[-1]['endstamp'] = "".join(endstamp)
            categorized = False

            for category in categories:
                if inCategory(data[-1],categories[category]):
                    data[-1]['category'] = category
                    data[-1]['type'] = types[category]
                    categorized = True
            if not categorized:
                data[-1]['category'] = 'Uncategorized'
                data[-1]['type'] = 'Neutral'
    return data

# Version of getEventsData which only returns web events between the times specified
# by the start and end datetime objects

# Unwraps the 'data' attribute of ActivityWatch events by placing them in the same
# level as the rest of the dictionary, and adds an endstamp attribute
# returns a list of events
@anvil.server.callable
def getEventsDataWeb(start,end):
    dateClean(start)
    dateClean(end)
    events_list = getBucketEvents(webBucket)
    data = list()
    categories = getBrowserCategories()
    types = getBrowserTypes()
    for event in events_list:
        if ((isodate.parse_datetime(event['timestamp']) > start) and (isodate.parse_datetime(event['timestamp']) < end)):
            data.append(event['data'])
            data[-1]['timestamp'] = event['timestamp']
            data[-1]['url'] = event['data']['url']
            data[-1]['title'] = event['data']['title']
            data[-1]['duration'] = float(event['duration'])
            endstamp = list(str(isodate.parse_datetime(data[-1]['timestamp']) + relativedelta(seconds=+data[-1]['duration'])))
            endstamp[10] = 'T'
            data[-1]['endstamp'] = "".join(endstamp)

            categorized = False
            for category in categories:
                if inBrowserCategory(data[-1],categories[category]):
                    data[-1]['category'] = category
                    data[-1]['type'] = types[category]
                    categorized = True
                #else:
            if not categorized:
                data[-1]['category'] = 'Uncategorized'
                data[-1]['type'] = 'Neutral'
    return data

# returns a list of lists containing top app name and its total duration
# top X elements returned is currently hardcoded at 5, could add parameter for this
@anvil.server.callable
def topApps(start,end):
    data = getEventsDataWindow(start,end)
    appBucket = dict()
    durationtotal = 0.0
    for event in data:
        if event['app'] in appBucket:
            appBucket[event['app']] += event['duration']
            durationtotal += event['duration']
        else:
            appBucket[event['app']] = event['duration']
            durationtotal += event['duration']
    appNames = nlargest(5,appBucket, key=appBucket.get)
    topApps = list()
    for app in appNames:
        topApps.append([app,appBucket[app],(appBucket[app]/durationtotal)*100.0])
    return topApps

# web bucket equivalent of above
@anvil.server.callable
def topWebTitles(start,end):
    data = getEventsDataWeb(start,end)
    appBucket = dict()
    durationtotal = 0.0
    for event in data:
        if event['title'] in appBucket:
            appBucket[event['title']] += event['duration']
            durationtotal += event['duration']
        else:
            appBucket[event['title']] = event['duration']
            durationtotal += event['duration']
    appNames = nlargest(5,appBucket, key=appBucket.get)
    topTitles = list()
    for app in appNames:
        topTitles.append([app,appBucket[app],(appBucket[app]/durationtotal)*100.0])
    return topTitles

# Unused test function to see if we're receiving date information correctly
@anvil.server.callable
def printDate(start,end):
    s = dateClean(start)
    e = dateClean(end)
    print(start)
    print(s)
    print(end)
    print(e)

# write Gantt chart pngs to file
def writeTimeline(fig):
    fig.write_image('timeline.png')

def writeWebTimeline(fig):
    fig.write_image('webtimeline.png')

# Creates a plotly gantt chart of what category of apps were used on a timeline
# parameters are start and end datetime objects
@anvil.server.callable
def getAppTimeline(start,end):
    data = getEventsDataWindow(start,end)
    format = list()
    # populate format array for use in gantt
    for i in range(len(data)):
        format.append(dict())
        #Each 'Task' specifies a single row in a Gantt chart. Since we're
        #using it as a horizontal timeline we only need one.
        format[i]['Task'] = 'Apps'
        # 'Start' and 'Finish' of each data point, populating the actual data
        format[i]['Start'] = isodate.parse_datetime(data[i]['timestamp']) - datetime.timedelta(hours=4)
        format[i]['Finish'] = isodate.parse_datetime(data[i]['endstamp']) - datetime.timedelta(hours=4)
        # Categorize and color code each data point by its category in app
        format[i]['Resource'] = data[i]['category']
    fig = ff.create_gantt(format,index_col='Resource',show_colorbar=True,group_tasks=True)
    writeTimeline(fig)

# Creates a plotly gantt chart of what category of websites were used on a timeline
# parameters are start and end datetime objects
@anvil.server.callable
def getWebTimeline(start,end):
    data = getEventsDataWeb(start,end)
    format = list()
    # populate format array for use in gantt
    for i in range(len(data)):
        format.append(dict())
        # Each 'Task' specifies a single row in a Gantt chart. Since we're
        # using it as a horizontal timeline we only need one.
        format[i]['Task'] = 'Web'
        # 'Start' and 'Finish' of each data point, populating the actual data
        format[i]['Start'] = isodate.parse_datetime(data[i]['timestamp']) - datetime.timedelta(hours=4)
        format[i]['Finish'] = isodate.parse_datetime(data[i]['endstamp']) - datetime.timedelta(hours=4)
        # Categorize and color code each data point by its category in app
        format[i]['Resource'] = data[i]['category']
    fig = ff.create_gantt(format,index_col='Resource',show_colorbar=True,group_tasks=True)
    writeWebTimeline(fig)

# Functions return an anvil.media object of the app/web Gantt charts
@anvil.server.callable
def getMedia():
    return anvil.media.from_file(filename='./timeline.png',mime_type='image/png')

@anvil.server.callable
def getWebMedia():
    return anvil.media.from_file(filename='./webtimeline.png',mime_type='image/png')

anvil.server.wait_forever()
