import dash
from dash import Dash, html, dash_table, Output, Input, State, dcc
import data
import logging

MAX_DAILY_SUMMARIES = 31  # days

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )

dash.register_page(__name__, path='/')

ctrl = data.Controller()

layout = html.Div([
    html.H1(id="title",children="", hidden=True),
    html.Div(id="empty"),
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
        dcc.Input(
            id="task-name-input",
            placeholder="new task name",
        ),
        html.Button(
            id="new-task-button",
            children="Start New",
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
            data=ctrl.get_daily_summary_table(MAX_DAILY_SUMMARIES).get_data(),
            editable=False,
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_header={
                'fontWeight': 'bold'
            },
        ),
    ]),
])

@dash.callback(
    Output("table-tasks", "data"),
    Output("table-tasks", "selected_cells"),
    Output("table-tasks", "active_cell"),
    Output("table-daily-summaries", "data"),
    Output("title", "children"),
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
        ctrl.get_daily_summary_table(MAX_DAILY_SUMMARIES).get_data(),
        ctrl.get_active_task_name(),
    )

@dash.callback(
    Output("table-tasks", "data", allow_duplicate=True),
    Output("table-daily-summaries", "data", allow_duplicate=True),
    Output("task-name-input", "value"),
    Output("title", "children", allow_duplicate=True),
    State("task-name-input", "value"),
    Input("new-task-button", "n_clicks"),
    prevent_initial_call=True,
)
def add_new_task(name, n_clicks):
    task = ctrl.add_task(name)
    ctrl.change_task_state(task.id)
    return (
        ctrl.get_tasks_view().get_data(),
        ctrl.get_daily_summary_table(MAX_DAILY_SUMMARIES).get_data(),
        "",
        ctrl.get_active_task_name(),
    )


dash.clientside_callback(
    """
    function(title) {
        document.title = title
        var link = document.querySelector("link[rel~='icon']");
        if (title === "") {
            link.href = 'https://images.icon-icons.com/934/PNG/512/pause-multimedia-big-gross-symbol-lines_icon-icons.com_72964.png';
        }else{
            link.href = 'https://images.icon-icons.com/934/PNG/512/play-black-triangle-interface-symbol-for-multimedia_icon-icons.com_72958.png';
        }
    }
    """,
    Output('empty', 'children'),
    Input('title', 'children'),
)
