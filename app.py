# Import packages
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html 
from dash import dcc
from dash.dependencies import Input, Output
from datetime import datetime, date, timedelta

def load_data():
    US_data = pd.read_csv('data/US_data.csv')
    states_data = pd.read_csv('data/states_data.csv')
    return US_data, states_data


US_data, states_data = load_data()
last_updated_date = datetime.now()
state_options =([{'label': 'All USA', 'value': 'USA'}] + [{'label':s, 'value':s} for s in states_data['state'].unique()])# make_list(data, 'states'),

app = dash.Dash(__name__)
server = app.server

def filter_data(dropdown_item):
    '''
    Helper function to filter data for dropdowns
    '''
    if dropdown_item == 'USA':
        filtered_data = US_data
    else:
        filtered_data = states_data[states_data['state'] == '{}'.format(dropdown_item)]

    return filtered_data


# Create app layout
app.layout = html.Div(id = 'row', children = [
    html.H1(id = 'H1', children = 'A Simple USA COVID-19 Dashboard',
    style = {'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40, 'font-family':'Helvetica'}),

    html.Div(children=[
        html.Div(id='dropdown-label', children = 'Select State', style={'font-family':'Helvetica','text-align': 'center', 'font-size': 24, 'font-weight': 'bold'}),
        dcc.Dropdown(id = 'state_dropdown',
        options = state_options,
        value = 'USA', 
        clearable = False,
        searchable = True,
        style={'font-family':'Helvetica', 'font-size': 24,'margin':'auto','width':200, 'text-align': 'center','align-items': 'center'}),
    ],style={'align-items': 'center'},className='justify-content-center'),

    html.Div(children=[
        html.Div(children=[
            html.Div(id='daily-label', children = 'DAILY', style={'text-align': 'center', 'font-size': 28, 'font-weight': 'bold'}),
            html.Div(id='textarea-daily-cases', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2,'marginRight': 2, 'whiteSpace': 'pre-line', 'color': 'red'}),
            html.Div(id='textarea-daily-deaths', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2,'whiteSpace': 'pre-line', 'color': 'black'}),
            html.Div(id='textarea-daily-icu', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2, 'whiteSpace': 'pre-line', 'color': 'orange'}),
            html.Div(id='textarea-daily-pos', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2, 'whiteSpace': 'pre-line', 'color': 'darkorange'}),
        ],style={ 'margin':'auto','width':'50%','font-family':'Helvetica','font-size':24,'display': 'inline-block'}), 
        
        html.Div(children=[
            html.Div(id='summary-label', children = 'TOTAL', style={'text-align': 'center', 'font-size': 28, 'font-weight': 'bold'}),
            html.Div(id='textarea-total-cases', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2,'marginRight': 2,  'color': 'red',}),
            html.Div(id='textarea-total-deaths', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2, 'color': 'black'}),
            html.Div(id='textarea-total-vaccinations-started', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2, 'color': 'green'}),
            html.Div(id='textarea-total-vaccinations-completed', style={'textAlign': 'center', 'marginTop': 2, 'marginBottom': 2, 'marginRight': 2,  'color': 'darkgreen'})
        ],style={ 'margin':'auto','width':'50%','font-family':'Helvetica','font-size':24,'display': 'inline-block'}), 
    ],style={'align-items': 'center'},className='justify-content-center'),

    dcc.Graph(id = 'cases_plot',config={'displayModeBar': False},style={'font-family':'Helvetica'}),#, style={'display': 'inline-block'}),
    dcc.Graph(id = 'icu_plot',config={'displayModeBar': False},style={'font-family':'Helvetica'}),#,,style={'display': 'inline-block'})
    dcc.Graph(id = 'test_plot',config={'displayModeBar': False},style={'font-family':'Helvetica'}),#,,style={'display': 'inline-block'}),
    dcc.Graph(id = 'vaccine_plot',config={'displayModeBar': False},style={'font-family':'Helvetica'}),#,,style={'display': 'inline-block'})

],style={'align-items': 'center'},className='justify-content-center')


# function to update COVID-19 summary metrics
@app.callback([
    Output(component_id='textarea-total-cases', component_property='children'),
    Output(component_id='textarea-total-deaths', component_property='children'),
    Output(component_id='textarea-total-vaccinations-started', component_property='children'),
    Output(component_id='textarea-total-vaccinations-completed', component_property='children'),
    Output(component_id='textarea-daily-cases', component_property='children'),
    Output(component_id='textarea-daily-deaths', component_property='children'),
    Output(component_id='textarea-daily-icu', component_property='children'),
    Output(component_id='textarea-daily-pos', component_property='children')]
    ,[Input(component_id='state_dropdown',component_property='value')])
