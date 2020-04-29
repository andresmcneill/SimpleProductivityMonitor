from ._anvil_designer import CategoryTemplate
from anvil import *
import anvil.server

class Category(CategoryTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def delete_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.remove_from_parent()






  



  
