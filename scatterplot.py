#Import packages
import pandas as pd
import plotly.express as px
from dash import Dash,dcc,html,callback,Input,Output,no_update #register_page

#register_page(__name__,path="/charts",name="Charts")

app = Dash(__name__) 
'''
since it is a multi-page dashboard, we do not need to initialize
dash with app=Dash()
'''

#import dataset
'''
pulling the dataset directly from github using a URL
'''
country_url = "https://raw.githubusercontent.com/VizualOptima/Datasets/main/data_.xlsx" 
region_url =  "https://raw.githubusercontent.com/VizualOptima/Datasets/main/Region.xlsx"

# reading the datasets as dataframe using pandas
df_country = pd.read_excel(country_url)
df_region = pd.read_excel(region_url)

#clean dataset by fixing country names and removing aggregate regions
'''
some country names from the world bank have a particular spelling. eg : (Bahamas, The) instead of Bahamas
the full code can be found here : https://github.com/VizualOptima/world_bank_data_cleanup/blob/main/Data_Cleanup.py
'''

df_country['Country Name']= df_country['Country Name'].replace({'Bahamas, The': 'Bahamas', 'Congo, Dem. Rep.' : 'Democratic Republic of Congo','Congo, Rep.':'Republic of Congo',
'Egypt, Arab Rep.':'Egypt','Micronesia, Fed. Sts.':'Micronesia','Gambia, The':'Gambia','Hong Kong SAR, China':'Hong Kong',
'Iran, Islamic Rep.':'Iran','Kyrgyz Republic':'Kyrgyzstan','Korea, Rep.':'South Korea','Lao PDR':'Laos','Macao SAR, China':'Macao',
'St. Martin (French part)':'Saint Martin','Korea, Dem. People*':'North Korea','Russian Federation':'Russia','Sint Maarten (Dutch part)':'Sint Maarten',
'Syrian Arab Republic':'Syria','Turkiye':'Turkey','Venezuela, RB':'Venezuela','Virgin Islands (U.S.)':'Virgin Islands',
'Yemen, Rep.':'Yemen'})
df_country

#merging both datasets to create one data set 
df = pd.merge(df_country,df_region,how='left',on='Country Code')

#filter years from 1980 - 2023
'''
filtered the years from 2000 to 2023. Years go back all the way to 1980.
'''
df = df[(df['Year']>=1980)&(df['Year']<=2023)]

'''
Below are the dropdown options . This is for the income group and region filters
'''
#Dropdown of unique IncomeGroup values
'''
To create a multi-select dropdown of income group, create
a dataframe that only show unique values from the IncomeGroup Column. This code
can be refactored for future multi-select options.
'''
income_group =[{'label': group, 'value': group} for group in sorted(df['IncomeGroup'].dropna().unique())]

#Dropdown of unique Region values
'''
To create a multi-select dropdown of different regions 
'''
region_dropdown = [{'label':region, 'value':region} for region in sorted(df['Region'].dropna().unique())]

'''
column pick allows the user to pick any column from the dataset 
'''

df_filtered = df.drop(columns=['Country Name', 'Region', 'IncomeGroup', 'Year'])
column_pick = df_filtered.columns

'''
create dropdown options based on all the columns of the dataset
'''

dropdown_options = [{'label':col, 'value':col} for col in column_pick]

# Dataframe for time series analysis
df_time = pd.melt(df,
                  id_vars=['Country Name', 'Year'],
                  value_vars=column_pick,
                  var_name='Indicator Name',
                  value_name='Value')

'''
Below is the Dash application layout.
html.H1 : is the title of the application, aligned center
html.Div : is a container with the a text field explaining what is in the application, aligned center
html.Br() : this is for line break vertical spacing
html.Div : is a container aligned to the right, that contains the income group filter including the label
dcc.Graph : is to call the barchart fig (see code above)
'''
#Create a color container
colors = {
    'background': '#f8f9fa',        
    'container': '#ffffff',         
    'header': '#154360',            
    'text': '#212529',              
    'accent': '#0d6efd'
}