def update_numbers(state_dropdown_value):

    filtered_data = filter_data(state_dropdown_value)

    covid_cases = 'Infections: {:,}'.format(filtered_data['actuals.cases'].max())[:-2]
    covid_deaths = 'Deaths: {:,}'.format(filtered_data['actuals.deaths'].max())[:-2]
    covid_vaccinations_started = 'Vaccinations started: {:,}'.format((filtered_data['actuals.vaccinationsInitiated'].dropna().iloc[-1]))[:-2]
    covid_vaccinations_completed = 'Vaccinations completed: {:,}'.format((filtered_data['actuals.vaccinationsCompleted'].dropna().iloc[-1]))[:-2]

    daily_cases = 'Infections: {:,}'.format(filtered_data['actuals.newCases'].dropna().iloc[-1])[:-2]
    daily_deaths = 'Deaths: {:,}'.format(filtered_data['actuals.newDeaths'].dropna().iloc[-1])[:-2]
    daily_icu = 'ICU Utilization Rate: {:,} '.format((filtered_data['metrics.icuCapacityRatio'].dropna().iloc[-1]*100)) + '%'
    daily_pos = 'Positivity Rate: {}'.format((filtered_data['metrics.testPositivityRatio'].dropna().iloc[-1]*100)) + '%'

    return covid_cases, covid_deaths, covid_vaccinations_started, covid_vaccinations_completed, daily_cases, daily_deaths, daily_icu, daily_pos

# function toupdate COVID-19 charts
@app.callback([
    Output(component_id='cases_plot', component_property='figure'),
    Output(component_id='test_plot', component_property='figure'),
    Output(component_id='icu_plot', component_property='figure'),
    Output(component_id='vaccine_plot', component_property='figure')]
    ,[Input(component_id='state_dropdown',component_property='value')])
def update_charts(state_dropdown_value):

    filtered_data = filter_data(state_dropdown_value)
    print(last_updated_date)
    print(date.today())
    time_diff = datetime.now() - last_updated_date
    if (time_diff.total_seconds() ) > 60*60*6: # update every 6 hours
            print('updating')
            US_data, states_data = load_data()
            filtered_data = filter_data(state_dropdown_value)

    covid_list_to_plot =[go.Scatter(x=filtered_data['date'],y=filtered_data['actuals.newCases'],
    line=dict(color = 'red', width = 2), name = 'Daily'),
    go.Scatter(x=filtered_data['date'],y=filtered_data['metrics.meanNewCases'],
    line=dict(color = 'firebrick', width = 3), name = '7-day Average'),
    ]

    fig = go.Figure(covid_list_to_plot)
    fig.update_layout(title = 'Daily New COVID-19 Infections',
        xaxis_title = 'Date', yaxis_title = 'COVID-19 Cases',
        plot_bgcolor='white')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)

    test_list_to_plot =[go.Scatter(x=filtered_data['date'],y=filtered_data['metrics.testPositivityRatio']*100,
    line=dict(color = 'orange', width = 2), name = 'Daily'),
    ]
    test_fig = go.Figure(test_list_to_plot)
    test_fig.update_layout(title = 'Test Positivity Rate',
        xaxis_title = 'Date', yaxis_title = '% of Positive Tests',
        plot_bgcolor='white')

    test_fig.update_xaxes(showgrid=False)
    test_fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)

    icu_list_to_plot =[go.Scatter(x=filtered_data['date'],y=filtered_data['metrics.icuCapacityRatio']*100,
    line=dict(color = 'orange', width = 2), name = 'Daily'),
    go.Scatter(x=filtered_data['date'],y=filtered_data['metrics.meanIcuCapacityRatio']*100,
    line=dict(color = 'orange', width = 3), name = '7-day Average'),
    ]

    icu_fig = go.Figure(icu_list_to_plot)
    icu_fig.update_layout(title = 'ICU Bed Utilization Rate',
        xaxis_title = 'Date', yaxis_title = '% of ICU Beds Occupied',
        plot_bgcolor='white')

    icu_fig.update_xaxes(showgrid=False)
    icu_fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)

    vaccine_list_to_plot =[go.Scatter(x=filtered_data['date'],y=filtered_data['actuals.vaccinationsCompleted'],
    line=dict(color = 'darkgreen', width = 2), name = 'Completed'),
    go.Scatter(x=filtered_data['date'],y=filtered_data['actuals.vaccinationsInitiated'],
    line=dict(color = 'lightgreen', width = 2), name = 'Started')
    ]

    vaccine_fig = go.Figure(vaccine_list_to_plot)
    vaccine_fig.update_layout(title = 'COVID-19 Vaccinations',
        xaxis_title = 'Date', yaxis_title = 'Vaccinations Administereed',
        plot_bgcolor='white')

    vaccine_fig.update_xaxes(showgrid=False)
    vaccine_fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)

    return fig, test_fig, icu_fig, vaccine_fig

if __name__ == "main":
    app.run_server(debug=False)