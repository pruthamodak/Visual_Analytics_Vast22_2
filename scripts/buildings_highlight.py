import pandas as pd
from bokeh.layouts import column, row, layout, Spacer
from bokeh.models import ColumnDataSource, HoverTool, TabPanel
from bokeh.models import BoxSelectTool, BoxZoomTool, LassoSelectTool
from bokeh.models.widgets import RadioButtonGroup, Select
from bokeh.plotting import figure
from os import path

from bokeh.palettes import tol

def Build_Loc():
    """ Create a tab to profiles a visitor's activity
    :return: bokeh Panel object 
    """
    appDirpath = path.basename(path.split(path.dirname(__file__))[0])


    def place_plot(place,x,y,color, cdsplace):
        """ Create the figure with map and the visitor's trajectory
        :return: bokeh Figure object 
        """
        
        p = figure(width=400, height=400,  title=place,tools="box_select,box_zoom,lasso_select,reset")

        p.circle(x=x, y=y,color = color, size=5,source=cdsplace)
    
        select_overlay = p.select_one(BoxSelectTool).overlay

        select_overlay.fill_color = "firebrick"
        select_overlay.line_color = None

        zoom_overlay = p.select_one(BoxZoomTool).overlay

        zoom_overlay.line_color = "olive"
        zoom_overlay.line_width = 8
        zoom_overlay.line_dash = "solid"
        zoom_overlay.fill_color = None

        p.select_one(LassoSelectTool).overlay.line_dash = [10, 10]
        p.xaxis.axis_label = x
        p.yaxis.axis_label = y
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
        
        
        
        # TODO
        
        #hover = HoverTool(tooltips=[('name', '@dinoFunName'), ('type', '@type'), ('num_checkins', '@num_checkins')], names=["checkins"])
        #p.add_tools(hover_apt,hover_pubs) 
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
    
    
        
    """
    def update(attr, old, new):
         Update the data after a user interaction
        
        idNew = selectId.value

        locidNew = load_currentlocid(idNew)
        locidCur.data.update(locidNew.data)
    
    
    # Create the user controls and link the interactions         
    selectId = Select(title='ID:', value='0', options=['0', '1','2'])
    selectId.on_change('value', update)
    
    controls = column(selectId, width=200)
    """
    # Create the plot
    buildLoc = load_buildLoc()

    places = ["Apartments", "Employers", "Pubs", "Restaurants", "Schools"]
    
    placeLoc=dict()
    for place in places:
        cds_place = load_place(place)
        placeLoc[place]=cds_place
    
    p = map_plot(buildLoc, placeLoc)
    q1 = place_plot("Apartments","maxOccupancy_Apartments","rentalCost","maroon", placeLoc["Apartments"])
    q2 = place_plot("Pubs","maxOccupancy_Pubs","hourlyCost","magenta", placeLoc["Pubs"])
    q3 = place_plot("Restaurants","maxOccupancy_Restaurants","foodCost","lime", placeLoc["Restaurants"])
    q4 = place_plot("Schools","maxEnrollment","monthlyCost","red", placeLoc["Schools"])

    # Create a layout for the tab and initialize it
    layout_r = row(p,layout([[q1, q2], [q3, q4]]))
    layout_c = column(Spacer(width=25),layout_r)
    
    tab = TabPanel(child=layout_c, title='Overview of Engagement')
    
    return tab
  
