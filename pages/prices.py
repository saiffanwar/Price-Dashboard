from this import d
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import plotly.io as pio
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dataproc import DataProcessing, fileDict
import dash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm import tqdm
import time
import pickle as pck
import numpy as np 
import os
from app import app
dataProc = DataProcessing()
dataProc.updateData(fileDict['TTF'])


def days_hours_minutes(td):
    return str(td.days)+' Days '+str(td.seconds//3600)+' Hours '+str((td.seconds//60)%60)+' Minutes'

def fileAge(path):
    path = fileDict[path][0]
    x = datetime.utcfromtimestamp(os.path.getmtime(os.getcwd()+'/data/'+path+'.csv'))

    lastRefresh = x.strftime('%d-%b-%y %H:%M')
    if x < datetime.today() - timedelta(days=1):
        color = 'red'
    else:
        color = 'black'
    age = datetime.today() - x
    age = days_hours_minutes(age)
    return age, lastRefresh, color

def fetchMinDate(file):
    data = dataProc.fetchData(fileDict[file])
    return min(data['TRADEDATE'])

tradeDate = dataProc.data['Trade Date']
# Selected Contract Month
selectedValue = []
for i in range(13):  # current + next 11 units
    thisMonth = (datetime.today() + relativedelta(months=(i))).strftime('%b-%y')
    selectedValue.append(thisMonth)
selectedValue = selectedValue[1:]

data = dataProc.fetchData(fileDict['TTF'])
gasPrice = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')
gasPrice2 = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')
data = dataProc.fetchData(fileDict['FO'])
oilPrice = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')
oilPrice2 = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')
data = dataProc.fetchData(fileDict['Pacific174'])
freightRate = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')
freightRate2 = px.line(data, x='Trade Date', y='Absolute', color='Contract Month')

linegraph_inputs = [
    html.Div(className='input', children=[
            html.H2(id='data-options-title', className='title', children='Data Selection Options')]),
    
    html.Div(className='input', children=[
    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Gas Price
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': i, 'value': i} for i in ['TAC FE', 'TAC EU', 'TAC ATL', 'TAC ME', 'TTF', 'HH', 'NBP', 'PSV', 'AOC', 'JKM']
        ], value='TAC FE', className='input-item', id='price-gas-data-type-dropdown-linegraph'),
    ],  style=dict(width='30%', margin = '0 0 0 0')),

    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Oil Price
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': i, 'value': i} for i in ['FO', 'GO', 'Ice Brent']
        ], value='GO', className='input-item', id='price-oil-data-type-dropdown-linegraph'),
    ],  style=dict(width='30%', margin = '0 5% 0 5%')),

    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Freight Rate
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': i, 'value': i} for i in ['Pacific174', 'Pacific155', 'Pacific138', 'Atlantic174', 'Atlantic155', 'Atlantic138']
        ], value='Pacific174', className='input-item', id='price-freight-data-type-dropdown-linegraph'),
    ],  style=dict(width='30%', margin = '0 0 0 0'))]),

    html.Div(children=[
    html.Div(className='input-compact', children=[
            html.H2(id='linegraph-options-title', className='title', children='Time Series Options')], style=dict(width='45%')),
    
    html.Div(className='input-compact', children=[
            html.H2(id='yoy-options-title', className='title', children='Y-o-Y Options')], style=dict(width='45%')),
        ]),

    html.Div(className='input-compact', children=[
    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Time Unit
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': 'Contract Month', 'value': 'Contract Month'},
            {'label': 'Quarters', 'value': 'Quarters'},
            {'label': 'Calendar', 'value': 'Calendar'},
            {'label': 'Summer/Winter', 'value': 'Summer/Winter'},
        ], value='Contract Month', className='input-item', id='timeunit-linegraph-dropdown'),
    ],  style=dict(width='45%', margin = '0 5% 0 0')),
    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='Trade Date'),
        dcc.DatePickerRange(
            id='linegraph-date-picker-range', className='date-range-child',
            min_date_allowed=min(dataProc.data['TRADEDATE']),
            max_date_allowed=max(dataProc.data['TRADEDATE']),
            display_format='DD-MMM-YY',
            start_date=(max(dataProc.data['TRADEDATE'])- timedelta(days=365)).replace(day=1),
            end_date=max(dataProc.data['TRADEDATE']),
        )],  style=dict(width='45%', margin = '0 0 0 5%')
             ),]),


    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='Trade Date'),
        dcc.DatePickerRange(
            id='yoy-date-picker-range', className='date-range-child',
            min_date_allowed=min(dataProc.data['TRADEDATE']),
            max_date_allowed=max(dataProc.data['TRADEDATE']),
            display_format='DD-MMM-YY',
            start_date=fetchMinDate('TAC FE'),
            end_date=max(dataProc.data['TRADEDATE']),
        )],  style=dict(margin='0 0 0 20')
             ),


    html.Div(children=[
    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', id='unit-title-linegraph', children='Contract Month'),
        dcc.Dropdown(clearable=True,
                     options=pd.unique(dataProc.data['Contract Month']), value=selectedValue,
                     id='linegraph-date-picker',
                     multi=True)
    ], style=dict(margin='0 20 0 0')),

    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', id='unit-title-yoy', children='Year'),
        dcc.Dropdown(clearable=True,
                     options=pd.unique(list(map(lambda x:x.strftime('%Y'),data['TRADEDATE']))), value=pd.unique(list(map(lambda x:x.strftime('%Y'),data['TRADEDATE']))),
                     id='yoy-date-picker',
                     multi=True)
    ],  style=dict(margin='0 0 0 20')),]),


    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Absolute/D-o-D
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': i, 'value': i} for i in ['Absolute', 'D-o-D Change']
        ], value='Absolute', className='input-item', id='price-absolute-dropdown-linegraph'),
    ],  style=dict(margin='0 0 0 20')),


    html.Div(className='input-compact', children=[
        html.Div(className='dropdown-title-child', children='''
    Absolute/D-o-D
'''),
        dcc.Dropdown(clearable=False, options=[
            {'label': i, 'value': i} for i in ['Absolute', 'D-o-D Change']
        ], value='Absolute', className='input-item', id='price-absolute-dropdown-yoy'),
    ],  style=dict(margin='0 0 0 20')),#])

]

