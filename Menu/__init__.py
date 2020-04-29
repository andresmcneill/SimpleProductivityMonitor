from ._anvil_designer import MenuTemplate
from anvil import *
import anvil.server
from .Activity import Activity
from .Timeline import Timeline
from .Settings import Settings
from .Data import Data
import plotly
from plotly import graph_objects as go
import datetime

### Class holds title bar, sidebar, and controls page switches

class Menu(MenuTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_pane.add_component(Activity())
    #anvil.server.call('funct')

    # Any code you write here will run when the form opens.

  def activity_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_pane.clear()
    self.content_pane.add_component(Activity())
    self.page_title.text = 'Activity Summary'

  def timeline_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_pane.clear()
    self.content_pane.add_component(Timeline())
    self.page_title.text = 'Timeline'


  def settings_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_pane.clear()
    self.content_pane.add_component(Settings())
    self.page_title.text = 'Settings'

  def data_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_pane.clear()
    self.content_pane.add_component(Data())
    self.page_title.text = 'Data'
    






