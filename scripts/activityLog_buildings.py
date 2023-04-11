import pandas as pd
from bokeh.layouts import column, row, Spacer
from bokeh.models import ColumnDataSource, HoverTool, TabPanel, DatetimeRangeSlider
from bokeh.models.widgets import Select
from bokeh.plotting import figure
import os
from os import path
from datetime import datetime
import random


def ID_currentLoc(ac_log):
    """ Create a tab to profiles a visitor's activity
    :return: bokeh Panel object 
    """
    appDirpath = path.basename(path.split(path.dirname(__file__))[0])
    

    def acloc_plot(building_type_dict, currentLoc):
        """ Create the figure with map and the visitor's trajectory
        :return: bokeh Figure object 
        """
        plotSize = 800
        p = figure(x_range=(-4760,2650), y_range=(-30,7850), width=plotSize, height=plotSize)
        url = path.join(appDirpath, 'static', 'BaseMap.png')
        p.image_url(url=[url], x=-4760, y=-30,w=7410, h=7880, anchor="bottom_left")

        color1 =['cornflowerblue', 'goldenrod', 'crimson']
        i=0
        print("***************************")
        for building_type, buildingloc_cds in building_type_dict.items():
            p.multi_line(xs='xs', ys='ys', legend_label=building_type, color=color1[i], source=buildingloc_cds)
            i+=1
        
        p.multi_line(xs='xs', ys='ys',color='mediumorchid', line_width=0.05,  source=currentLoc)

        return p

    def map_plot(building_type_dict, placeLoc_dict):
        """ Create the figure with map and the visitor's trajectory
        :return: bokeh Figure object 
        """
        plotSize = 800
        p = figure(x_range=(-4760,2650), y_range=(-30,7850), width=plotSize, height=plotSize)
        url = path.join(appDirpath, 'static', 'BaseMap.png')
        p.image_url(url=[url], x=-4760, y=-30,w=7410, h=7880, anchor="bottom_left")

        color1 =['cornflowerblue', 'goldenrod', 'crimson']
        i=0
        print("***************************")
        for building_type, buildingloc_cds in building_type_dict.items():
            p.multi_line(xs='xs', ys='ys', legend_label=building_type, color=color1[i], source=buildingloc_cds)
            i+=1

        p.circle(x='xs', y='ys', radius=10, color='maroon', fill_alpha=0.5, legend_label="Apartments", source=placeLoc_dict["Apartments"])  
        p.circle(x='xs', y='ys', radius=50, color='magenta', fill_alpha=0.6, legend_label="Pubs", source=placeLoc_dict["Pubs"])
        p.circle(x='xs', y='ys', radius=50, color='lime', fill_alpha=0.6, legend_label="Restaurants", source=placeLoc_dict["Restaurants"])
        p.circle(x='xs', y='ys', radius=10, color='midnightblue', fill_alpha=0.5, legend_label="Employers", source=placeLoc_dict["Employers"]) 
        p.circle(x='xs', y='ys', radius=50, color='red', fill_alpha=0.5, legend_label="Schools",source=placeLoc_dict["Schools"]) 
        
        p.legend.click_policy="hide"

        return p

    def parse_building_loc(loc): # parse single building loc
        
        p_loc = loc.replace("POLYGON ((","").replace("))","")
        polys = p_loc.split("), (")
        xs = list()
        ys = list()
        for poly in polys:
            pts = poly.split(",")    
            for pt in pts:
                p1=pt.split()
                x0=float(p1[0].strip()) 
                y0=float(p1[1].strip())
                xs.append(x0)
                ys.append(y0)
        
        return xs,ys

    def parse_point(loc): # parse single loc
        
        p1 = loc.split()
        x0 = float(p1[1].replace("(", ""))
        y0 = float(p1[2].replace(")", ""))
        
        return x0,y0
        
        
    def load_buildLoc():
        buildings_df = pd.read_csv(appDirpath+"/data/Attributes/Buildings.csv")
        building_type_df = buildings_df.groupby("buildingType")
        building_type_dict =dict()
        
        for buildings_df in building_type_df:
            xs = list()
            ys = list()
            buildingloc_ls =list(buildings_df[1].apply(lambda x: parse_building_loc(x['location']), axis=1))
            for buildLoc in buildingloc_ls:
                xs.append(buildLoc[0])
                ys.append(buildLoc[1])
            building_type_dict[buildings_df[0]]=ColumnDataSource(dict(xs=xs,ys=ys))
            
        return building_type_dict

    def load_place(place):
        xs = list()
        ys = list()
        place_df = pd.read_csv(appDirpath+"/data/Attributes/"+place+".csv")
        placeloc_ls = list(place_df.apply(lambda x: parse_point(x['location']), axis=1))
        for placeLoc in placeloc_ls:
            xs.append(placeLoc[0])
            ys.append(placeLoc[1])
        place_df['xs'] = xs
        place_df['ys'] = ys
        place_df = place_df.drop(columns=['location'])
        if place=="Apartments" or place=="Pubs" or place=="Restaurants":
            place_df['maxOccupancy_'+place] = place_df['maxOccupancy']
            place_df = place_df.drop(columns=['maxOccupancy'])
        return ColumnDataSource(place_df)
        
    def load_currentlocid(ac_log):
        #ac_log = pd.read_csv(appDirpath+"/data/ActivityLogs/ParticipantStatusLogs1.csv")
        id_arr = ac_log.participantId.unique()
        #id_ar = random.sample([i for i in range(len(id_arr))], 100)
        id_ar = [i for i in range(100)]
        xs = list()
        ys = list()
        for id in id_ar:
            ac_log_df = ac_log.loc[ac_log['participantId'] == id].sort_values(by='timestamp', ascending=True)
            geo_loc_id = ac_log_df["currentLocation"]
            #currloc = list()
            x_id = list()
            y_id = list()
            for loc in geo_loc_id:
                p1 = loc.split()
                x0 = float(p1[1].replace("(", ""))
                y0 = float(p1[2].replace(")", ""))
                #currloc.append((x0,y0))
                x_id.append(x0)
                y_id.append(y0)
            xs.append(x_id)
            ys.append(y_id)
            #df = pd.DataFrame(currloc,columns=["x","y"])

        #ac_log_df['timestamp'] = ac_log_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        return ColumnDataSource(dict(xs=xs,ys=ys))
    
    
    def updatesid(attr, old, new):
        """ Update the data after a user interaction
        """
        print("In updatesid")
        sidNew = selectId.value
        ac_log, start_ts, end_ts = get_aclog_tsarraydt(sidNew)
        # print(ac_log['timestamp'])
        locidNew = load_currentlocid(ac_log)
        locidCur.data.update(locidNew.data)
        ts_slider.value=(start_ts, end_ts)
        ts_slider.start=start_ts
        ts_slider.end=end_ts
        
    def updatets(attr, old, new):
        """ Update the data after a user interaction
        """
        print("In updatets")
        tsrangeNew = ts_slider.value_as_datetime
        ac_log, start_ts, end_ts = get_aclog_tsarraydt(selectId.value, tsrangeNew[0], tsrangeNew[1])
        # print(ac_log['timestamp'])
        locidNew = load_currentlocid(ac_log)
        locidCur.data.update(locidNew.data)


    def update(attr, old, new):
        pass  


    def get_aclog_tsarraydt(selectId, start_ts=None, end_ts=None):
        ac_log = pd.read_csv(os.path.join(appDirpath, "data/ActivityLogs", "ParticipantStatusLogs"+selectId+".csv"))
        ts_array = ac_log.loc[ac_log['participantId'] == 0].sort_values(by='timestamp', ascending=True).timestamp.unique()

        if start_ts==None and end_ts==None:
            start_ts = datetime.strptime(ts_array[0], '%Y-%m-%dT%H:%M:%SZ')
            end_ts = datetime.strptime(ts_array[-1], '%Y-%m-%dT%H:%M:%SZ')
        
        ac_log['timestamp']=pd.to_datetime(ac_log['timestamp'], format='%Y-%m-%dT%H:%M:%SZ')
        ac_log = ac_log[(ac_log['timestamp'] >= start_ts) & (ac_log['timestamp'] < end_ts)]

        return ac_log, start_ts, end_ts

    sid_options = [str(i) for i in range(1,73)]
    selectId = Select(title='Activity Log:', value='1', options=sid_options, width=100)
    selectId.on_change('value', updatesid)

    ac_log, start_ts, end_ts = get_aclog_tsarraydt(selectId.value)
    
    ts_slider = DatetimeRangeSlider(value=(start_ts, end_ts),start=start_ts, end=end_ts, title="Timestamp", width=600)
    ts_slider.on_change('value',updatets)
    
    controls = row(Spacer(width=25), selectId, Spacer(width=25), ts_slider)
   
    # Create the plot
    locidCur = load_currentlocid(ac_log)
    
    

    # Create the plot
    buildLoc = load_buildLoc()
    places = ["Apartments", "Employers", "Pubs", "Restaurants", "Schools"]
    placeLoc=dict()
    for place in places:
        cds_place = load_place(place)
        placeLoc[place]=cds_place
    p = map_plot(buildLoc, placeLoc)

    q = acloc_plot(buildLoc,locidCur)
    
    
    # Create a layout for the tab and initialize it
    layout = column(controls, row(p, q))
    tab = TabPanel(child=layout, title='Movement Trajectory')
    
    return tab
  
