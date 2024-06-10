import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Sample']
collection = db['Data']

# Fetch data from MongoDB
def fetch_data():
    data = list(collection.find())
    return pd.DataFrame(data)

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("MongoDB Dashboard", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='data-graph'), width=8),
        dbc.Col([
            html.H4("Add New Data"),
            dbc.Input(id='input-name', placeholder='Enter name', type='text'),
            dbc.Input(id='input-value', placeholder='Enter value', type='number'),
            dbc.Button('Add Data', id='add-button', color='primary', className='mt-2'),
            html.Hr(),
            html.H4("Update Data"),
            dbc.Input(id='update-id', placeholder='Enter ID', type='text'),
            dbc.Input(id='update-name', placeholder='Enter new name', type='text'),
            dbc.Input(id='update-value', placeholder='Enter new value', type='number'),
            dbc.Button('Update Data', id='update-button', color='warning', className='mt-2'),
            html.Hr(),
            html.H4("Delete Data"),
            dbc.Input(id='delete-id', placeholder='Enter ID', type='text'),
            dbc.Button('Delete Data', id='delete-button', color='danger', className='mt-2')
        ], width=4)
    ])
])

# Callback to update the graph
@app.callback(
    Output('data-graph', 'figure'),
    Input('add-button', 'n_clicks'),
    Input('update-button', 'n_clicks'),
    Input('delete-button', 'n_clicks'),
    State('input-name', 'value'),
    State('input-value', 'value'),
    State('update-id', 'value'),
    State('update-name', 'value'),
    State('update-value', 'value'),
    State('delete-id', 'value')
)
def update_graph(add_clicks, update_clicks, delete_clicks, name, value, update_id, update_name, update_value, delete_id):
    ctx = dash.callback_context

    if not ctx.triggered:
        df = fetch_data()
        fig = px.scatter(df, x='name', y='value', title='Data from MongoDB')
        return fig

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-button' and name and value is not None:
        collection.insert_one({'name': name, 'value': value})
    elif button_id == 'update-button' and update_id and update_name and update_value is not None:
        collection.update_one({'_id': ObjectId(update_id)}, {"$set": {'name': update_name, 'value': update_value}})
    elif button_id == 'delete-button' and delete_id:
        collection.delete_one({'_id': ObjectId(delete_id)})

    df = fetch_data()
    if df.empty:
        return px.scatter()
    fig = px.scatter(df, x='name', y='value', title='Data from MongoDB')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
