import dash
from dash import html, dcc, Input, Output
import data
import plotly.express as px
import pandas as pd
import datetime

dash.register_page(__name__)

ctrl = data.Controller.get()

def get_timeline(date):
    fig = px.timeline(
        ctrl.get_daily_timeline_dataframe(date),
        x_start="start",
        x_end="end",
        y="name",
        text="name",
        color="name", # to put the same task to the same line
        title=f"Timeline of {date}",
    )
    return fig

layout = html.Div([
        dcc.DatePickerSingle(
        id='date-picker',
        initial_visible_month=datetime.date.today(),
        date=datetime.date.today(),
        min_date_allowed=ctrl.get_first_activity_date().date(),
        first_day_of_week=1,
    ),
    dcc.Graph(
        id='activity-timeline',
        figure=get_timeline(datetime.date.today()),
        #style={'height': '90vh'},
    ),
])



@dash.callback(
    Output('activity-timeline', 'figure'),
    Input('date-picker', 'date'),
)
def update_chart(date):
    return get_timeline(datetime.date.fromisoformat(date))
