from ._anvil_designer import EventTemplate
from anvil import *
import anvil.server

class Event(EventTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    if len(self.item[0]) > 30:
      self.label_1.text = self.item[0][0:30]
    else:
      self.label_1.text = self.item[0][0:len(self.item[0])]
    if len(self.item[1]) > 40:
      self.label_2.text = self.item[1][0:40]
    else:
      self.label_2.text = self.item[1][0:len(self.item[1])]
    self.label_3.text = str(self.item[2])
    # Any code you write here will run when the form opens.