from ._anvil_designer import TimelineTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import datetime
import anvil.media
import plotly.graph_objects as go

def getAppTimeline(start,end):
  return anvil.server.call('getAppTimeline',start,end)  

def getWebTimeline(start,end):
  return anvil.server.call('getWebTimeline',start,end)

class Timeline(TimelineTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #now = datetime.datetime.now()
    #now - datetime.timedelta(hours=1),now
    self.image_1.width = 700 + 175
    self.image_1.height = 600 + 150
    self.image_2.width = 700 + 175
    self.image_2.height = 600 + 150
    self.end_date.pick_time = True
    self.start_date.pick_time = True
    self.start_date.enabled = False
    self.end_date.enabled = False
    now = datetime.datetime.now()
    self.end_date.date = now
    self.start_date.date = now - datetime.timedelta(hours=1)
    self.initData()

    
    ##FIXME look at the LAST bookmarked page on google drive uploads
    
    # Any code you write here will run when the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.start_date.date < self.end_date.date:
      self.initData()

  def time_select_dropdown_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    options = ['Last Hour','2h','4h','8h','1d','1w','All time','Manual Select']
    self.time_select_dropdown.items = options

  def initData(self):
    start = self.start_date.date
    end = self.end_date.date
    getAppTimeline(start,end)
    getWebTimeline(start,end)
    self.image_1.source = anvil.server.call('getMedia')
    self.image_2.source = anvil.server.call('getWebMedia')
    
  #FIXME add code to do show timeline
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






