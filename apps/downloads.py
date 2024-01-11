import dash_core_components as dcc
import dash_html_components as html


download_layout = html.Div(
    [
        html.H4(
            'Download datasets to explore further',
        ),
        dcc.Dropdown(
            id='app-2-dropdown',
            options=[
                {'label': 'Dataset {}'.format(x), 'value': x} for x in range(10)
            ],
        ),
        html.Button(
            'Download', n_clicks=0, id='download-button',
        ),
        dcc.Download('download-data'),
    ],
    style = {'padding': 10},
)