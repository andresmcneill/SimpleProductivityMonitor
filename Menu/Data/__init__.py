from ._anvil_designer import DataTemplate
from anvil import *
import anvil.server
import datetime

class Data(DataTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.type_drop.items = ['Application','Browsing']
    self.end_date.pick_time = True
    self.start_date.pick_time = True
    self.start_date.enabled = False
    self.end_date.enabled = False
    now = datetime.datetime.now()
    self.start_date.date = now - datetime.timedelta(hours=1)
    self.end_date.date = now
    self.initData()
    # Any code you write here will run when the form opens.
    
    
  def initData(self):
    now = datetime.datetime.now()
    start = self.start_date.date
    end = self.end_date.date
    data = list()
    if self.type_drop.selected_value == 'Application':
      events = anvil.server.call('getEventsDataWindow',start,end)
      for event in events:
        data.append([event['app'],
                     event['title'],
                     event['duration']])
      self.data_panel.items = data
    elif self.type_drop.selected_value == 'Browsing':
      events = anvil.server.call('getEventsDataWeb',start,end)
      for event in events:
        data.append([event['title'],
                     event['url'],
                     event['duration']])
      self.data_panel.items = data
    else:
      print('oh bother')

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
    else:
      print("Oh no, something terrible has happened")
 
    self.initData()

  def type_drop_change(self, **event_args):
    """This method is called when an item is selected"""
    self.initData()

  def time_select_dropdown_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    options = ['Last Hour','2h','4h','8h','1d','1w','All time']
    self.time_select_dropdown.items = options


