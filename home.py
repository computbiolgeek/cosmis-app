import os

import dash_table
import dash_bio
import dash_bio_utils.ngl_parser as ngl_parser
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd


from app import app


# load data
pdb_path = '/Users/lib14/OneDrive/Research/projects/cosmis/dash_app/pdbs/'
data_path = '/Users/lib14/OneDrive/Research/projects/cosmis/dash_app'
dataset_name = 'cosmis_dash.tsv'
cosmis_df = pd.read_csv(
    os.path.join(data_path, dataset_name),
    sep='\t',
    header=0
)
hgnc_to_uniprot = {}
with open(os.path.join(data_path, 'hgnc_to_uniprot.tsv'), 'rt') as in_f:
    for l in in_f:
        x, y = l.strip().split('\t')
        hgnc_to_uniprot[x] = y

# uniprot_id to structure mapping
map_file = 'uniprot_to_struct.tsv'
uniprot_to_struct = pd.read_csv(
    os.path.join(data_path, map_file),
    sep='\t',
    header=0,
    index_col='uniprot_id'
)

# layout
home_layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    className='app_header',
                    children=[
                        html.Span(
                            '''
                            COSMIS is a new framework for quantification of 
                            the constraint on protein-coding genetic variation in 3D spatial neighborhoods. 
                            The central hypothesis of COSMIS is that amino acid sites connected through 
                            direct 3D interactions collectively shape the level of constraint on each site. 
                            It leverages recent advances in computational structure prediction, large-scale 
                            sequencing data from gnomAD, and a mutation-spectrum-aware statistical model. 
                            The framework currently maps the landscape of 3D spatial constraint on 6.1 
                            amino acid sites covering >80% (16,533) of human proteins. As genetic
                            variation database and protein structure databases grow, we will continuously
                            update COSMIS.
                            ''',
                        ),
                    ],
                    style={'padding': 10},
                ),
            ],
        ),
        html.Div(
            [
                html.Hr(),
            ],
            style={
                'padding': 10,
            },
        ),
        html.H4('Explore COSMIS', style={'padding-left': 10}),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        type='search',
                        placeholder='UniProt ID or Gene Name',
                        id='uniprot-id',
                    )
                ),
                dbc.Col(
                    dbc.Button(
                        'Search', color='secondary', className='ml-2', n_clicks=0, id='search-button'
                    ),
                    width='auto',
                )
            ],
            no_gutters=True,
            className='ml-auto flex-nowrap mt-3 mt-md-0',
            align='center',
            style={'padding': 10},
        ),
        html.Div(
            [
                html.Hr(),
                html.Span('Slide to set a threshold'),
                dcc.Slider(
                    id='cosmis-slider',
                    min=-8,
                    max=8,
                    value=8,
                    step=0.25,
                    marks={x: str(x) for x in range(-8, 9, 2)},
                ),
            ],
            style={
                'padding': 10
            },
        ),
        dcc.Store(id='store'),
        dbc.Tabs(
            [
                dbc.Tab(label='Plot', tab_id='cosmis-plot'),
                dbc.Tab(label='3D View', tab_id='3d-view'),
                dbc.Tab(label='Table', tab_id='cosmis-table'),
            ],
            id='tabs',
            active_tab='cosmis-plot',
            style={'padding': 10},
        ),
        html.Div(
            id='tab-content', className='p-4'
        ),
    ],
)


@app.callback(
    Output('tab-content', 'children'),
    [
        Input('tabs', 'active_tab'),
        Input('store', 'data')
    ]
)
def render_tab_content(active_tab, data):
    if active_tab and data is not None:
        if active_tab == 'cosmis-plot':
            return dcc.Graph(figure=data['cosmis-plot'])
        elif active_tab == 'cosmis-table':
            return data['cosmis-table']
        elif active_tab == '3d-view':
            return data['3d-view']
    return 'No tab selected'


def generate_table(dataframe, max_rows=10):
    return dash_table.DataTable(
        columns=[
            {'name': col, 'id': col} for col in [
                'uniprot_id', 'enst_id', 'uniprot_pos', 'uniprot_aa', 'cosmis', 'p_value'
            ]
        ],
        page_size=max_rows,
        data=dataframe.to_dict('records')
    )


@app.callback(
    Output('store', 'data'),
    [
        Input('uniprot-id', 'value'),
        Input('cosmis-slider', 'value'),
        Input('search-button', 'n_clicks')
    ]
)
def generate_graphs(given_uniprot_id, cosmis_cutoff, n):
    if not n:
        return None

    if given_uniprot_id in hgnc_to_uniprot.keys():
        uniprot_id = hgnc_to_uniprot[given_uniprot_id]
    else:
        uniprot_id = given_uniprot_id

    # extract the correct data
    filtered_df = cosmis_df[
        (cosmis_df['uniprot_id'] == uniprot_id) & (cosmis_df['cosmis'] <= cosmis_cutoff)
    ]

    # make a scatter plot
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=filtered_df['uniprot_pos'],
            y=filtered_df['cosmis'],
            mode='markers',
            marker_size=7,
        )
    )
    for i in range(len(filtered_df)):
        fig.add_shape(
            type='line',
            x0=filtered_df['uniprot_pos'].iloc[i],
            x1=filtered_df['uniprot_pos'].iloc[i],
            y0=0,
            y1=filtered_df['cosmis'].iloc[i],
            line=dict(
                color='grey',
                width=1
            )
        )
    fig.update_layout(
        transition_duration=500,
        plot_bgcolor='white'
    )
    fig.update_xaxes(
        ticks='outside',
        linecolor='black',
        linewidth=1,
        title='Sequence position'
    )
    fig.update_yaxes(
        ticks='outside',
        linecolor='black',
        linewidth=1,
        range=[-8, 8],
        title='COSMIS score'
    )

    # create and NGL view
    atoms = ','.join([str(x) for x in filtered_df['uniprot_pos']])
    struct_id = uniprot_to_struct.loc[uniprot_id, 'struct_id']
    struct_source = uniprot_to_struct.loc[uniprot_id, 'struct_source']
    if struct_source == 'PDB':
        selected_atoms = struct_id + '.' + struct_id[4:] + ':1-5000@' + atoms
    elif struct_source == 'SWISS-MODEL':
        selected_atoms = struct_id + '.' + struct_id[-1] + ':1-5000@' + atoms
    else:
        selected_atoms = struct_id + '.A' + ':1-5000@' + atoms

    data_list = [
        ngl_parser.get_data(
            data_path=pdb_path,
            pdb_id=selected_atoms,
            color='blue',
            reset_view=True,
            local=True
        )
    ]
    molstyles_dict = {
        'representations': ['cartoon'],
        'chosenAtomsColor': 'red',
        'chosenAtomsRadius': 1,
        'molSpacingXaxis': 100
    }
    image_parameters = {
        'antialias': True,
        'transparent': True,
        'trim': True,
        'defaultFilename': 'tmp'
    }

    ngl_view = dash_bio.NglMoleculeViewer(
        data=data_list,
        molStyles=molstyles_dict,
        imageParameters=image_parameters
    )

    # make a table
    cosmis_table = generate_table(filtered_df, max_rows=10)

    return {'cosmis-plot': fig, '3d-view': ngl_view, 'cosmis-table': cosmis_table}