#Dash application layout
app.layout = html.Div([
    # Application title aligned center
    html.H1(
        children='Country Indicators Scatterplot',
        style={'textAlign': 'center','color':colors['header'],'paddingTop':'5px','marginBottom':'0px','fontFamily':'Arial, sans-serif','fontSize':'50px'}
    ),

    html.Div("Explore country indicators and development trends by regions, and income groups from 1980 to 2023. " \
    "Use the filters to adjust the scatterplots and time series insights.", 
         style={
             'textAlign': 'center',
             'color': colors['text'],
             'marginBottom': '20px',
             'fontSize': '16px',
             'fontFamily': 'Aptos, sans-serif'
         }),
#----------------------------------------------------------------------------------------------------------------
    # Years slider
    # html.Div([
    #         html.Label('Select Year:', style={'color':'white','fontFamily':'Aptos, sans-serif','fontSize':'14px','fontWeight':'bold','marginBottom':'10px','display':'block'}),
    #         dcc.Slider(
    #             id='year-slider',
    #             min=df['Year'].min(),
    #             max=df['Year'].max(),
    #             value=df['Year'].min(),
    #             marks={str(year):{'label': str(year), 'style': {'fontSize': '14px', 'fontFamily': 'Aptos, sans-serif','color':'#d5dbdb'}}for year in df['Year'].unique()},
    #     tooltip={"placement": "bottom", "always_visible": True},
    #     step=None
    #         )
    #     ],style={'width': '90%','backgroundColor':'#154360',
    # 'borderRadius': '10px','margin': '20px auto','color':'#ecf0f1','padding': '15px 20px'}),
#-----------------------------------------------------------------------------------------------------------------
    #Container 1 : Regions ,Income Group and Country Filter
    html.Div([
            html.Div([
                html.Label('Region(s):',style={'fontFamily': 'Aptos, sans-serif','color':'#ffffff',
                'fontSize': '14px','marginBottom': '10px'}),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=region_dropdown,
                    multi=True,
                    placeholder="Select",
                )
        ], style={'width': '30%','justifyContent': 'space-between','backgroundColor':'#154360','boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                  'padding': '10px', 'borderRadius': '8px'}),

        html.Div([
            html.Label('Income Group(s):',style={'fontFamily': 'Aptos, sans-serif','color':'#ffffff',
            'fontSize': '14px','marginBottom': '10px'}),
            dcc.Dropdown(
                id='income-dropdown',
                options=income_group,
                multi=True,
                placeholder="Select",
            )
        ], style={'width': '30%','backgroundColor':'#154360','boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                  'padding': '10px', 'borderRadius': '8px'}),

        html.Div([
        html.Label('Country Name',style={'fontFamily': 'Aptos, sans-serif','color':'#ffffff',
            'fontSize': '14px','marginBottom': '10px'}),
        dcc.Dropdown(
            id="country-filter",
            placeholder="Select a Country",
    
        )
    ], style={'width': '30%','backgroundColor':'#154360','boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
              'padding': '10px', 'borderRadius': '8px'}),

    ], style={
        'display': 'flex',
        'gap':'2%',
        'justifyContent': 'space-between',
        'backgroundColor': colors['container'],
        'padding': '20px',
        'borderRadius': '10px',
        'margin': '20px auto',
        'width': '90%',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
    }),
    #---------------------------------------------------------------------------------------------------------------   
    #---------------------------------------------------------------------------------------------------------------
    # Container 2 : x-axis and y-axis selectors
    html.Div([
        html.Div([
            html.Label('X axis Indicator',style={'fontWeight':'bold'}),
            dcc.Dropdown(
                id='xaxis-column',
                options=dropdown_options,
                value= 'Life expectancy at birth, total (years)',
                style={'width': '100%', 'fontSize': '14px'}),
            
            dcc.RadioItems(
                ['Linear','Log'],'Linear',
                id='xaxis-type',
                inline=True,
                 style={'fontSize': '14px'}
            )
        ],style={'width': '48%', 'display': 'inline-block','verticalAlign': 'top'}),

        html.Div([
            html.Label('Y axis Indicator',style={'fontWeight':'bold'}),
            dcc.Dropdown(
                id='yaxis-column',
                options=dropdown_options,
                value= 'Population, total',
                style={'width': '100%', 'fontSize': '14px'}),
            
            dcc.RadioItems(
                ['Linear','Log'],'Linear',
                id='yaxis-type',
                inline=True,
                style={'fontSize': '14px'}
            )
        ],style={'width': '48%', 'display': 'inline-block','marginLeft': '4%','verticalAlign': 'top'})
], style={
    'display': 'flex',
        'justifyContent': 'space-between',
        'backgroundColor': colors['container'],
        'padding': '20px',
        'borderRadius': '10px',
        'margin': '20px auto',
        'width': '90%',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        }),
#--------------------------------------------------------------------------------
#Scatterplots
    html.Div([
        dcc.Graph(id='scatter-plot')
    ],style={
        'backgroundColor': colors['container'],
        'padding': '20px',
        'borderRadius': '10px',
        'margin': '20px auto',
        'width': '90%',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
}),

#X time-series and Y time-series

    html.Div([
        
        html.Div([
        dcc.Graph(id='x-time-series'),
    ], style={'width': '48%',
    'backgroundColor': colors['container'],
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),

        html.Div([
        dcc.Graph(id='y-time-series'),
    ], style={'width': '48%',
    'marginLeft': '4%',
    'backgroundColor': colors['container'],
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
    ],style={
    'display': 'flex',
    'justifyContent': 'space-between',
    'width': '92%',
    'margin': '20px auto'
})
    ],style={'minHeight':'100vh','fontFamily':'Aptos,sans-serif','fontSize':'14px','backgroundColor':colors['background']})
#--------------------------------------------------------------------------------------------------

#adding a callback for filters to be applied to the scatterplot
@callback([
    Output('scatter-plot','figure'),
    Output('country-filter', 'options'),
    Input('region-dropdown','value'),
    Input('income-dropdown','value'),
    Input('country-filter','value'),
    Input('xaxis-column','value'),
    Input('yaxis-column','value'),
    Input('xaxis-type','value'),
    Input('yaxis-type','value')
    ]
)

    
def update_graph(region_value,income_value,country_value,xaxis_column_name,yaxis_column_name,xaxis_type,
                  yaxis_type):
    # year_value):
    
    #indicator_df = df[df['Year']== year_value] <- only to use if year filter is activated
    indicator_df = df.copy()
    indicator_df = indicator_df.dropna(subset=['Population, total'])  # remove rows with NaN in size column
     # Apply filters
    if region_value:
        indicator_df = indicator_df[indicator_df['Region'].isin(region_value)]
    if income_value:
        indicator_df = indicator_df[indicator_df['IncomeGroup'].isin(income_value)]
    if country_value:
        indicator_df = indicator_df[indicator_df['Country Name']==country_value]

    fig4 = px.scatter(indicator_df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        hover_name='Country Name',
        color='Region',
        size='Population, total',)

    

    fig4.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')

    fig4.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')
    fig4.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    countries = [{'label': c, 'value': c} for c in sorted(indicator_df['Country Name'].unique())]
    
    return fig4,countries

def create_time_series(indicator_df, axis_type, title):
    fig = px.line(indicator_df, x='Year', y='Value', markers=True)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

# X time-series on hover
@app.callback(
    Output('x-time-series', 'figure'),
    Input('scatter-plot', 'hoverData'),
    Input('xaxis-column', 'value'),
    Input('xaxis-type', 'value')
)
def update_x_timeseries(hoverData, xaxis_column_name, axis_type):
    if hoverData is None:
        return {}
    country_name = hoverData['points'][0]['hovertext']
    dff = df_time[(df_time['Country Name'] == country_name) &
                  (df_time['Indicator Name'] == xaxis_column_name)]
    title = f"<b>{country_name}</b><br>{xaxis_column_name}"
    return create_time_series(dff, axis_type, title)

# Y time-series on hover
@app.callback(
    Output('y-time-series', 'figure'),
    Input('scatter-plot', 'hoverData'),
    Input('yaxis-column', 'value'),
    Input('yaxis-type', 'value')
)
def update_y_timeseries(hoverData, yaxis_column_name, axis_type):
    if hoverData is None:
        return {}
    country_name = hoverData['points'][0]['hovertext']
    dff = df_time[(df_time['Country Name'] == country_name) &
                  (df_time['Indicator Name'] == yaxis_column_name)]
    title = f"<b>{country_name}</b><br>{yaxis_column_name}"
    return create_time_series(dff, axis_type, title)

if __name__ == '__main__':
    app.run(debug=True)
