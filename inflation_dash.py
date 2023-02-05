import datetime
from datetime import date

import pandas as pd
import pandas_datareader as pdr
import yfinance as yf

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from bs4 import BeautifulSoup
import requests

import plotly.express as px

#---------------Collect Commodity Prices---------------#

# Set start and end dates
start_date = datetime.datetime(2019, 3, 1) 
end_date = date.today()

# These symbols correspond to different commodities tracked on Yahoo Finance
commodity_symbols = ['GC=F', 'SI=F', 'PL=F', 'HG=F', 'PA=F', 'CL=F', 'HO=F',
                     'NG=F', 'RB=F', 'ZC=F', 'SB=F', 'ZO=F', 'ZS=F', 'LE=F',
                     'HE=F', 'CC=F', 'KC=F', 'CT=F', 'LBS=F']

# User-friendly descriptions of commodities
commodity_names = {'GC=F': 'Gold',
                   'SI=F': 'Silver',
                   'PL=F': 'Platinum',
                   'HG=F': 'Copper',
                   'PA=F': 'Palladium',
                   'CL=F': 'Crude Oil',
                   'HO=F': 'Heating Oil',
                   'NG=F': 'Natural Gas',
                   'RB=F': 'Gasoline Futures',
                   'ZC=F': 'Corn',
                   'SB=F': 'Sugar',
                   'ZO=F': 'Oat',
                   'ZS=F': 'Soybean',
                   'LE=F': 'Live Cattle',
                   'HE=F': 'Lean Hogs',
                   'CC=F': 'Cocoa',
                   'KC=F': 'Coffee',
                   'CT=F': 'Cotton',
                   'LBS=F': 'Lumber'}

# Collect closing prices and rename column headers
commodities = yf.download(commodity_symbols, start_date, end_date)['Adj Close']
commodities = commodities.rename(columns=commodity_names)

# Unpivot from wide to long format
commodities = pd.melt(commodities.reset_index(), id_vars='Date', value_name='Closing Price')
commodities = commodities.rename(columns={'variable': 'Commodity Name'})

#---------------Scrape AAA Gas Prices---------------#

# Scrape gas prices table from AAA website into DataFrame
url = 'https://gasprices.aaa.com/state-gas-price-averages/'
headers = {'User-Agent': 'Mozilla/5.0'}

# Using pd.read_html() directly without BeautifulSoup is a viable alternative here
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.content, 'lxml')
table = soup.find_all('table')

gas_prices = pd.read_html(str(table))[0]

# Dictionary of 2-letter abbreviations of states for Plotly map
abbv = {'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'}

# New abbreviation column using map on State column
gas_prices['Abbreviation'] = gas_prices.State.map(abbv)

# Removing dollar sign from gas price columns and converting values to float
gas_prices[['Regular', 'Mid-Grade', 'Premium', 'Diesel']] = \
gas_prices[['Regular', 'Mid-Grade', 'Premium', 'Diesel']].replace('[\$,]', '', regex=True).astype(float)


#---------------Build Gas Prices Map---------------#

fig2 = px.choropleth(gas_prices,
                     locations='Abbreviation',
                     color='Regular',
                     color_continuous_scale='spectral_r', # Adding _r to any colorscale reverses it
                     locationmode='USA-states',
                     scope='usa',
                     title='Price of Regular Unleaded Gasoline',
                     height=1000)

fig2.add_scattergeo(locations=gas_prices['Abbreviation'],
                    locationmode='USA-states',
                    text=gas_prices['Abbreviation'],
                    mode='text',
                    hoverinfo='skip')

fig2.update_layout(coloraxis_colorbar_title='Price $',
                   title=dict(xanchor='center',
                              yanchor='top',
                              font_size=18,
                              x=0.5,))

#---------------Collect Economic Indicators---------------#

def fetch_data(fred_code, series_name, start_date, end_date, is_percent=True):
    '''
    Fetches data from the FRED database using a unique FRED code.
    
    Parameters:
        fred_code (str): The FRED code of the data series to be fetched.
        series_name (str): The name of the series to be used as a column name.
        start_date (str): The start date for the data series in the format 'YYYY-MM-DD'.
        end_date (str): The end date for the data series in the format 'YYYY-MM-DD'.
        is_percent (bool, optional): If True, the returned data frame will include a 
                                     'Percent' column with the percentage change of 
                                     the data series. Default is True.
    
    Returns:
        pandas.DataFrame: The fetched data with the specified series name and, if is_percent is True, a 'Percent' column.
    '''
    df = pdr.DataReader(fred_code, 'fred', start_date, end_date)
    if is_percent:
        df['Percent'] = df[fred_code].pct_change().round(4) * 100
    df = df.rename(columns={fred_code: series_name})
    return df

