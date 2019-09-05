# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


# Each tab is drawn by one script
from scripts.histogram import histogram_tab

# Read data into dataframes
car = pd.read_csv(join(dirname(__file__), 'data', 'car_accident_final.csv'), 
	                                          index_col=0)

# Create each of the tabs
tab1 = histogram_tab(car)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1])

# Put the tabs in the current document for display
curdoc().add_root(tabs)


