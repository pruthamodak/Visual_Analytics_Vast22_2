import csv
from datetime import datetime, timedelta
from os import path
import pandas as pd
import glob
import os
from bokeh.plotting import figure, show
from bokeh.models import Text, Button, Div, HoverTool, TextInput, CustomJS, TabPanel, ColumnDataSource, LayoutDOM
from bokeh.io import show, output_file, curdoc
from bokeh.layouts import gridplot
from bokeh.models.widgets import Select, RadioGroup
from bokeh.layouts import row, column
from bokeh.embed import components
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from IPython.display import display
from math import pi
from PIL import Image
import numpy as np


# ----------------------------------------Start - Config section--------------------------------------------------------------
# Control the colors for the indicators on the calendar for each purpose
purposeColorIndicators = {
    'Going Back to Home': 'red',
    'Coming Back From Restaurant': 'blue',
    'Eating': 'orange', 
    'Work/Home Commute': 'green',
    'Recreation (Social Gathering)': 'purple'
}

days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
# ----------------------------------------End - Config section----------------------------------------------------------------


def generateVisualisation(dataSet):
        #
        # Visualisation Description: Aims to answer, what makes the area so busy? 
        # What activities/puropse does the participant perform in the week adding to the overall traffic in the area? - Answering this could help solve traffic issues based on frequency of use(More restaurants, office space, schools needed in his area of residence)
        # For aggregate data, we can see the most popular activities in each area, helps answering, if any additional support is requierd to reduce traffic on particular days. (E.g: Weekends do restaurants need additional parking space, can they use unused facitiles/resources?)
        #

        texts = [Text(text=day) for day in days]
        calendarVisuals = [None] * 7
        #grid = gridplot([divs], width=250, height=250)
        grid = gridplot([calendarVisuals], width=230, height=230)

        # Radiobutton group to control view of aggregate or individual participant data
        dataView_options = ["Aggregate Data", "Individual Participant Data"]
        dataView_radioGroup = RadioGroup(labels=dataView_options, active=0, sizing_mode='stretch_width')
        dataView_radioGroupDiv = column(Div(text="Choose Data View Mode:"), dataView_radioGroup)
        # Disable particpiant id selection, when "Aggregate Data" is selected to avoid user confusion
        def dataViewOption_Changed(attrname, oldDataView_radioGroup_active, newDataView_radioGroup_active):
            if newDataView_radioGroup_active == 0:
                participant1SelectInput.disabled = True
                participant2SelectInput.disabled = True
            else:
                participant1SelectInput.disabled = False
                participant2SelectInput.disabled = False
        dataView_radioGroup.on_change("active", dataViewOption_Changed)

        # Create dropdown where the participant details to view is selected from
        # Get all unqiue values for 'participantId' column
        participantList = list(map(str, set(dataSet['participantId'].values.tolist()))) 
        # We compare 2 particpants in the 'Individual Participant Data' view
        participant1SelectInput = Select(title="Select 1st Participant Id:", value=participantList[0], options=participantList, sizing_mode='stretch_width')
        participant2SelectInput = Select(title="Select 2nd Participant Id:", value=participantList[1], options=participantList, sizing_mode='stretch_width')
        # Set particpiant id selection as disabled initially as the dataView option is set to 'Aggregate Data'
        participant1SelectInput.disabled = True
        participant2SelectInput.disabled = True


        # Create dropdown where the desired district to view activity is selected from
        districtList = list(map(str, set(dataSet['district'].values.tolist()))) # Get all unqiue values for 'district' column 
        districtSelectInput = Select(title="""Select District:""", value=districtList[0], options=districtList, sizing_mode='stretch_width')


        # Button to trigger reload of data
        loadDataButton = Button(label='Update Visualisation/Data', button_type="primary", sizing_mode='stretch_width')
        def onLoadDataButtonClick():
            participant1Id = None if dataView_radioGroup.active == 0 else participant1SelectInput.value
            participant2Id = None if dataView_radioGroup.active == 0 else participant2SelectInput.value
            updateVisualisation(dataSet, participant1Id, participant2Id, districtSelectInput.value)
        loadDataButton.on_click(onLoadDataButtonClick)


        # Legend section
        legendDiv_text = '<div style="display: flex; flex-direction: row; align-items: center; font-size: 14px; color: #444;">'
        for key, value in purposeColorIndicators.items():
            legendDiv_text += '<span style="display: inline-block; width: 12px; height: 12px; margin: 6px; border-radius: 50%; background-color:' + value + ';"></span>' + key
        legendDiv_text += '</div>'
        legendDiv = Div(text=legendDiv_text)


        # Import static image to display regional division of the map        
        appDirpath = path.basename(path.split(path.dirname(__file__))[0])
        regionMapUrl = path.join(appDirpath, 'static', 'RegionalDivisionMap.png')
        img_html = '<img src="' + regionMapUrl + '" alt="Base map division by regions" width="250">'
        regionMapImage = Div(text=img_html, sizing_mode='stretch_width')

        
        # Text describing the visualisation
        desciptionText = Div(text="""<b style='font-size: 18px;'>This visualisation, helps view the busiest areas in the city of 'Engagement', by viewing against most time consuming participant purpose.</b>""")


        # Arrange visulisation
        layout_row1 = row(dataView_radioGroupDiv, participant1SelectInput, participant2SelectInput, districtSelectInput, regionMapImage, sizing_mode='stretch_width')
        solutionLayout = column(children = [], sizing_mode = 'stretch_width')


        def loadVisualisationData(visualisationData, participant1Id, participant2Id, districtId):
            visualLayout = []
            if (participant1Id == participant2Id and participant1Id != None):
                # return with div saying both values are equal
                visualLayout = [Div(text="""<h1>Both Participant Values selected are equal or empty!</h1>""")]
            elif(participant1Id == participant2Id and participant1Id == None):
                # For 'Aggregate Data' view
                visualText = Div(text="""<b style='font-size: 14px;'>Aggregate Data View</b>""")
                visualLayout = [visualText, generateVisualisation(visualisationData, None, districtId)]
            else:
                # For 'Individual Participant Data' view
                participant1CalendarVisual = generateVisualisation(visualisationData, participant1Id, districtId)
                participant2CalendarVisual = generateVisualisation(visualisationData, participant2Id, districtId)
                visualText1 = Div(text="""<b style='font-size: 14px;'>Data View for Particpant: {}</b>""".format(participant1Id))
                visualText2 = Div(text="""<b style='font-size: 14px;'>Data View for Particpant: {}</b>""".format(participant2Id))
                visualLayout = [visualText1, participant1CalendarVisual, visualText2, participant2CalendarVisual]

            solutionLayout.children=[column(desciptionText,layout_row1,loadDataButton,legendDiv,*visualLayout)]
            return solutionLayout

        def generateVisualisation(visualisationData, participantId, districtId):
            if participantId is None: #If true, show aggregate data of all participants
                # generate aggregate data for all users
                visualisationData = (visualisationData.groupby(['purpose', 'dayOfWeek', 'district'])).mean() 
                visualisationData = visualisationData.reset_index()
            else: # Else, show data specific to selected participantId
                visualisationData = visualisationData[visualisationData['participantId'] == int(participantId)]

            # Filter data by selected district
            visualisationData = visualisationData[(visualisationData.district == districtId)]

            if len(visualisationData) == 0:
                print('No data')
                div = Div(text="""<h1>No Data!</h1>""")
                return div
                #solutionLayout.children=[layout_row1,loadDataButton,div]
                #return solutionLayout
            else:
                for dayIndex, day in enumerate(days):
                    dayFilteredData = visualisationData[visualisationData.dayOfWeek == dayIndex]
                    chartData = dict(zip(dayFilteredData.purpose, dayFilteredData.purposeDuration))
                    calendarVisuals[dayIndex] = generateCalendarVisualisation(chartData, day)

            grid = gridplot([calendarVisuals], width=220, height=220)
            return grid
            #solutionLayout.children=[column(layout_row1,loadDataButton,legendDiv,grid)]
            #return solutionLayout


        def generateCalendarVisualisation(visualisationData, day):
            data = pd.Series(visualisationData).reset_index(name='value').rename(columns={'index': 'purpose'})
            data['angle'] = data['value']/data['value'].sum()*2*pi            
            data['color'] = data['purpose'].map(purposeColorIndicators).fillna('white')

            p = figure(height=150, width=150, title=day, toolbar_location=None,
                   tools="hover", tooltips="@purpose: @value", x_range=(-0.6, 0.6), align='center')

            if len(data) > 1:
                p.wedge(x=0, y=1, radius=0.4,
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', source=data)
            else:
                p.wedge(x=0, y=1, radius=0.4,
                    start_angle=0, end_angle=2*pi,
                    line_color="white", fill_color='color', source=data)

            p.axis.axis_label = None
            p.axis.visible = False
            p.grid.grid_line_color = None
            return p


        def updateVisualisation(visualisationData, participant1Id, participant2Id, districtId):
            solutionLayout = loadVisualisationData(visualisationData, participant1Id, participant2Id, districtId)
            curdoc().add_next_tick_callback(lambda: solutionLayout.update())


        return loadVisualisationData(dataSet, None, None, districtSelectInput.value)