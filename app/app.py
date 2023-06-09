# import libraries
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash import dash_table

import spacy
from spacy import displacy
import pandas as pd
import math

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)

# Load model
nlp = spacy.load("app\\ner_model")

# Settings for producing displacy images
colors = {"MAS": "linear-gradient(120deg, #a1c4fd, #a1c4fd)", "FEM": "linear-gradient(120deg, #fdcbf1, #fdcbf1)"}
options = {"ents": ["MAS", "FEM"], "colors": colors}

# Function to get spacy doc summary stats
def get_doc_stats(doc):

    total_tokens = doc.__len__()

    total_masculine = len([ent.text for ent in doc.ents if ent.label_ == "MAS"])
    total_feminine = len([ent.text for ent in doc.ents if ent.label_ == "FEM"])

    n = total_feminine + total_masculine

    if (n == 0):
        gt_score = 0.5
    else:
        x = (1/n)*(total_feminine - total_masculine)
        gt_score = 1/(1+math.exp(-x))


    result = {
        'Total Words': total_tokens,
        'Total Masculine Entities': total_masculine,
        'Total Feminine Entities': total_feminine,
        'Percentage Words Masculine': round(total_masculine/total_tokens, 4),
        'Percentage Words Feminine': round(total_feminine/total_tokens, 4),
        'Masculine Entities': [ent.text for ent in doc.ents if ent.label_ == "MAS"],
        'Feminine Entities' : [ent.text for ent in doc.ents if ent.label_ == "FEM"],
        'Gender Target Score' : gt_score
    }

    return result

app.layout = dbc.Container(
    [
    dbc.Navbar(
        children=
        [
            html.Img(src="/assets/job-search-svgrepo-com.svg", height="30px"),
            dbc.NavbarBrand("Gendered Language in Job Advertisements", className="ms-2"),
            dbc.Col(dbc.Button("About", id="btn-about", color="white", n_clicks=0, style={'float' : 'right'}))
        ],
        color="white",
        style={'width' : '100%'}
        )
    ,  
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Header")),
            dbc.ModalBody("Gendered language in job advertisements can discourage applicants. We use NLP is identify gendered language."),
        ],
        id="modal-about",
        size="lg",
        is_open=False,
    ),
    html.Div(
        children=[
            dbc.Textarea(id="job_description", size="lg", placeholder="Enter a job description here", style={'margin' : '50px 0px 10px 0px', 'font-family' : 'sans-serif', 'height' : '200px'})
            ],
        style={}
        ),
    dbc.Button("Run model", id="run_model", color="light", className="me-1", style={}),
    html.Hr(),
    dbc.NavbarSimple(
        children=
        [
            dbc.Button("Show", id="btn-output", color="white", n_clicks=0)
        ],
        brand="Entities Identified",
        color="white",
        style={'width' : '100%'}
        ),
    
    dbc.Collapse(
        html.Div(id='displacy-image'),
        id="collapse-output",
        is_open=False
        ),   
    dbc.NavbarSimple(
        children=
        [
            dbc.Button("Show", id="btn-stats", color="white", n_clicks=0)
        ],
        brand="Model Output",
        color="white",
        style={'width' : '100%'}
        ),
    dbc.Collapse(children=
        [
            html.Div(id='table')
        ],
        id="collapse-stats",
        is_open=False
        ), 
    ]
)




@app.callback(
    Output("modal-about", "is_open"),
    Input("btn-about", "n_clicks"),
    State("modal-about", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-output", "is_open"),
    [Input("btn-output", "n_clicks")],
    [State("collapse-output", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-stats", "is_open"),
    [Input("btn-stats", "n_clicks")],
    [State("collapse-stats", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(Output('displacy-image', 'children'),
              Input('run_model', 'n_clicks'),
              State('job_description', 'value'))
def update_displacy(n_clicks, value):
    

    if n_clicks is not None:
    # Create doc object
        text = value
        doc = nlp(text)

        # Create displacy visualisation
        html_doc = displacy.render(doc, style="ent", options=options)
        disp = dcc.Markdown([html_doc], dangerously_allow_html=True)

    return (disp)

@app.callback(Output('table', 'children'),
              [Input('run_model', 'n_clicks'),
              State('job_description', 'value')])
def update_table(n_clicks, value):

    if n_clicks is not None:

        # Create doc object
        text = value
        doc = nlp(text)

        data=get_doc_stats(doc)

        df = pd.json_normalize(data)
        df = df.transpose()
        df = df.reset_index()
        df.columns = ["Attribute", "Value"]

        return (dbc.Table.from_dataframe(df))

if __name__ == "__main__":
    app.run_server()