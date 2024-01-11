import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import home
from apps import downloads, about

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

server = app.server

page_list = ['', 'home', 'downloads', 'about']


navbar = html.Nav(
    [
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink('Home', id='home-link', href='/')),
                dbc.NavItem(dbc.NavLink('Downloads', id='download-link', href='/apps/downloads')),
                dbc.NavItem(dbc.NavLink('About', id='about-link', href='/apps/about')),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(
                            'MTR',
                            href='http://biosig.unimelb.edu.au/mtr-viewer/',
                            external_link=True,
                        ),
                        dbc.DropdownMenuItem(
                            'MTR3D',
                            href='http://biosig.unimelb.edu.au/mtr3d/',
                            external_link=True,
                        ),
                        dbc.DropdownMenuItem(
                            'PIVOTAL',
                            href='http://pivotal.yulab.org/',
                            external_link=True,
                        ),
                    ],
                    label='Other Tools',
                    nav=True,
                ),
            ],
            pills=True,
            id='navbar'
        ),
    ],
    style={'padding': 10}
)


app.layout = html.Div([
    navbar,
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    [
        Input('url', 'pathname')
    ],
    [
        State('session-store', 'data')
    ]
)
def display_page(pathname, data):
    if pathname == '/':
        return home.home_layout
    if pathname == '/apps/downloads':
        return downloads.download_layout
    if pathname == '/apps/about':
        return about.about_layout


@app.callback(
    [
        Output('home-link', 'active'),
        Output('download-link', 'active'),
        Output('about-link', 'active')
    ],
    [
        Input('url', 'pathname')
    ]
)
def navbar_state(pathname):
    active_link = (
        [pathname == f'/{x}' for x in page_list]
    )
    return active_link[0], active_link[1], active_link[2]


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
