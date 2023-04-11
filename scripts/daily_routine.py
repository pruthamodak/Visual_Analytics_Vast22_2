from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from os import path
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning, )
pd.options.mode.chained_assignment = None

class DailyRoutine:

    def __init__(self):
        self.data_path = os.path.join(path.basename(path.split(path.dirname(__file__))[0]), "data")
        self.data_path = "./data"
        self.participants_info_checkin_df = pd.read_csv(self.data_path+'/participants_info_checkin_df.csv')
        self.working_df = self.participants_info_checkin_df[self.participants_info_checkin_df['venueType']=='Workplace']
        self.age_group = [18, 25, 45, 60]
        self.age={0:'18-25', 1:'26-45', 2:'46-60'}
        self.work={0:'<500 hrs', 1:'500-2500 hrs', 2:'2500-2750 hrs', 3: '2750-3000 hrs', 4:'>3000 hrs'}
        self.work_group = []
        for index, hrs in enumerate(self.working_df['timeSpentInVenue']):
            if hrs <= 500:
                self.work_group.append(0)
            elif hrs <= 2500:
                self.work_group.append(1)
            elif hrs <= 2750:
                self.work_group.append(2)
            elif hrs <= 3000:
                self.work_group.append(3)
            else:
                self.work_group.append(4)
    
    def preprocess_data(self):
        
        checkin = pd.read_csv(self.data_path+'/journals/CheckinJournal.csv')
        participants = pd.read_csv(self.data_path+'/attributes/Participants.csv')
        participants_checkin = pd.merge(participants, checkin, on="participantId")

        # Preprocessing
        # Adding Time Spent

        time_spent = []
        for index, row in enumerate(checkin['timestamp'][:-1]):
            format = '%Y-%m-%dT%H:%M:%SZ'
            # In minutes
            diff = int((datetime.strptime(checkin['timestamp'].iloc[index+1], format) - datetime.strptime(row, format))
                    .total_seconds()/60/60)
            time_spent.append(diff)  
        time_spent.append(0)

        checkin['time_spent'] = time_spent

        # Preprocessing
        # Getting time spent in each venue sum
        participantids = checkin['participantId'].unique()
        agg_val = None
        participant_info = []
        places = ['pub', 'apartment', 'resturant', 'workplace']
        for pid in participantids:
            checkin_p = checkin.query("participantId == "+str(pid)+"")
            from datetime import datetime
            format = '%Y-%m-%dT%H:%M:%SZ'
            time_spent=[int((datetime.strptime(checkin_p['timestamp'].iloc[index+1], format) - datetime.strptime(row, format)).total_seconds()/60/60)
                        for index, row in enumerate(checkin_p['timestamp'][:-1])]
            time_spent.append(0)
            checkin_p = checkin_p.assign(time_spent=time_spent)
            agg_val = checkin_p.groupby('venueType').agg( {"time_spent":"sum"} )
            for i, value in enumerate(agg_val['time_spent'].values):
                participant_info.append([pid, agg_val['time_spent'].values[i], agg_val.index.values[i], sum((agg_val['time_spent'].values))])

        # Preprocessing
        # Merge with participants data with time spent in venue
        # Add age_group

        participant_info_df = pd.DataFrame(participant_info)
        participant_info_df.columns = ['participantId','timeSpentInVenue','venueType', 'totalTime']
        participants_info_checkin_df = pd.merge(participant_info_df, participants, on="participantId")
        participants_info_checkin_df[:4]
        age_group = []
        for index, age in enumerate(participants_info_checkin_df['age']):
            if age <= 25:
                age_group.append('0')
            elif age <= 45:
                age_group.append('1')
            else:
                age_group.append('2')
        participants_info_checkin_df['ageGroup'] = age_group
        print("Processed Participant info")

    def radial_plot(self, df=None,  selectedIds= None):
        if not hasattr(df,'shape'):
            df = self.participants_info_checkin_df
        # venues = df['venueType'].unique()
        venues = ['Pub', 'Apartment', 'Workplace',  'Restaurant']
        # df['ageGroup'] = df['ageGroup'].astype(str)
        df['timePercent'] = [(row[1][0]/row[1][1])*100 for row in df[["timeSpentInVenue",'totalTime']].iterrows()]
        means = []
        maxes = []
        lows = []
        for venue in venues:
            means.append(df[df['venueType'] == venue]['timePercent'].mean())
            maxes.append(df[df['venueType'] == venue]['timePercent'].max())
            lows.append(df[df['venueType'] == venue]['timePercent'].min())

        if not selectedIds:
            selectedIds = df['participantId'].unique()
            plot_df = df[df['participantId'].isin(selectedIds)]
            plot_df = plot_df.sort_values(by=['venueType'], na_position='last')
            fig = px.scatter_polar(plot_df, 
                                r='timePercent',
                                theta="venueType", hover_data=['timeSpentInVenue', "age"],
                                                        hover_name="participantId", 
                                labels={
                                    "timeSpentInVenue": "Time spent (hrs)",
                                    "joviality": "Joviality (Hapiness)",
                                    "color": "Work hours",
                                    "timePercent": "Time spent (%)",
                                    "venueType": "Type of venue",
                                    "age": "Age"
                                },
                                # color='ageGroup',
                                # color_discrete_map={
                                # "less work hours": "#d13f3f", #Red
                                # "more work hours": "#74d13f", #Green
                                # self.age_group[0]: "#d13f3f", #Red
                                # self.age_group[1]: "#74d13f", #Green
                                # self.age_group[2]: "#3f70d1", #Blue
                                # },
                                height=345,
                                )
        else:
            plot_df = df[df['participantId'].isin(selectedIds)]
            selected_time_percent = [plot_df[plot_df['venueType'] == venue]['timePercent'].mean() for venue in venues]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=selected_time_percent, theta=venues, 
                                        marker=dict(
                color='black',
                opacity=0.9,
                size=15,
                line=dict(
                    color='MediumPurple',
                    width=2
                )
            ),name="Participants' time",
            hovertemplate = 'Time spent at %{theta} (%): %{r:.2f}<extra></extra>'
            ))
        
        fig.add_trace(go.Scatterpolar(r=means, theta=list(venues), marker=dict(
                opacity=0.5,
                color='yellow',
                size=13,
                line=dict(
                    color='yellow',
                    width=3,
                )), name='Average time',
                hovertemplate = 'Time spent at %{theta} (%): %{r:.2f}<extra></extra>'
            ))
        fig.add_trace(go.Scatterpolar(r=maxes, theta=list(venues), marker=dict(
                opacity=0.5,
                color='green',
                size=13,
                line=dict(
                    color='green',
                    width=3,
                )),name='Max time',
                hovertemplate = 'Time spent at %{theta} (%): %{r:.2f}<extra></extra>'
                ))
        fig.add_trace(go.Scatterpolar(r=lows, theta=list(venues), marker=dict(
                opacity=0.5,
                color='red',
                size=13,
                line=dict(
                    color='red',
                    width=3,
                )), name='Min time',
                hovertemplate = 'Time spent at %{theta} (%): %{r:.2f}<extra></extra>'
                ))
        
        fig.update_layout( font_family="fantasy", margin=dict(t=15, b=15), )
        return fig


    def age_filter(self, df, ag_selected):
        age_group = [17, 25, 45, 61]
        if ag_selected:
            df_age = pd.DataFrame()
            for i, ag_sel in enumerate(ag_selected):
                if ag_sel != 'legendonly':
                    df_age = pd.concat([df_age, df[df['age'].between(age_group[i], age_group[i+1], inclusive=False)]])
            return df_age
    
        return df

    def call_work_scatter(self, df = None, ag_selected = None):
        if not hasattr(df,'shape'):
            df = self.participants_info_checkin_df[self.participants_info_checkin_df['venueType']=='Workplace']
        df = self.age_filter(df, ag_selected)
        if len(df.columns) > 0:
            temp = self.participants_info_checkin_df[self.participants_info_checkin_df['venueType']=='Workplace']
            less_working_ids = temp[temp['timeSpentInVenue'] <= 50]['participantId'].values
            not_less_working_ids = [x for x in self.participants_info_checkin_df['participantId'].unique() if x not in less_working_ids]
            age_group = [self.age[ag] for ag in df["ageGroup"]]
            fig = px.scatter(df,
                            y='joviality', x='timeSpentInVenue', 
                            color=age_group,
                            symbol=['less work hours' if x in less_working_ids else 'more work hours' for x in list(df['participantId'].values)],
                            symbol_sequence=['circle-open', 'circle', 'square-open'],
                            
                            # {
                            #     "less work hours": 'circle-open',
                            #     "more work hours": 'circle',
                            # },
                            color_discrete_map={
                                "less work hours": "#d13f3f", #Red
                                "more work hours": "#74d13f", #Green
                                self.age[0]: "#d13f3f", #Red
                                self.age[1]: "#74d13f", #Green
                                self.age[2]: "#3f70d1", #Blue
                                },
                            hover_name="participantId", hover_data=['age'],
                            labels={
                                "timeSpentInVenue": "Time spent at work (hrs)",
                                "joviality": "Joviality (Hapiness)",
                                "color": "Age group",
                                "symbol": "Worker type"
                            }, 
                            height=345,
                            
                            )
            fig.update_layout( font_family="fantasy", margin=dict(t=15, b=5), )
            return fig
        fig = px.scatter()
        fig.update_layout( font_family="fantasy", margin=dict(t=15, b=5), )
        # fig.update_layout(
        # hoverlabel=dict(
        #     bgcolor="white",
        #     font_size=16,
        #     font_family="Rockwell"
        # )
        # )
        return fig

    def call_radial_selected(self, df=None, selectedIds=None, ag_selected=None):
        if not hasattr(df,'shape'):
            df = self.participants_info_checkin_df
        df = self.age_filter(df, ag_selected)
        if len(df.columns) > 0:
            return self.radial_plot(df, selectedIds=selectedIds)
        fig = px.scatter_polar()
        fig.update_layout( font_family="fantasy",margin=dict(t=15, b=5), )
        return fig

    def call_age_bar(self):
        self.working_df['work_group'] = self.work_group
        workgroup_count = [[],[],[],[]]
        for wg in range(0,5):
            wg_total = 0
            for ag in range (0,3):
                workgroup_count[0].append(wg)
                workgroup_count[1].append(ag)
                wg_count = len(self.working_df.loc[(self.working_df['work_group']==wg) & (self.working_df['ageGroup']==ag)])
                workgroup_count[2].append(wg_count)
                wg_total += wg_count
            for i in range (wg*3,(wg*3)+3):
                workgroup_count[3].append(round(((workgroup_count[2][i]/wg_total)*100),2))

        fig = px.bar(x=[self.work[i] for i in workgroup_count[0]], y=workgroup_count[2], color=[self.age[i] for i in workgroup_count[1]],
                    color_discrete_map={
                                self.age[0]: "#d13f3f", #Red
                                self.age[1]: "#74d13f", #Green
                                self.age[2]: "#3f70d1", #Blue
                                },
                    hover_data={"Age group(%)": workgroup_count[3]},
                    labels={
                                    "x": "Time spent at work(hrs)",
                                    "y": "Count",
                                    "color": "Age",
                                },
                    height=300)
        fig.update_layout( font_family="fantasy", margin=dict(t=15, b=5), )
        return fig
        