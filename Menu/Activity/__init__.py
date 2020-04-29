from ._anvil_designer import ActivityTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import datetime
import math


def getEventsDataWindow(start,end):
  anvil.server.call('getEventsDataWindow',start,end)

# returns dict of {category:productivitytype}
def getTypes():
  return anvil.server.call('getTypes')

def getAppTimeline(start,end):
  anvil.server.call('getAppTimeline',start,end)

# returns dict of {appcategory:[list|items]}
def getCategories():
  return anvil.server.call('getCategories')

# returns dict of {webcategory:[list|items]}
def getEventsData():
  return anvil.server.call('getEventsData')

# returns top 5 used app names and their percent usage
def topApps(start,end):
  return anvil.server.call('topApps',start,end)

# returns top 5 used website titles and their percent usage
def topWebTitles(start,end):
  return anvil.server.call('topWebTitles',start,end)

# Returns the sum of the counts of unproductive categories in a list
# of values returned from getCounts or getBrowserCounts
def getUnproductivity(counts):
  prodsum = 0.0
  for cat in counts:
    if (counts[cat][1] == 'Unproductive'):
      prodsum += counts[cat][0]
  return prodsum

class Activity(ActivityTemplate):
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.end_date.pick_time = True
    self.start_date.pick_time = True
    self.start_date.enabled = False
    self.end_date.enabled = False
    now = datetime.datetime.now()
    self.top_app_lbl.width = '200'
    self.prod_label.font_size = 24
    self.prod_label.underline = True
    self.top_apps_repeating.width = '200'
    self.end_date.date = now
    self.start_date.date = now - datetime.timedelta(hours=1)
    start = self.start_date.date
    end = self.end_date.date
    #update pie chart function
    self.initData()

  # sets all components showing data
  # assumes that start_date and end_date have been assigned valid
  # input
  def initData(self):
    start = self.start_date.date
    end = self.end_date.date
    categories = anvil.server.call('getCategories')
    counts = anvil.server.call('getCounts',categories,start,end)
    applabels = counts.keys()
    types = getTypes()
    vals = list()
    appvals = list()
    webvals = list()
    browsercats = anvil.server.call('getBrowserCategories')
    browscounts = anvil.server.call('getBrowserCounts',browsercats,start,end)
    browslabels = browscounts.keys()
    for c in counts:
      appvals.append(counts[c][0])
    del counts['Browsing']
    total = 0.0
    for c in counts:
      vals.append(counts[c][0])
      total += counts[c][0]
    for c in browscounts:
      vals.append(browscounts[c][0])
      webvals.append(browscounts[c][0])
      total += browscounts[c][0]
    
    prodsum = getUnproductivity(counts)
    prodsum += getUnproductivity(browscounts)
    allcounts = counts.update(browscounts)
    labels = counts.keys() + browscounts.keys()
    unprodPercent = (prodsum/total) * 100
    prodstring = "You are {:.2f}% unproductive".format(round(unprodPercent,2))
    self.prod_label.text = prodstring
    self.category_pie.data = go.Pie(labels=labels,values=vals)
    self.app_pie.data = go.Pie(labels=applabels,values=appvals)
    self.web_pie.data = go.Pie(labels=browslabels,values=webvals)
    self.top_apps_repeating.items = topApps(start,end)
    self.top_web_repeating.items = topWebTitles(start,end)

  

  def time_select_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    select = self.time_select_dropdown.selected_value
    now = datetime.datetime.now()
    self.end_date.date = now
    if select != 'Manual':
      self.start_date.enabled = False
      self.end_date.enabled = False
    
    if select == 'Last Hour':
      self.start_date.date = now - datetime.timedelta(hours=1)
    elif select == '2h':
      self.start_date.date = now - datetime.timedelta(hours=2)
    elif select == '4h':
      self.start_date.date = now - datetime.timedelta(hours=4)
    elif select == '8h':
      self.start_date.date = now - datetime.timedelta(hours=8)
    elif select == '1d':
      self.start_date.date = now - datetime.timedelta(days=1)
    elif select == '1w':
      self.start_date.date = now - datetime.timedelta(weeks=1)
    elif select == 'All time':
      self.start_date.date = now - datetime.timedelta(weeks=1000)
    elif select == 'Manual Select':
      self.start_date.enabled = True
      self.end_date.enabled = True
    else:
      print("Oh no, something terrible has happened")
    
  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.start_date.date < self.end_date.date:
      self.initData()

  def time_select_dropdown_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    options = ['Last Hour','2h','4h','8h','1d','1w','All time','Manual Select']
    self.time_select_dropdown.items = options