layout = html.Div(
    children=
    linegraph_inputs + [html.Div(children=[
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title', className='title', children='Gas Prices Time Series'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph',
                figure=gasPrice
            )), style={"min-height": "6rem"}),
        ]),
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title-2', className='title', children='Gas Prices Y-o-Y Comparison'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph-2',
                figure=gasPrice2
            )), style={"min-height": "6rem"}),
        ]),
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title-3', className='title', children='Oil Prices Time Series'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph-3',
                figure=oilPrice
            )), style={"min-height": "6rem"}),
        ]),
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title-4', className='title', children='Oil Prices Y-o-Y Comparison'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph-4',
                figure=oilPrice2
            )), style={"min-height": "6rem"}),
        ]),
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title-5', className='title', children='Freight Rate Time Series'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph-5',
                figure=freightRate
            )), style={"min-height": "6rem"}),
        ]),
        html.Div(className='input-compact', children=[
            html.H2(id='linegraph-title-6', className='title', children='Freight Rate Y-o-Y Comparison'),
            html.Div(dcc.Loading(dcc.Graph(
                id='line-graph-6',
                figure=freightRate2
            )), style={"min-height": "6rem"}),
        ]),

    ]),
        dcc.Store(id='loaded-dataframe', storage_type='memory'),
        dcc.Interval(id='page-reload-dcc-interval', interval=10 * 60 * 1000),
        # reloaded every 2 minutes, in milliseconds
    ])


