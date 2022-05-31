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

url = 'https://gasprices.aaa.com/state-gas-price-averages/'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

page = urlopen(req).read()
soup = BeautifulSoup(page, 'lxml')
table = soup.find_all('table')

gas = pd.read_html(str(table))[0]

def remove_dollar(sign):
    try:
        sign = sign.str.replace('$','', regex=True)
    except:
        pass
    return sign

gas = gas.apply(remove_dollar)

code = {'Alabama': 'AL',
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

gas.set_index('State', inplace=True)

gas['Code'] = gas.index.map(code)

gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']] = gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']].astype(float)
gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']] = gas[['Regular', 'Mid-Grade', 'Premium', 'Diesel']].round(decimals=2)

order = list(gas.columns)
order = [order[-1]] + order[:-1]
gas = gas[order]

fig1 = px.choropleth(gas,
                     locations='Code',
                     color='Regular',
                     color_continuous_scale='spectral_r',
                     locationmode='USA-states',
                     scope='usa',
                     height=1000)

fig1.add_scattergeo(locations=gas['Code'],
                    locationmode='USA-states',
                    text=gas['Code'],
                    mode='text',
                    hoverinfo='skip')

fig1.update_layout(title={'text':'Current Price of Regular Unleaded Gasoline by State',
                          'xanchor':'center',
                          'yanchor':'top',
                          'x':0.5})

# ------------------------------------------------------------ #

start = datetime.datetime(2019, 3, 1)
end = date.today()

com = pdr.DataReader(['GC=F', 'SI=F', 'PL=F', 'HG=F', 'PA=F', 'CL=F', 'HO=F', 'NG=F', 'RB=F', 'ZC=F',
                      'SB=F', 'ZO=F', 'ZR=F', 'ZS=F', 'LE=F', 'HE=F', 'CC=F', 'KC=F', 'CT=F', 'LBS=F'],
                      'yahoo', start, end)['Adj Close']

com = com.rename(columns={'GC=F':'Gold',
                          'SI=F':'Silver',
                          'PL=F':'Platinum',
                          'HG=F':'Copper',
                          'PA=F':'Palladium',
                          'CL=F':'Crude Oil',
                          'HO=F':'Heating Oil',
                          'NG=F':'Natural Gas',
                          'RB=F':'Gasoline Futures',
                          'ZC=F':'Corn',
                          'SB=F':'Sugar',
                          'ZO=F':'Oat',
                          'ZR=F':'Rough Rice',
                          'ZS=F':'Soybean',
                          'LE=F':'Live Cattle',
                          'HE=F':'Lean Hogs',
                          'CC=F':'Cocoa',
                          'KC=F':'Coffee',
                          'CT=F':'Cotton',
                          'LBS=F':'Lumber'})

com = com.stack().reset_index()
com = com.rename(columns={com.columns[2]:'Closing Price'})

# ------------------------------------------------------------ #

home = pdr.DataReader('CSUSHPINSA', 'fred', start, end)
cpi = pdr.DataReader('CPIAUCSL', 'fred', start, end)
ppi = pdr.DataReader('PPIACO', 'fred', start, end)

home['% Change'] = home['CSUSHPINSA'].pct_change().round(4)*100
cpi['% Change'] = cpi['CPIAUCSL'].pct_change().round(4)*100
ppi['% Change'] = ppi['PPIACO'].pct_change().round(4)*100

home = home.rename(columns={'CSUSHPINSA':'Case Shiller Home Price Index'})
cpi = cpi.rename(columns={'CPIAUCSL':'Consumer Price Index'})
ppi = ppi.rename(columns={'PPIACO':'Producer Price Index'})

fig3 = px.bar(cpi,
              y='% Change',
              color='% Change',
              color_continuous_scale='BlueRed',
              title='Consumer Price Index - Month to Month % Change',
              height=500)
fig3.update_xaxes(title='')

fig4 = px.bar(ppi,
              y='% Change',
              color='% Change',
              color_continuous_scale='BlueRed',
              title='Producer Price Index - Month to Month % Change',
              height=500)
fig4.update_xaxes(title='')

fig5 = px.bar(home,
              y='% Change',
              color='% Change',
              color_continuous_scale='BlueRed',
              title='Case Shiller Home Price Index - Month to Month % Change',
              height=500)
fig5.update_xaxes(title='')

# ------------------------------------------------------------ #

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1('Inflation Tracking Dashboard',
                        className='text-center text-primary mb-4'),
                width=15)
            ),

    dbc.Row(
        dbc.Col([
            dcc.Graph(id='gas_map', figure=fig1)
                ]),
            justify='center'
           ),

    dbc.Row([
        dbc.Col(
            dcc.Graph(id='cpi_bar', figure=fig3)),
         
        dbc.Col(
            dcc.Graph(id='ppi_bar', figure=fig4)),
        
        dbc.Col(
            dcc.Graph(id='home_bar', figure=fig5))
            ], justify='start'
            ),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='drpdwn', multi=False, value='',
                        options=[{'label':x, 'value':x}
                                 for x in sorted(com['Symbols'].unique())]
                        ),
            dcc.Graph(id='commodity-select', figure={})
                ])
            ]),

                            ], fluid=True)

# ------------------------------------------------------------ #

@app.callback(Output('commodity-select', 'figure'),
              Input('drpdwn', 'value'))

def update_plot(commodity_selected):
    com_select = com[com['Symbols'] == commodity_selected]
    fig2 = px.line(com_select,
                   y='Closing Price',
                   x='Date',
                   title='Daily Closing Commodity Prices',
                   height=700)
    fig2.update_xaxes(title='')
    return fig2

if __name__ == "__main__":
    app.run_server(debug=True, port=8800)