import pandas as pd
import pandas_datareader as pdr
import plotly.express as px
import datetime
from datetime import date
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# ------------------------------------------------------------ #

start = datetime.datetime(2019, 3, 1)
end = date.today()

com = pdr.DataReader(['GC=F', 'SI=F', 'PL=F', 'HG=F', 'PA=F', 'CL=F', 'HO=F',
                      'NG=F', 'RB=F', 'ZC=F', 'SB=F', 'ZO=F', 'ZS=F', 'LE=F',
                      'HE=F', 'CC=F', 'KC=F', 'CT=F', 'LBS=F'],
                     'yahoo', start, end)['Adj Close']

com = com.rename(columns={'GC=F': 'Gold',
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
                          'LBS=F': 'Lumber'})

com = com.stack().reset_index()
com = com.rename(columns={com.columns[2]: 'Closing Price'})

# ------------------------------------------------------------ #

url = 'https://gasprices.aaa.com/state-gas-price-averages/'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

page = urlopen(req).read()
soup = BeautifulSoup(page, 'lxml')
table = soup.find_all('table')

gas = pd.read_html(str(table))[0]

def remove_dollar(sign):
    sign = sign.str.replace('$', '', regex=True)
    return sign

gas = gas.apply(remove_dollar)

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

gas['Abbreviation'] = gas.State.map(abbv)

gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']
    ] = gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']].astype(float)
gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']
    ] = gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']].round(2)

fig2 = px.choropleth(gas,
                     locations='Abbreviation',
                     color='Regular',
                     color_continuous_scale='spectral_r',
                     locationmode='USA-states',
                     scope='usa',
                     title='Price of Regular Unleaded Gasoline',
                     height=1000)

fig2.add_scattergeo(locations=gas['Abbreviation'],
                    locationmode='USA-states',
                    text=gas['Abbreviation'],
                    mode='text',
                    hoverinfo='skip')

fig2.update_layout(coloraxis_colorbar_title='Price $',
                   title=dict(xanchor='center',
                              yanchor='top',
                              font_size=18,
                              x=0.5,))

# ------------------------------------------------------------ #

hpi = pdr.DataReader('CSUSHPINSA', 'fred', start, end)
cpi = pdr.DataReader('CPIAUCSL', 'fred', start, end)
ppi = pdr.DataReader('PPIFIS', 'fred', start, end)
pce = pdr.DataReader('PCEPI', 'fred', start, end)
exp = pdr.DataReader('MICH', 'fred', start, end)
ppm = pdr.DataReader('STLPPM', 'fred', start, end)

hpi['%'] = hpi['CSUSHPINSA'].pct_change().round(4) * 100
cpi['%'] = cpi['CPIAUCSL'].pct_change().round(4) * 100
ppi['%'] = ppi['PPIFIS'].pct_change().round(4) * 100
pce['%'] = pce['PCEPI'].pct_change().round(4) * 100

hpi = hpi.rename(columns={'CSUSHPINSA': 'Case Shiller Home Price Index'})
cpi = cpi.rename(columns={'CPIAUCSL': 'Consumer Price Index'})
ppi = ppi.rename(columns={'PPIFIS': 'Producer Price Index'})
pce = pce.rename(columns={'PCEPI': 'Personal Consumption Expenditures'})
exp = exp.rename(columns={'MICH': 'Univ. of Michigan Inflation Expectations'})
ppm = ppm.rename(columns={'STLPPM': 'St. Louis Fed Price Pressures Measure'})

fig3 = px.bar(cpi,
              y='%',
              color='%',
              color_continuous_scale='BlueRed',
              title='Consumer Price Index - Monthly % Change')
fig3.update_xaxes(title=None)
fig3.update_yaxes(title=None)

fig4 = px.bar(ppi,
              y='%',
              color='%',
              color_continuous_scale='BlueRed',
              title='Producer Price Index - Monthly % Change')
fig4.update_xaxes(title=None)
fig4.update_yaxes(title=None)

fig5 = px.bar(hpi,
              y='%',
              color='%',
              color_continuous_scale='BlueRed',
              title='Case-Shiller Home Price Index - Monthly % Change')
fig5.update_xaxes(title=None)
fig5.update_yaxes(title=None)

fig6 = px.bar(pce,
              y='%',
              color='%',
              color_continuous_scale='BlueRed',
              title='Personal Consumption Expenditures - Monthly % Change')
fig6.update_xaxes(title=None)
fig6.update_yaxes(title=None)

fig7 = px.line(ppm,
               y='St. Louis Fed Price Pressures Measure',
               title='St. Louis Fed Price Pressures Measure')
fig7.update_xaxes(title=None)
fig7.update_yaxes(title=None)

fig8 = px.line(exp,
               y='Univ. of Michigan Inflation Expectations',
               title='Univ. of Michigan Consumer Inflation Expectations')
fig8.update_xaxes(title=None)
fig8.update_yaxes(title=None)

# ------------------------------------------------------------ #

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1('Inflation Tracking Dashboard',
                        className='text-center text-primary mb-4'),
                width=15)
            ),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='drpdwn',
                         multi=False,
                         clearable=False,
                         placeholder='Select a Commodity',
                         options=[{'label': x, 'value': x}
                                  for x in sorted(com['Symbols'].unique())]
                         ),
            dcc.Graph(id='commodity-select', figure={})
                ])
            ]),

    dbc.Row(
        dbc.Col([
            dcc.Graph(id='gas_map', figure=fig2)
                ]), justify='center'
            ),

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
                dcc.Graph(id='ppm_bar', figure=fig7)),
            dbc.Col(
                dcc.Graph(id='exp_bar', figure=fig8))
            ]),

                            ], fluid=True)

# ------------------------------------------------------------ #

@app.callback(Output('commodity-select', 'figure'),
              Input('drpdwn', 'value'))

def update_plot(commodity_selected):
    com_select = com[com['Symbols'] == commodity_selected]
    fig1 = px.line(com_select,
                   y='Closing Price',
                   x='Date',
                   height=700)
    fig1.update_xaxes(title=None)
    return fig1

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
