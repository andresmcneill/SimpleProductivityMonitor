from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
from .Category import Category
from .BrowserCategory import BrowserCategory

def getCategories():
  return anvil.server.call('getCategories')

def saveCategories(categories):
  anvil.server.call('saveCategories',categories)
  
def getTypes():
  return anvil.server.call('getTypes')
  
def saveTypes(types):
  anvil.server.call('saveTypes',types)
  
def getBrowserCategory():
  return anvil.server.call('getBrowserCategory')
  
class Settings(SettingsTemplate):
  def displayCategories(self):
    categories = getCategories()
    types = getTypes()
    browsercat = anvil.server.call('getBrowserCategories')
    browsertyp = anvil.server.call('getBrowserTypes')
    for category in categories:
      newcat = Category()
      newcat.cat_name.text = category
      newcat.cat_list.text = "|".join(categories[category])
      newcat.prod_select.selected_value = types[category]
      self.category_panel.add_component(newcat)
    for category in browsercat:
      newbrows = BrowserCategory()
      newbrows.cat_name.text = category
      newbrows.cat_list.text = "|".join(browsercat[category])
      newbrows.prod_select.selected_value = browsertyp[category]
      self.subcategory_panel.add_component(newbrows)
    
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.displayCategories()
    # Any code you write here will run when the form opens.

  def add_category_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.category_panel.add_component(Category())

  def save_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    components = self.category_panel.get_components()
    categories = dict()
    types = dict()
    for c in components:
      if isinstance(c,Category):
        newlist = c.cat_list.text.split()
        categories[c.cat_name.text] = newlist
        types[c.cat_name.text] = c.prod_select.selected_value
    saveCategories(categories)
    saveTypes(types)

  def save_subcat_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    components = self.subcategory_panel.get_components()
    categories = dict()
    types = dict()
    for c in components:
      if isinstance(c,BrowserCategory):
        newlist = c.cat_list.text.split()
        categories[c.cat_name.text] = newlist
        types[c.cat_name.text] = c.prod_select.selected_value
    anvil.server.call('saveBrowserCategories',categories)
    anvil.server.call('saveBrowserTypes',types)

  def add_subcat_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.subcategory_panel.add_component(BrowserCategory())



  
