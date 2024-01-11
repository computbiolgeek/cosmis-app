import dash_core_components as dcc
import dash_html_components as html


about_layout = html.Div(
    [
        html.H4(
            'About COSMIS'
        ),
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
        html.Br(),
        html.Br(),
        html.H4(
            'Citation',
        ),
        html.Span(
            '''
            If you find COSMIS helpful in your research, please consider citing the COSMIS paper.
            '''
        )
    ],
    style={'padding': 10}
),
