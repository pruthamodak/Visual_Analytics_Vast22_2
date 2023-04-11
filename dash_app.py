import dash
from dash import Dash, html, dcc, Input, Output
from scripts.daily_routine import DailyRoutine

app = Dash('Work and Joviality')
age_group = [True, True, True]
selected_ids = None

daily_routine_handler = DailyRoutine()

@app.callback(
    Output('scatter_work', 'figure'),
    Output('radial_selected', 'figure'),
    Input('scatter_work', 'selectedData'),
    Input('age_bar', 'restyleData'),
    )
def update_histogram(selectedData, restyleData):
    global selected_ids, age_group
    if selectedData and selectedData['points']:
        selected_ids = [x['customdata'][0] for x in selectedData['points']]
        return dash.no_update, daily_routine_handler.call_radial_selected(selectedIds=selected_ids)
    elif restyleData and len(restyleData[1]) > 1:
        return daily_routine_handler.call_work_scatter(ag_selected = restyleData[0]['visible']), daily_routine_handler.call_radial_selected(ag_selected=restyleData[0]['visible'])
    elif restyleData:
        age_group[restyleData[1][0]] = restyleData[0]['visible'][0]

    if not selectedData and selected_ids:
        selected_ids = None
        return dash.no_update, daily_routine_handler.call_radial_selected(selectedIds=selected_ids)
    elif not selectedData and not restyleData:
        return dash.no_update, dash.no_update
    return daily_routine_handler.call_work_scatter(ag_selected = age_group), daily_routine_handler.call_radial_selected(selectedIds=selected_ids, ag_selected=age_group)


app.layout = html.Div(children=[
    html.H1(
        id="main_header",
        children=[
            "Work and Joviality pattern by age"],
        className="app-header",
    ),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
            id='scatter_work',
            figure=daily_routine_handler.call_work_scatter()
            ),
            html.Div(children="Fig1: Scatter plot of hours spent at work place wrt Joviality, color coded by age and clusters indicate 5 Work groups.",
                    className="graph-title")
            ], className="graph-wrapper"),

        html.Div(children=[
            dcc.Graph(
            id='radial_selected',
            figure=daily_routine_handler.call_radial_selected()
            ),
            html.Div(children="Fig2: Radial plot for total time spent in different venue types with times indicating max, min and avg values",
                    className="graph-title")
            ], className="graph-wrapper"),
        
    ], style={
        'display': 'flex',
    }),
    html.Div(children=[
        dcc.Graph(
        id='age_bar',
        figure=daily_routine_handler.call_age_bar(),
        className="age-bar-graph"
        ),
        html.Div(children="Fig3: Bar graph for the 5 different clusters found in Fig1 stacked by the count of each age group and color coded for the same",
                className="graph-title")
        ], className="graph-wrapper"),
    
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
