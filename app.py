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
                for n in ctrl.get_tasks_view().get_columns()],
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
            ]
        ),
    ]),
    html.Div([
        dash_table.DataTable(
            id='table-daily-summaries',
            fixed_rows={'headers': True},
            columns=[
                {"id": n, "name": n}
                for n in data.DailyWorkSummaryTableView.get_columns()],
            data=ctrl.get_daily_summary_table(5).get_data(),
            editable=False,
        ),
    ]),
])

@app.callback(
    Output("table-tasks", "data"),
    Output("table-tasks", "selected_cells"),
    Output("table-tasks", "active_cell"),
    Input("table-tasks", "active_cell"),
    State("table-tasks", "derived_viewport_data"),
)
def cell_clicked(active_cell, data):
    if active_cell:
        row = active_cell["row"]
        ctrl.change_task_state(data[row]["id"])

        return ctrl.get_tasks_view().get_data(), [], None

    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)