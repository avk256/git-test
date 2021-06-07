import sys
### change to the current script folder
sys.path.insert(0, 'E:\\Work\\aspirantura\\kafedra\\upwork\\RtoP\\PyModels\\LinearRegression')

import base64
import io
import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

from R2P_linregr import linear_regression, NLG


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.DataFrame()
columns = []

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

########### UI settings using html components from dash_html_components
# and widgets from dash_core_components

app.layout = html.Div([
## head 'Linear regression model'
        html.H1(
        children='Linear regression model',
        style={
            'textAlign': 'center',
            'color': '#7FDBFF'}
        ),
## file upload component
        dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': '',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
# Allow multiple files to be uploaded
        multiple= False
    ),
## show uploaded file name    
    html.Div(id='filename',style={'margin': '10px'}), 

## dropdown widget for selecting xValues    
    html.Label('Select xValues'),
    dcc.Dropdown(
        id='xValues',
        options = [{'label': '', 'value': ''}],
        multi=True
        
    ),

## dropdown widget for selecting yValue
    html.Label('Select yValue'),
    dcc.Dropdown(
        id='yValue',
        options = [{'label': '', 'value': ''}],
        
    ),

# Output from the model: corr_val1, corr_val2, corr_val3, var_val, quantile_val
  
    html.Div([
        html.Button(id='model-button', children='Create model'),
        html.Div(id='corr_val1'),
        html.Div(id='corr_val2'),
        html.Div(id='corr_val3'),
        html.Div(id='var_val'),
        html.Div(id='quantile_val'),
        html.Div(id='glm_r2'),
        html.Div(id='glm_rmse')
    ],style={'textAlign': 'center','margin': '40px'})

])

"""
 Method for reading csv and xls files 
 
 input:
     contents - file content from upload widget
     filename - filename from upload widget
 output:
     saved dataframe in global variable
     list of dataset columns 

"""
def parse_contents(contents, filename):
    print('parse_contents')
    content_type, content_string = contents.split(',')
    
    global df
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file

            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)


    return list(df.columns)


"""
 Callback method for updating xValues - list of the features 
 from uploaded file   
 
 input:
     contents - file content from upload widget
     filename - filename from upload widget
 output:
     xValues', 'options' - list of elements for dropdown widget
     name of the uploaded file 

"""
@app.callback([Output('xValues', 'options'),
               Output('filename', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])

def update_output(list_of_contents, list_of_names):
    print('update_output')
    if list_of_contents is not None:
        
        cols = parse_contents(list_of_contents, list_of_names)
        global columns 
        columns = cols.copy()
#        print(cols)
        cols_list = [{'label': i, 'value': i} for i in cols]
#        print(cols_list)
        return cols_list, 'Processing file '+ str(list_of_names)
    else:
        return [{'label': '', 'value': ''}], ''

"""
 Callback method for updating yValue - predicted feature. 
 It excludes selected features like xValues from the list of available   
 
 input:
     'xValues', 'value' - selected features
     
 output:
     'yValue', 'options' - list of elements for dropdown widget 

"""
@app.callback(
    Output('yValue', 'options'),
    [Input('xValues', 'value')])

def update_yValue(xValues):
    if xValues is not None:
#        print(xValues)
        yValue = list(set(columns)-set(xValues))
        y_list = [{'label': i, 'value': i} for i in yValue]
#        print(columns)
        return y_list 
    else:
        return [{'label': '', 'value': ''}]

"""
 Callback method for rendering model results. It calls methods from other developed modules 
 It excludes selected features like xValues from the list of available   
 
 input:
     'model-button', 'n_clicks' - if button pressed
     'xValues', 'value' - selected predictors
     'yValue', 'value' - selected response    
     
 output:
     'corr_val1', 'children' - model text description
     'corr_val2', 'children' - model text description
     'corr_val3', 'children' - model text description
     'var_val', 'children' - model text description
     'quantile_val', 'children' - model text description
"""
@app.callback([Output('corr_val1', 'children'),
               Output('corr_val2', 'children'),
               Output('corr_val3', 'children'),
               Output('var_val', 'children'),
               Output('quantile_val', 'children'),
               Output('glm_r2','children'),
               Output('glm_rmse','children')],
              [Input('model-button', 'n_clicks')],
              [State('xValues', 'value'),
               State('yValue', 'value')])

def linregr(n_clicks, xValues, yValue):
    if xValues is not None:

        columnsArray = '[{"columnDisplayName":"S@#@#no","tableDisplayType":"string","columnName":"S#@#@no"},{"columnDisplayName":"Region","tableDisplayType":"string","columnName":"Region"},{"columnDisplayName":"Country","tableDisplayType":"string","columnName":"Country"},{"columnDisplayName":"Item Type","tableDisplayType":"string","columnName":"Item Type"},{"columnDisplayName":"Sales Channel","tableDisplayType":"string","columnName":"Sales Channel"},{"columnDisplayName":"Order Priority","tableDisplayType":"string","columnName":"Order Priority"},{"columnDisplayName":"Order Date","tableDisplayType":"string","columnName":"Order Date"},{"columnDisplayName":"Order ID","tableDisplayType":"string","columnName":"Order ID"},{"columnDisplayName":"Ship Date","tableDisplayType":"string","columnName":"Ship Date"},{"columnDisplayName":"Units Sold","tableDisplayType":"number","columnName":"Units Sold"},{"columnDisplayName":"Unit Price","tableDisplayType":"number","columnName":"Unit Price"},{"columnDisplayName":"Unit Cost","tableDisplayType":"number","columnName":"Unit Cost"},{"columnDisplayName":"Total Revenue","tableDisplayType":"number","columnName":"Total Revenue"},{"columnDisplayName":"Total Cost","tableDisplayType":"number","columnName":"Total Cost"},{"columnDisplayName":"Total Profit","tableDisplayType":"number","columnName":"Total Profit"}]'    

        try:
            columnsArray = json.loads(columnsArray)
        except:
            print('json format not valid')
        print('###################### data for regression #####################')
        global df  
        print(df.head())
        print('###################### xValues #####################') 
        print(xValues)
        print('###################### yValue #####################') 
        print(yValue)

        linear_regr = linear_regression(yValue=yValue,xValues=xValues,columnsArray=columnsArray, data=df)
    
        output = NLG(linear_regr, yValue=yValue,xValues=xValues)
        
        return output[0], output[1], output[2], output[3], output[4], "GLM model R^2 coeff is "+ str(linear_regr[2]), "GLM model RMSE coeff is " + str(linear_regr[3]) 
    else:
        return '', '', '', '', '', '', ''
        
    


if __name__ == '__main__':
    app.run_server(debug=True)


