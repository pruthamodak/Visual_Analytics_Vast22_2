def create_daily_routine_tab():
    from bokeh.models import Div, TabPanel

    div = Div(text="""Link: <a href="http://127.0.0.1:8051/" target="_blank">Dash</a>
    <br/><br/>
    <iframe src="http://127.0.0.1:8051/" style="width: 1500px; height: 800px;" ></iframe>""",
    width=200, height=100)
    daily_pattern_tab = TabPanel(child=div, title="Work and Joviality")
    return daily_pattern_tab