# Create each indicator variable
hpi = fetch_data('CSUSHPINSA', 'Case Shiller Home Price Index', start_date, end_date)
cpi = fetch_data('CPIAUCSL', 'Consumer Price Index', start_date, end_date)
ppi = fetch_data('PPIFIS', 'Producer Price Index', start_date, end_date)
pce = fetch_data('PCE', 'Personal Consumption Expenditures', start_date, end_date)
exp = fetch_data('MICH', 'Univ. of Michigan Inflation Expectations', start_date, end_date, is_percent=False)
ppm = fetch_data('STLPPM', 'St. Louis Fed Price Pressures Measure', start_date, end_date, is_percent=False)

#---------------Build Indicator Plots---------------#

def plot_indicator(dataframe, indicator, title, plot_type='bar'):
    '''
    Plots the data from a dataframe using the specified indicator.

    Parameters:
        dataframe (pandas.DataFrame): The data to plot.
        indicator (str): The column from the dataframe to use as the fred indicator.
        title (str): The title to use for the plot.
        plot_type (str, optional): The type of plot to create. Default is 'bar'.

    Returns:
        plotly.graph_objs._figure.Figure: The plotly figure object, either a bar or line plot.
    '''
    fig = None
    percentages = ['Consumer Price Index', 'Producer Price Index',
                   'Case-Shiller Home Price Index',
                   'Personal Consumption Expenditures']
    y = 'Percent' if indicator in percentages else indicator
    
    if plot_type == 'bar':
        fig = px.bar(dataframe, y=y, color=y, color_continuous_scale='BlueRed', title=title)
    elif plot_type == 'line':
        fig = px.line(dataframe, y=y, title=title)
    
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return fig

# Create a plot variable for each indicator DataFrame
fig3 = plot_indicator(cpi, 'Consumer Price Index', \
                      'Consumer Price Index - Monthly % Change')

fig4 = plot_indicator(ppi, 'Producer Price Index', \
                      'Producer Price Index - Monthly % Change')

fig5 = plot_indicator(hpi, 'Case-Shiller Home Price Index', \
                      'Case-Shiller Home Price Index - Monthly % Change')

fig6 = plot_indicator(pce, 'Personal Consumption Expenditures', \
                      'Personal Consumption Expenditures - Monthly % Change')

fig7 = plot_indicator(ppm, 'St. Louis Fed Price Pressures Measure', \
                      'St. Louis Fed Price Pressures Measure', plot_type="line")
                  
fig8 = plot_indicator(exp, 'Univ. of Michigan Inflation Expectations', \
                      'Univ. of Michigan Consumer Inflation Expectations', plot_type="line")

#---------------Dash Layout---------------#

# Initialize Dash app with external stylesheet and meta tag
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# Begin layout with dash_bootstrap_components Container
app.layout = dbc.Container([

# High level HTML header
    dbc.Row(
        dbc.Col(html.H1('Inflation Tracking Dashboard',
                        className='text-center text-primary mb-4'),
                width=15)
            ),
 
# This row contains the commodity selection dropdown and corresponding plot
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='drpdwn',
                         multi=False,
                         clearable=False,
                         placeholder='Select a Commodity',
                         # The options are created by taking the unique values in the commodity column
                         options=[{'label': x, 'value': x} 
                                  for x in sorted(commodities['Commodity Name'].unique())]
                         ),
            dcc.Graph(id='commodity-select', figure={})
                ])
            ]),

# This row is the gas prices choropleth map with data scraped from AAA
    dbc.Row(
        dbc.Col([
            dcc.Graph(id='gas_map', figure=fig2)
                ]), justify='center'
            ),

# These rows are an assortment of inflation tracking economic indicators in either bar or line plots
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='cpi_bar', figure=fig3)),
        dbc.Col(
            dcc.Graph(id='ppi_bar', figure=fig4)),
        dbc.Col(
            dcc.Graph(id='hpi_bar', figure=fig5))
            ]),

    dbc.Row([
            dbc.Col(
                dcc.Graph(id='pce_bar', figure=fig6)),
            dbc.Col(
                dcc.Graph(id='ppm_line', figure=fig7)),
            dbc.Col(
                dcc.Graph(id='exp_line', figure=fig8))
            ]),

    ], fluid=True)

#---------------Add Callback Functionality---------------#

# The Dash callback makes the input and output of commodity selection options possible
# via the @app.callback decorator from the Dash library to define a callback function in the app
@app.callback(Output('commodity-select', 'figure'),
              Input('drpdwn', 'value'))

def update_plot(commodity_selected):
    '''
    This function updates the commodity prices plot via the commodity selection dropdown.

    Parameters:
        commodity_selected (str): The name of the selected commodity.

    Returns:
        plotly.graph_objs._figure.Figure: A line plot of the closing prices of the selected commodity over time.
    '''
    commodity_select = commodities[commodities['Commodity Name'] == commodity_selected]
    fig1 = px.line(commodity_select,
                   y='Closing Price',
                   x='Date',
                   height=700)
    fig1.update_xaxes(title=None)
    return fig1

#---------------Run Server---------------#

if __name__ == '__main__':
    app.run_server(debug=True, port=8080) # debug=True enables Dash debug functionality when app is running