@app.callback(
    Output('linegraph-date-picker', 'options'),
    Output('linegraph-date-picker-range', 'min_date_allowed'),
    Output('yoy-date-picker-range', 'min_date_allowed'),
    Output('linegraph-date-picker', 'value'),
    Output('unit-title-linegraph', 'children'),
    Output('linegraph-title', 'children'),
    Output('linegraph-title-2', 'children'),
    Output('linegraph-title-3', 'children'),
    Output('linegraph-title-4', 'children'),
    Output('linegraph-title-5', 'children'),
    Output('linegraph-title-6', 'children'),
    Input('timeunit-linegraph-dropdown', 'value'),
    Input('price-gas-data-type-dropdown-linegraph', 'value'),
    # Input('price-gas-data-type-dropdown-yoy', 'value'),
    Input('price-oil-data-type-dropdown-linegraph', 'value'),
    # Input('price-oil-data-type-dropdown-yoy', 'value'),
    Input('price-freight-data-type-dropdown-linegraph', 'value'),
    # Input('price-freight-data-type-dropdown-yoy', 'value')
)
def unitChange(value, gastype, oiltype, freightRate):
    dataProc.fetchData(fileDict[gastype])
    contractDateItems = np.unique(dataProc.data[value])
    selectedValue = []
    for x in dataProc.data[value].drop_duplicates(keep='first').values.tolist():
        item = {'label': x, 'value': x}
        selectedValue.append(x)
    if value == 'Contract Month':
        selectedValue = []
        for i in range(13):  # current + next 11 units
            thisMonth = (datetime.today() + relativedelta(months=i)).strftime('%b-%y')
            selectedValue.append(thisMonth)
        selectedValue = selectedValue[1:]

    elif value == 'Quarters':
        q = [['Jan', 'Feb', 'Mar'], ['Apr', 'May', 'Jun'], ['Jul', 'Aug', 'Sep'], ['Oct', 'Nov', 'Dec']]
        selectedValue = []
        for i in range(12):  # current + next 11 units
            thisMonth = (datetime.today() + relativedelta(months=(3 * i)))
            dateData = np.select(
                [thisMonth.strftime('%b') in q[0], thisMonth.strftime('%b') in q[1],
                 thisMonth.strftime('%b') in q[2], thisMonth.strftime('%b') in q[3]],
                [thisMonth.strftime('%y') + 'Q1', thisMonth.strftime('%y') + 'Q2',
                 thisMonth.strftime('%y') + 'Q3', thisMonth.strftime('%y') + 'Q4']
            )
            selectedValue.append(dateData)
    elif value == 'Summer/Winter':
        season = [['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'], ['Oct', 'Nov', 'Dec'], ['Jan', 'Feb', 'Mar']]
        selectedValue = []
        for i in range(12):  # current + next 11 units
            thisMonth = (datetime.today() + relativedelta(months=(6 * i)))
            dateData = np.select(
                [thisMonth.strftime('%b') in season[0], thisMonth.strftime('%b') in season[1],
                 thisMonth.strftime('%b') in season[2]],
                ['Summer ' + thisMonth.strftime('%Y'), 'Winter ' + thisMonth.strftime('%Y'),
                 'Winter ' + thisMonth.strftime('%Y')]
            )
            selectedValue.append(dateData)

    else:
        selectedValue = []
        for i in range(12):  # current + next 11 units
            thisMonth = datetime.today()
            dateData = 'Cal' + str(int(thisMonth.strftime('%y')) + i)
            selectedValue.append(dateData)
    title1= gastype+' Time Series'
    title2=gastype+' Y-o-Y Comparison'
    title3=oiltype+' Time Series'
    title4=oiltype+' Y-o-Y Comparison'
    title5=freightRate+' Time Series'
    title6=freightRate+' Y-o-Y Comparison'


    minDate = min([fetchMinDate(file) for file in [gastype, oiltype, freightRate]])

    return contractDateItems, minDate, minDate, selectedValue, value, title1, title2, title3, title4, title5, title6

