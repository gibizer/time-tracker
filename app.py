import dash
from dash import Dash, html, dash_table, Output, Input, State, dcc
import data
import logging
import datetime
import math


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )

ctrl = data.Controller()

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dash_table.DataTable(
            id='table-tasks',
            fixed_rows={'headers': True},
            columns=[
                {"id": n, "name": n}
                for n in data.TasksView.get_columns()],
            data=ctrl.get_tasks_view().get_data(),
            editable=False,
            style_data_conditional=[
            {
                'if': {
                    'column_id': 'state',
                    'filter_query': '{state} = running',
                },
                'backgroundColor': 'red',
                'color': 'white'
            },
            ],
            filter_action="native",
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_header={
                'fontWeight': 'bold'
            },
        ),
    ]),
    html.Hr(),
    html.Div([
        dash_table.DataTable(
            id='table-daily-summaries',
            fixed_rows={'headers': True},
            columns=[
                {"id": n, "name": n}
                for n in data.DailyWorkSummaryTableView.get_columns()],
            data=ctrl.get_daily_summary_table(30).get_data(),
            editable=False,
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_header={
                'fontWeight': 'bold'
            },
        ),
    ]),
])

@app.callback(
    Output("table-tasks", "data"),
    Output("table-tasks", "selected_cells"),
    Output("table-tasks", "active_cell"),
    Output("table-daily-summaries", "data"),
    Input("table-tasks", "active_cell"),
    State("table-tasks", "derived_viewport_data"),
)
def cell_clicked(active_cell, data):
    if active_cell:
        task_id = active_cell["row_id"]
        ctrl.change_task_state(task_id)

    return (
        ctrl.get_tasks_view().get_data(),
        [],
        None,
        ctrl.get_daily_summary_table(30).get_data()
    )


if __name__ == "__main__":
    app.run_server(debug=True)