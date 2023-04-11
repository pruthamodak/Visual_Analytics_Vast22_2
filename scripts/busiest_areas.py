import csv
from datetime import datetime, timedelta
from os import path
import pandas as pd
import glob
import os
from bokeh.plotting import figure, show
from bokeh.models import Text, Button, Div, HoverTool, TextInput, CustomJS, TabPanel
from bokeh.io import show, output_file, curdoc
from bokeh.layouts import gridplot
from bokeh.models.widgets import Select, RadioGroup
from bokeh.layouts import column
from bokeh.embed import components
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from IPython.display import display
from math import pi

from scripts.busiest_areas_generate_visual import generateVisualisation


def buildDailyPatternActivities():
    appDirpath = path.basename(path.split(path.dirname(__file__))[0])
    # Build a processed dataset
    processedDataSet = buildDataSet(appDirpath)
    layout = generateVisualisation(processedDataSet)
    tab = TabPanel(child=layout, title='High Density Activity')
    return tab


def buildDataSet(appDirpath):
    # Set districtConfig area based on location
    districtConfig = [
        { 'districtName': 'NorthWest', 'greaterThanLocations': 0, 'lessThanLocation': 250 },
        { 'districtName': 'NorthEast', 'greaterThanLocations': 250, 'lessThanLocation': 500 },
        { 'districtName': 'SouthWest', 'greaterThanLocations': 500, 'lessThanLocation': 750 },
        { 'districtName': 'SouthEast', 'greaterThanLocations': 750, 'lessThanLocation': 1000 }
    ]

    # create url to location of raw dataset
    url = path.join(appDirpath, 'data', 'Journals', 'TravelJournal.csv')

    # open the input raw dataset file, process existing data and add metadata siuch as 'district' to all records
    with open(url, 'r') as infile, open('dailyPatternActivitiesDataset.csv', 'w') as outfile:
        # create a CSV reader and writer
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # iterate over the rows of the input file
        for i, row in enumerate(reader):
            # skip the header row
            if i == 0:
                writer.writerow(row + ['purposeDuration', 'dayOfWeek', 'district'])
                continue

            # parse the timestamp strings into datetime objects
            ts1 = datetime.strptime(row[6], '%Y-%m-%dT%H:%M:%SZ') #checkInTime field
            ts2 = datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%SZ') #checkOutTime field

            # compute the time difference
            time_difference = (ts2 - ts1)/60

            # convert the time difference to seconds
            time_difference_seconds = time_difference.total_seconds()

            # Find the day of the week the participant has recorded the activity for
            dayOfWeek = ts1.weekday()

            # Set district value based on districtConfig list
            endLocationId = int(row[4])
            district = 'None'
            if endLocationId >= 0 and endLocationId <= 500:
                district = 'NorthWest'
            elif endLocationId > 500 and endLocationId <= 1000:
                district = 'NorthEast'
            elif endLocationId > 1000 and endLocationId <= 1500:
                district = 'SouthWest'
            elif endLocationId > 1500 and endLocationId <= 2000:
                district = 'SouthEast'

            # write the row with the time difference to the output file
            writer.writerow(row + [time_difference_seconds, dayOfWeek, district])

    Csvdata = pd.read_csv('dailyPatternActivitiesDataset.csv',
                  header=0, 
                  usecols=['participantId', 'district', 'purpose', 'purposeDuration', 'dayOfWeek'])
    
    # Find mean of dataSet by grouping relevant columns
    meanDataSet = (Csvdata.groupby(['participantId', 'purpose', 'dayOfWeek', 'district'])).mean()
    meanDataSet = meanDataSet.reset_index()

    return meanDataSet