for figure, price in zip(['', '-3', '-5'],['price-gas-data-type-dropdown-linegraph', 'price-oil-data-type-dropdown-linegraph','price-freight-data-type-dropdown-linegraph']):

    @app.callback(
        Output(f'line-graph{figure}', 'figure'),

        Input(f'linegraph-date-picker-range', 'start_date'),
        Input(f'linegraph-date-picker-range', 'end_date'),
        Input(f'linegraph-date-picker', 'value'),
        Input(f'timeunit-linegraph-dropdown', 'value'),
        Input(f'price-absolute-dropdown-linegraph', 'value'),

        Input(f'{price}', 'value'),


    )

    def TimeSeriesChange(sDate, eDate, cDate, unit, price_absolute, data_type):

        # All plots for price comparison Time Series
        try:
            eDate = datetime.strptime(eDate, '%Y-%m-%dT%H:%M:%S')
        except:
            eDate = datetime.strptime(eDate, '%Y-%m-%d')
        if eDate.weekday() == 5:
            eDate -= timedelta(days=1)
        elif eDate.weekday() == 6:
            eDate -= timedelta(days=2)

        try:
            sDate = datetime.strptime(sDate, '%Y-%m-%dT%H:%M:%S')
        except:
            sDate = datetime.strptime(sDate, '%Y-%m-%d')
        if sDate.weekday() == 5:
            sDate += timedelta(days=2)
        elif sDate.weekday() == 6:
            sDate += timedelta(days=1)

        xtickformat='%d-%b-%y'
        plot = make_subplots()

        plot.data=[]

        data = dataProc.fetchData(fileDict[data_type])
        if data_type in ['Pacific174', 'Pacific155', 'Pacific138', 'Atlantic174', 'Atlantic155', 'Atlantic138']:
            data['Absolute'] = [np.round(x/1000, 1) for x in data['Absolute']]
            ytitle = price_absolute+str(10)+' (\N{SUPERSCRIPT THREE}) ($ kpd)'
        elif data_type in ['TAC FE', 'TAC EU', 'TAC ATL', 'TAC ME', 'TTF', 'HH', 'NBP', 'PSV', 'AOC', 'JKM']:
            ytitle = price_absolute+'( $/mmbtu)'
        elif data_type in ['FO', 'GO', 'Ice Brent']:
            ytitle = price_absolute+' (%/bbl)'


        daterangeData = data[data['TRADEDATE'] <= eDate]
        daterangeData = daterangeData[daterangeData['TRADEDATE'] >= sDate]
        if len(np.unique(daterangeData['TRADEDATE'])) <100:
            xtickformat='%d-%b-%y'

        # Add each plot for the contract months:
        if unit != 'Contract Month':
            for interval in cDate:
                intervalData = daterangeData[daterangeData[unit] == interval]
                intervalData['Trade Month'] = [x[3:] for x in intervalData['Trade Date']]
                intervalData['Month Average'] = np.zeros(len(intervalData))
                for month in np.unique(intervalData['Trade Month']):
                    monthInterval = intervalData[intervalData['Trade Month'] == month]
                    average = np.mean(monthInterval['Absolute'])
                    for i in monthInterval.index:
                        intervalData.at[i, 'Month Average'] = average
                if price_absolute == 'D-o-D Change':
                    diffs = np.diff(pd.unique(intervalData['Month Average']))
                    plot.add_trace(go.Scatter(x=pd.unique(intervalData['Trade Month']), y=diffs, mode='lines', name=interval, hovertemplate=unit + " = <b>" + interval + "</b><br>Trade Date = <b>%{x}</b><br>" +
                                                        ' Average {} {}'.format(price_absolute, data_type)
                                                        + " = <b>%{y:.2f}</b><extra></extra>"), row=1, col=1)

                else:
                    plot.add_trace(go.Scatter(x=pd.unique(intervalData['Trade Month']), y=pd.unique(intervalData['Month Average']), mode='lines', name=interval, hovertemplate=unit + " = <b>" + interval + "</b><br>Trade Date = <b>%{x}</b><br>" +
                                                        ' Average {} {}'.format(price_absolute, data_type)
                                                        + " = <b>%{y:.2f}</b><extra></extra>"), row=1, col=1)

        else:
            if price_absolute == 'D-o-D Change':
                for interval in cDate:
                    intervalData = daterangeData[daterangeData[unit] == interval]
                    diffs = np.diff(intervalData['Absolute'])
                    plot.add_trace(go.Scatter(x=intervalData['TRADEDATE'], y=diffs, mode='lines', name=interval, hovertemplate=unit + " = <b>" + interval + "</b><br>Trade Date = <b>%{x}</b><br>" +
                                                        ' Average {} {}'.format(price_absolute, data_type)
                                                        + " = <b>%{y:.2f}</b><extra></extra>"), row=1, col=1)
            else:
                for interval in cDate:
                    intervalData = daterangeData[daterangeData[unit] == interval]

                    plot.add_trace(go.Scatter(x=intervalData['TRADEDATE'], y=intervalData[price_absolute], mode='lines', name=interval, hovertemplate=unit + " = <b>" + interval + "</b><br>Trade Date = <b>%{x}</b><br>" +
                                                        ' Average {} {}'.format(price_absolute, data_type)
                                                        + " = <b>%{y:.2f}</b><extra></extra>"), row=1, col=1)

        age, lastRefresh, ageColor = fileAge(str(data_type))
        plot.update_layout(title=dict(text='Last Data Refresh: '+str(lastRefresh)+'<br>Age: '+str(age), x=1),
            title_font_color=ageColor,
                font_family='Helvetica',
                hoverlabel=dict(bgcolor='white', font_size=16),
                height=600,
                yaxis=dict(title=ytitle),
                xaxis = dict(title='Trade Day', range = [sDate, eDate],
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                    label="1m",
                                    step="month",
                                    stepmode="backward", ),
                            dict(count=6,
                                    label="6m",
                                    step="month",
                                    stepmode="backward"),
                            dict(count=1,
                                    label="YTD",
                                    step="year",
                                    stepmode="todate"),
                            dict(count=1,
                                    label="1y",
                                    step="year",
                                    stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(
                        visible=True,
                    ),
                    tickformat=xtickformat,
                )
            )



        return plot


