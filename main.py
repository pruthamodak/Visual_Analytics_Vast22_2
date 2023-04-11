# Bokeh basics
from bokeh.io import curdoc
from bokeh.models import Tabs

# Load city overview and movement trajectory
from scripts.activityLog_buildings import ID_currentLoc
from scripts.buildings_highlight import Build_Loc

# Load Busiest Purpose Patterns By Region
from scripts.busiest_areas import buildDailyPatternActivities
from scripts.daily_routine_wrapper import create_daily_routine_tab

# Create each of the tabs
tab1 = Build_Loc()
tab2 = ID_currentLoc(ac_log=None)
tab3 = buildDailyPatternActivities()
tab4 = create_daily_routine_tab()

# Put all the tabs into one application
tabs = Tabs(tabs=[tab1, tab2, tab3, tab4])
# tabs = Tabs(tabs=[tab1])

# Put the tabs in the current document for display
c = curdoc().add_root(tabs)