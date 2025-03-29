import dash
from dash import html, dcc, Input, Output
import data
import plotly.express as px
import pandas as pd
import datetime

dash.register_page(__name__)

ctrl = data.Controller.get()

def parse_time_range(
    start_date_str=None,
    end_date_str=None,
):
    if start_date_str is None:
        start = datetime.date.today() - datetime.timedelta(days=7)
    else:
        start = datetime.date.fromisoformat(start_date_str)

    if end_date_str is None:
        end = datetime.date.today()
    else:
        end = datetime.date.fromisoformat(end_date_str)

    return start, end


def get_tasks_pie(
    start_date_str=None,
    end_date_str=None,
    group_by="name",
):
    start, end = parse_time_range(start_date_str, end_date_str)

    fig=px.pie(
        ctrl.get_tasks_dataframe(start, end),
        values="runtime",
        names=group_by,
        hover_data="runtime_str",
        title=f"Tasks distribution by runtime between {start} - {end}",
    )
    hovertemplate = "<b>%{label}</b><br>runtime: %{customdata[0]}"
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate=hovertemplate,
    )
    return fig


layout = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        start_date=datetime.date.today() - datetime.timedelta(days=7),
        end_date=datetime.date.today(),
        min_date_allowed=ctrl.get_first_activity_date().date(),
        first_day_of_week=1,
        minimum_nights=0,
    ),
    dcc.Dropdown(
        id='category-dropdown',
        options=[o for o in ctrl.get_tasks_dataframe(*parse_time_range()) if o not in ["runtime", "runtime_str"]],
        value="name",
    ),
    dcc.Graph(
        id='tasks-pie-chart',
        figure=get_tasks_pie(),
        style={'height': '90vh'},
    ),
])

@dash.callback(
    Output('tasks-pie-chart', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('category-dropdown', 'value'),
)
def update_pie_chart(start_date, end_date, category):
    return get_tasks_pie(start_date, end_date, category)