for figure, price in zip(['-2', '-4', '-6'],['price-gas-data-type-dropdown-linegraph', 'price-oil-data-type-dropdown-linegraph','price-freight-data-type-dropdown-linegraph']):
    @app.callback(
        Output(f'line-graph{figure}', 'figure'),

        Input(f'yoy-date-picker-range', 'start_date'),
        Input(f'yoy-date-picker-range', 'end_date'),
        Input(f'yoy-date-picker', 'value'),
        Input(f'price-absolute-dropdown-yoy', 'value'),
        Input(f'{price}', 'value'),


    )

    def YoYChange(sDate, eDate, cDate, price_absolute, data_type_yoy):
            plot = make_subplots()
            plot.data=[]

            data = dataProc.fetchData(fileDict[data_type_yoy])
            if data_type_yoy in ['Pacific174', 'Pacific155', 'Pacific138', 'Atlantic174', 'Atlantic155', 'Atlantic138']:
                data['Absolute'] = [np.round(x/1000, 1) for x in data['Absolute']]
                ytitle = price_absolute+str(10)+' (\N{SUPERSCRIPT THREE}) ($/day)'
            elif data_type_yoy in ['TAC FE', 'TAC EU', 'TAC ATL', 'TAC ME', 'TTF', 'HH', 'NBP', 'PSV', 'AOC', 'JKM']:
                ytitle = price_absolute+'( $/mmbtu)'
            elif data_type_yoy in ['FO', 'GO', 'Ice Brent']:
                ytitle = price_absolute+' (%/bbl)'

            daterangeData = data[data['TRADEDATE'] <= eDate]
            daterangeData = daterangeData[daterangeData['TRADEDATE'] >= sDate]
            xtickformat='%d-%b'


            daterangeData['Year'] = list(map(lambda x:x.strftime('%Y'),daterangeData['TRADEDATE']))


            tic2 = time.time()
            for year in cDate:
                try:
                    yearData = daterangeData[daterangeData['Year'] == year]
                    yearData = yearData[yearData['Absolute'].notna()]
                    yearData.index = range(len(yearData))
                    def findFirstContract(date):
                        idx = yearData[yearData['TRADEDATE']==date].first_valid_index()
                        ContractDate = (yearData['Trade Date'].iloc[idx])
                        ContractPrice = (yearData['Absolute'].iloc[idx])
                        return (ContractDate, ContractPrice)

                    datePricePairs = list(map(findFirstContract, list(np.unique(yearData['TRADEDATE']))))
                    dates = [d[0] for d in datePricePairs]
                    prices = [d[1] for d in datePricePairs]

                    dates = pd.to_datetime(dates,format='%d-%b-%y')

                    dates, prices = zip(*sorted(zip(dates, prices)))
                    dates = [pd.to_datetime(d.strftime('%d-%b'),format='%d-%b') for d in dates]
                    if price_absolute == 'D-o-D Change':
                                diffs = np.diff(prices)
                                plot.add_trace(go.Scatter(x=dates, y=diffs, mode='lines', name=year,meta=year, xhoverformat="%d-%b", hovertemplate="</b><br>Year = <b>%{meta}</b><br>" +"Trade Date = <b>%{x}</b><br>" +
                                                                    ' {} {}'.format(price_absolute, data_type_yoy)
                                                                    + " = <b>%{y:.2f}</b><extra></extra>"))

                    else:
                        plot.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=year,meta=year, xhoverformat="%d-%b", hovertemplate="</b><br>Year = <b>%{meta}</b><br>" +"Trade Date = <b>%{x}</b><br>" +
                                                                    ' {} {}'.format(price_absolute, data_type_yoy)
                                                                    + " = <b>%{y:.2f}</b><extra></extra>"))
                except:
                    pass
            sTick = pd.to_datetime(sDate,format='%Y-%m-%d %H:%M:%S')
            eTick = pd.to_datetime(eDate,format='%Y-%m-%d %H:%M:%S')
            age, lastRefresh, ageColor = fileAge(str(data_type_yoy))
            plot.update_layout(title=dict(text='Last Data Refresh: '+str(lastRefresh)+'<br>Age: '+str(age), x=1),
                title_font_color=ageColor,
                font_family='Helvetica',
                hoverlabel=dict(bgcolor='white', font_size=16),
                legend={"title": 'Years'},
                height=600,
                yaxis=dict(title=ytitle),
                xaxis = dict(title='Trade Day', range = [sTick.strftime('%d-%b'), eTick.strftime('%d-%b')],
                rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                    label="1m",
                                    step="month",
                                    stepmode="backward", ),
                            dict(count=6,
                                    label="6m",
                                    step="month",
                                    stepmode="backward"),
                            dict(count=1,
                                    label="YTD",
                                    step="year",
                                    stepmode="todate"),
                            dict(count=1,
                                    label="1y",
                                    step="year",
                                    stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                rangeslider=dict(
                        visible=True,
                    ),  tickformat=xtickformat )
                )

            return plot
