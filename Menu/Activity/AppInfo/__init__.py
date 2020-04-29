from ._anvil_designer import AppInfoTemplate
from anvil import *
import anvil.server
import math

class AppInfo(AppInfoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if len(self.item[0]) > 30:
      self.app_name.text = self.item[0][0:30]
    else:
      self.app_name.text = self.item[0]
    self.app_name.font_size = 20
    ## FIXME this displays the current count, not percentage
    self.app_percentage.text = "{:.2f}".format(round(self.item[2],2)) + "%"
    self.app_percentage.font_size = 15