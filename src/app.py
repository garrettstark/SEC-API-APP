## Simple Dash AG Grid to return 10-k, 10-Q and DEF 14A filings information from SEC API. 
import requests
import pandas as pd
import dash  
from dash import Dash, dcc, html, callback, Output, Input, State, no_update, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc

from gridsetup import table
user_email = "test@test.com"

def CompanyData():
  """ Lookup the SEC Company Data For Dropdown 1 """
  headers = {'User-Agent': user_email }
  companyTickers = requests.get(
      "https://www.sec.gov/files/company_tickers.json",
      headers=headers
  )
  companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
    
  # Add a new column named 'cik_ten_digits' with 10-digit padded CIK values
  companyData['cik_ten_digits'] = companyData['cik_str'].apply(lambda x: str(x).zfill(10))
  return companyData

def DocsLookup(cik_ten_digits, title):
  headers = {'User-Agent': user_email}
  filingMetadata = requests.get(f'https://data.sec.gov/submissions/CIK{cik_ten_digits}.json', headers=headers)
  allForms = pd.DataFrame.from_dict(filingMetadata.json()['filings']['recent'])
  
  def create_url(row):
    primaryDocument = row['primaryDocument']
    accessionNumber = row['accessionNumber'].replace('-', '')
    return f"https://www.sec.gov/Archives/edgar/data/{cik_ten_digits}/{accessionNumber}/{primaryDocument}"
    
  # Apply lambda function to create URLs and assign using .loc
  allForms.loc[:, 'URL'] = allForms.apply(create_url, axis=1)
  # Filter to relevant columns
  filtered_forms = allForms[(allForms['form'] == '10-K') | (allForms['form'] == 'DEF 14A') | (allForms['form'] == '10-Q')]
  filtered_forms = filtered_forms.drop(['act', 'fileNumber', 'filmNumber', 'items', 'core_type', 'size', 'isXBRL', 'isInlineXBRL', 'primaryDocDescription', 'acceptanceDateTime', 'primaryDocument', 'accessionNumber'], axis=1)
  # Create markdownURL column with formatted string
  filtered_forms['markdownURL'] = filtered_forms[['form', 'URL']].apply(lambda x: f"[{x['form']}]({x['URL']})", axis=1)
  # Company name from title
  filtered_forms['company'] = title
  # Extract report year with vectorized approach
  filtered_forms['reportYear'] = pd.to_datetime(filtered_forms['reportDate']).dt.year
  # Reset index for consistency
  filtered_forms.reset_index(drop=True, inplace=True)
  return filtered_forms


df_company = CompanyData()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','Content' : 'width=device-width,  initial-scale=1.0'}] )
server = app.server

app.layout = dbc.Container([
    dcc.Store(id="lookups-id", data=[], clear_data = True, storage_type='session'), #this is CIK data for dropdown
    dcc.Store(id="title-id", data=[], clear_data = True, storage_type='session'),
    dbc.Row([
        dbc.Col([
            html.H2("Company")
        ]), 
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='company-dpdn',
                options=[{'label': s, 'value': s} for s in sorted(df_company.title.unique())],
                value=[],
                clearable=False,
                ), 
        ], width=4,), 

         dbc.Col([
            dcc.Dropdown(
                id='form-dpdn',
                options=[
                     {'label': '10-K', 'value': '10-K'},
                     {'label': '10-Q', 'value': '10-Q'},
                     {'label': 'DEF 14A', 'value': 'DEF 14A'},
                ],
                value=[],
                clearable=True,
                multi=True,  
                ), 
        ], width=2,), 
    ]), 

    dbc.Row([
        dbc.Col([
            html.Label("SEC Records", style={'fontSize':20, 'textAlign':'Left'}),
            dbc.Spinner(children=[table], size="lg", color="primary", type="border", fullscreen=True,),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div(id="loading-output-1")
    ),
        ], width={'size': 8, }), #close column
    ]),
]),

is_initial_load = True #Prevent initial call error

@app.callback(
    Output('lookups-id', 'data'),
    Output('title-id', 'data'),
    Input('company-dpdn', 'value'),
    prevent_initial_call=True
)

def CIK_Lookup(chosen_company):
    dff = df_company[df_company.title==chosen_company]
    title = dff['title'].item()
    cik = dff['cik_ten_digits'].head(1).item() 
    return cik, title

@app.callback(
    Output('table-id', 'rowData'),
    Input('lookups-id', 'data'), # CIK
    Input('title-id', 'data'), # Tile
    Input('form-dpdn', 'value'),
    prevent_initial_call=True,
)

def DocumentLookupStep(cik, title, forms_selected):
    global is_initial_load
    if is_initial_load:
        is_initial_load = False
        print("Initial Load is False")
        return []  

    else:
        docs = DocsLookup(cik, title)
        # Filter based on forms_selected (if not empty)
        if forms_selected:
            filtered_docs = docs[docs['form'].isin(forms_selected)]
        else:
            filtered_docs = docs.copy()  # Show all forms if none selected
        return filtered_docs.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True, port=8008)
