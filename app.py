import logging

import dash
from dash import Dash, html, dcc

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.Div([
        html.Table(
            html.Tbody(
                html.Tr([
                    html.Th(dcc.Link("Home", href="/")),
                    html.Th(dcc.Link("Analytics", href="/analytics")),
                    html.Th(dcc.Link("Timeline", href="/timeline")),
                ])
            )
        ),
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
