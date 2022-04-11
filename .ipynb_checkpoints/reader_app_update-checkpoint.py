import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output, State
from surgeon_recording.reader import Reader
from os.path import join
import cv2
import base64
import time


# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = False

reader = Reader()
data_folder = 'data'

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='three columns div-user-controls',
                             children=[
                                 html.H2('DATA VISUALISATION APP'),
                                 html.P('Experiment data selection'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                        dcc.Dropdown(id='exp_folder',
                                                     options=[{'label': key, 'value': path} for key, 
                                                              path in reader.get_experiment_list(data_folder).items()]),
                                        dcc.Interval(id='auto-stepper',
                                                    interval=300, # in milliseconds
                                                    n_intervals=0
                                        ),
                                        ### Those are the data that we save at the user's browser's session :
                                         
                                        dcc.Store(id='selected_exp'),
                                        dcc.Store(id='start_index'),
                                        dcc.Store(id='stop_index'),
                                        dcc.Store(id='selected_frame'),

                                        dcc.Store(id='selected_emg_frame'),
                                        dcc.Store(id='emg_start_index'),
                                        dcc.Store(id='emg_stop_index'),

                                        dcc.Store(id='selected_opt_frame'),
                                        dcc.Store(id='opt_start_index'),
                                        dcc.Store(id='opt_stop_index'),

                                        dcc.Store(id='selected_tps_frame'),
                                        dcc.Store(id='tps_start_index'),
                                        dcc.Store(id='tps_stop_index'),

                                        dcc.Store(id='max_interval'),
                                        dcc.Store(id='max_cut_interval'),

                                        dcc.Store(id='window_size', data=2000)
                                     ],
                                     style={'color': '#1E1E1E'}),
                                 html.P('Playback speed selection'),
                                 dcc.Slider(
                                    id="speed_selector",
                                    min=0,
                                    max=2,
                                    step=0.1,
                                    value=0,
                                    marks={
                                        0: {'label': '0', 'style': {'color': 'rgb(200, 200, 255)'}},
                                        0.5: {'label': '0.5', 'style': {'color': 'rgb(200, 200, 255)'}},
                                        1: {'label': '1','style': {'color': 'rgb(200, 200, 255)'}},
                                        1.5: {'label': '1.5', 'style': {'color': 'rgb(200, 200, 255)'}},
                                        2: {'label': '2','style': {'color': 'rgb(200, 200, 255)'}}
                                    },
                                  ),
                                 html.Div(
                                     className="buttons-bar",
                                     children=[
                                      html.P('Export'),
                                      dcc.Input(id="export_folder", type="text", placeholder=""),
                                      html.Button('Export', id='btn-export', n_clicks=0),
                                      html.Div(id='output_text'),
                                      ],
                                      style={'padding-bottom': 35}
                                  ),
                                ],
                            ),
                    html.Div(className='nine columns div-for-charts bg-grey',
                               children=[
                                html.H4('The camera visualisation of our data:'),
                                html.Div(className='images',
                                         children=[ 
                                             html.Div([
                                             html.P('Start: '),
                                             html.Img(id='rgb_image', height="480", width="640")
                                             ], style={'width': '48%', 'margin-left': '10px', 'display': 'inline-block', 'padding': '10 20'}),
                                             html.Div([
                                             html.P('End: '),
                                             html.Img(id='rgb_image_1', height="480", width="640")
                                             ], style={'width': '48%','margin-left': '10px', 'display': 'inline-block', 'padding': '10 20'}),    
                                                 
                                                ],),
                                   
                                html.Div(className= 'slider',
                                         children = [
                                             
                                             html.P('Time sequence selection'),
                                             dcc.RangeSlider(
                                                  id="slider_frame",
                                                  min=0,
                                                  max=100,
                                                  step=0.01,
                                                  value=[0.,100.], allowCross=False,
                                                  marks={
                                                      0: {'label': '0', 'style': {'color': 'rgb(200, 200, 255)'}},
                                                      25: {'label': '25','style': {'color': 'rgb(200, 200, 255)'}},
                                                      50: {'label': '50', 'style': {'color': 'rgb(200, 200, 255)'}},
                                                      75: {'label': '75','style': {'color': 'rgb(200, 200, 255)'}},
                                                      100: {'label': '100', 'style': {'color': 'rgb(200, 200, 255)'}}
                                                  }),]),
                                html.Div(className='graphs',
                                         children=[
                                             html.H4('Useful graph representations:'),
                                             dcc.Graph(id='timeseries', config={'displayModeBar': False}, 
                                                             animate=False,  style={'margin-left': '10px', 'margin-bottom':'10px'}),
                                             html.Div([
                                             dcc.Graph(id='opt',config={'displayModeBar': True, 
                                                                       'autosizable': True},animate=False)
                                             ], style={'width': '48%', 'margin-left': '10px', 'display': 'inline-block', 'padding': '10 20'}),
                                             html.Div([
                                             dcc.Graph(id='tps',config={'displayModeBar': False, 'autosizable': True}, 
                                                     animate=False)
                                             ], style={'width': '48%','margin-left': '10px', 'display': 'inline-block', 'padding': '10 20'}),
                                             
                                           
                                         
                                         ],                                        
                                         ),
                               ],
                               )
                 ])
        ]

)



## This callback function is very useful to export the specific segment in the folders :

@app.callback(Output('selected_exp', 'data'),
              [Input('exp_folder', 'value')])
def update_exp(path):
    if path is None:
        return
    reader.play(path)
    return True


@app.callback(Output('output_text', 'children'),
              [Input('btn-export', 'n_clicks')],
              [State('export_folder', 'value'),
               State('start_index', 'data'),
               State('stop_index', 'data'),
               State('emg_start_index', 'data'),
               State('emg_stop_index', 'data'),
               State('opt_start_index', 'data'),
               State('opt_stop_index', 'data'),
               State('tps_start_index', 'data'),
               State('tps_stop_index', 'data'),
               State('selected_exp', 'data')])
def export(n_clicks, value, start_index, stop_index,
           emg_start_index, emg_stop_index,
           opt_start_index, opt_stop_index,
           tps_start_index, tps_stop_index,
           selected_exp):
    if selected_exp is None:
        return 'No data folder selected'
    if value is None:
        return 'Empty folder specified, please enter a valid name'
    sensor_indexes = {}
    sensor_indexes["camera"] = [start_index, stop_index]
    sensor_indexes["emg"] = [emg_start_index, emg_stop_index]
    sensor_indexes["optitrack"] = [opt_start_index, opt_stop_index]
    sensor_indexes["tps"] = [tps_start_index, tps_stop_index]
    reader.export(value, sensor_indexes)
    return 'Sequence exported to {} folder'.format(value)


@app.callback([Output('start_index', 'data'),
               Output('stop_index', 'data'),
               Output('emg_start_index', 'data'),
               Output('emg_stop_index', 'data'),
               Output('opt_start_index', 'data'),
               Output('opt_stop_index', 'data'),
               Output('tps_start_index', 'data'),
               Output('tps_stop_index', 'data'),
               Output('auto-stepper', 'n_intervals'),
               Output('max_interval', 'data'),
               Output('max_cut_interval', 'data'),
               Output('auto-stepper', 'disabled'),],
              [Input('slider_frame', 'value'),
               Input('selected_exp', 'data'),
               Input('speed_selector', 'value')],
               [State('auto-stepper', 'interval')]
               )
def select_frame(selected_percentage, selected_exp,  speed, interval):
    if selected_exp is None:
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, True
    start_index = int(selected_percentage[0] / 100 * (reader.get_nb_frames() - 1))
    stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_frames() - 1))

    emg_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_sensor_frames("emg") - 1))
    emg_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_sensor_frames("emg") - 1))
    opt_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
    opt_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
    tps_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_sensor_frames("tps") - 1))
    tps_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_sensor_frames("tps") - 1))

    total_time= reader.data["camera"].iloc[-1,1] - reader.data["camera"].iloc[0,1]
    total_cut_time= reader.data["camera"].iloc[stop_index,1] - reader.data["camera"].iloc[start_index,1]


    if speed==0:
        disabled=True
        max_interval=1
        max_cut_interval=1
    else :
        disabled=False
        max_interval=total_time/(interval/1000)/speed
        max_cut_interval=total_cut_time/(interval/1000)/speed

    return start_index, stop_index, emg_start_index, emg_stop_index, opt_start_index, opt_stop_index, tps_start_index, tps_stop_index, 0, max_interval, max_cut_interval, disabled


@app.callback([Output('selected_frame', 'data'),
               Output('selected_emg_frame', 'data'),
               Output('selected_opt_frame', 'data'),
               Output('selected_tps_frame', 'data')],
              [Input('auto-stepper', 'n_intervals'),
               Input('slider_frame', 'value'),                      
               Input('max_interval', 'data'),
               Input('max_cut_interval', 'data'),
               Input('selected_exp', 'data') ],
              [
               State('speed_selector', 'value')])
def on_click(n_intervals, limits, max_interval, max_cut_interval,  selected_exp, speed):
    if selected_exp is None:
        return 0, 0 ,0, 0
    idx=n_intervals%int(max_cut_interval)
    selected_percentage = (idx/max_interval*100) + limits[0]
    selected_frame = int(selected_percentage / 100 * (reader.get_nb_frames() - 1))
    selected_emg_frame = int(selected_percentage / 100 * (reader.get_nb_sensor_frames("emg") - 1))
    selected_opt_frame = int(selected_percentage / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
    selected_tps_frame = int(selected_percentage / 100 * (reader.get_nb_sensor_frames("tps") - 1))
 
    return selected_frame, selected_emg_frame, selected_opt_frame, selected_tps_frame


@app.callback(Output('rgb_image', 'src'),
              [Input('selected_frame', 'data')],
              [State('selected_exp', 'data')])
def update_rgb_image_src(selected_frame, selected_exp):
    if selected_exp is None:
        return
    if selected_frame > reader.get_nb_frames():
        return
    image = reader.get_image("rgb", selected_frame)
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())


# Callback for timeseries price,  this is for the EMG Graph
@app.callback(Output('timeseries', 'figure'),
              [Input('selected_emg_frame', 'data'),
               Input('emg_start_index', 'data'),
               Input('emg_stop_index', 'data')],
              [State('selected_exp', 'data')])
def emg_graph(selected_frame, emg_start_index, emg_stop_index, selected_exp):
 
    if selected_exp is None:
        return go.Figure()
    figure = go.Figure()
    nb_measures=len(reader.data["emg"])
    data_divider=int(nb_measures/500)

    if data_divider==0:
        data_divider=1
    data_fraction=reader.data["emg"][0:-1:data_divider]
    
    emg_labels = ["channel " + str(i) for i in range(len(reader.data["emg"].columns) - 3)]

    for i, emg in enumerate(emg_labels):
         figure.add_trace(go.Scatter(x=data_fraction["relative_time"],
                                 y=data_fraction["emg" + str(i)],
                                 mode='lines',
                                 opacity=0.7,
                                 name=emg,
                                 textposition='bottom center'))
         
    time = reader.data["emg"].iloc[selected_frame, 2]

    #  =>2 pour exclure les deux premiere colones
    y_max=data_fraction.iloc[:,3:].max().max()
    y_min=data_fraction.iloc[:,3:].min().min()

    x_min=data_fraction.iloc[0, 2]
    x_max=data_fraction.iloc[-1, 2]
    figure.add_trace(go.Scatter(x=[time, time],
                             y=[y_min, y_max],
                             mode='lines',
                             opacity=0.7,
                             name="current frame",
                             textposition='bottom center',
                             line=dict(                             
                              width=5),
                             ))

    #this is for the selction rectangle
    x_start=reader.data["emg"].iloc[emg_start_index, 2]
    x_end=reader.data["emg"].iloc[emg_stop_index, 2]

    figure.add_trace(go.Bar(x=[(x_end+x_start)/2.],
                            y=[y_max-y_min],
                            base=y_min,
                            width= x_end-x_start,# customize width here
                            opacity=0.3,
                            marker_color='rgb(100, 118, 255)',
                            showlegend=False
                            ))
    
    figure.update_layout(
          colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
          template='plotly_dark',
          paper_bgcolor='rgba(0, 0, 10, 0.3)',
          plot_bgcolor='rgba(0, 0, 0, 0)',
          margin={'b': 15},
          hovermode='x',
          autosize=True,
          title={'text': 'EMG signals', 'font': {'color': 'white'}, 'x': 0.5},
          xaxis={'range': [x_min, x_max]},
          yaxis={'range': [y_min, y_max], 'nticks': 10},
          uirevision='true',
    )
    return figure


#Callback for opt price
@app.callback(Output('opt', 'figure'),
              [Input('selected_opt_frame', 'data')],
              [State('selected_exp', 'data')])
def opt_graph(selected_frame, selected_exp):

    if selected_exp is None:
        return go.Figure()
    range_frame=75
    opt_data = reader.data['optitrack'][selected_frame-range_frame:selected_frame+range_frame:(int(range_frame/5))]
   
    header=list(opt_data.columns)[3:]
    nb_frames=int(len(header)/7)
    names=[]

    for i in range(nb_frames):
        names.append(header[i*7].replace('_x', ''))
    
    opt_labels = ["channel " + str(i) for i in range (0, nb_frames)]

    fig = go.Figure()
    for i, opt in enumerate(opt_labels):
        multiplier0=str(100+i*50)
        multiplier1=str(118+i*30)
        multiplier2=str(255-i*50) 

          #history frame  add 
        fig.add_trace(go.Scatter3d(
            x=opt_data[names[i]+"_x"], y=opt_data[names[i]+"_y"], z=opt_data[names[i]+"_z"],
            name='history '+opt,
            mode='markers',
            showlegend = True,
            marker_color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, .8)',
             
            marker=dict(
                size=np.linspace(3,12,10), 
                opacity=0.5)
         ))

      #current frame
        fig.add_trace(go.Scatter3d(
            x=[reader.data['optitrack'][names[i]+"_x"].iloc[selected_frame]],
            y=[reader.data['optitrack'][names[i]+"_y"].iloc[selected_frame]],
            z=[reader.data['optitrack'][names[i]+"_z"].iloc[selected_frame]],
            name="current "+opt,
            mode='markers',
            showlegend = True,
            marker_color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)',
        
            marker=dict(
                size=13,
                opacity=0.9)
         ))

    max_x = [0] * nb_frames
    max_y = [0] * nb_frames
    max_z = [0] * nb_frames
    min_x = [0] * nb_frames
    min_y = [0] * nb_frames
    min_z = [0] * nb_frames

    for i in range (0,nb_frames):
        max_x[i] = max(reader.data['optitrack'][names[i]+"_x"])
        max_y[i] = max(reader.data['optitrack'][names[i]+"_y"])
        max_z[i] = max(reader.data['optitrack'][names[i]+"_z"])

        min_x[i] = min(reader.data['optitrack'][names[i]+"_x"])
        min_y[i] = min(reader.data['optitrack'][names[i]+"_y"])
        min_z[i] = min(reader.data['optitrack'][names[i]+"_z"])

    fig.update_layout(
                        scene = dict(
                         xaxis = dict(

                               backgroundcolor="rgb(200, 200, 230)",
                               gridcolor="white",
                               showbackground=True,
                               zerolinecolor="white",
                               nticks=10,
                               range=[min(min_x)-abs(0.1*min(min_x)),max(max_x)+0.1*max(max_x)]),
                          yaxis = dict(
                              
                              backgroundcolor="rgb(230, 200,230)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              nticks=10,
                              range=[min(min_y)-abs(0.1*min(min_y)),max(max_y)+0.1*max(max_y)]),
                          zaxis = dict(
                             
                              backgroundcolor="rgb(230, 230,200)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              nticks=10,
                              range=[min(min_z)-abs(0.1*min(min_z)),max(max_z)+0.1*max(max_z)]),
                         
                          xaxis_title='X AXIS ',
                          yaxis_title='Y AXIS ',
                          zaxis_title='Z AXIS '),
                        #autosize=True,
                        width=600,

                        margin=dict(r=0, b=10, l=0, t=80),
                        title={'text': 'Optitrack signals', 'font': {'color': 'white'}, 'x': 0.5},
                        hovermode='x',
                        paper_bgcolor='rgba(0, 0, 10, 0)',
                        template='plotly_dark',
                        scene_aspectmode='cube',
                        uirevision='true',
                        
                      )
    return fig


#Callback for tps price
@app.callback(Output('tps', 'figure'),
              [Input('selected_tps_frame', 'data')],
              [State('selected_exp', 'data')])
def tps_graph(selected_frame, selected_exp):
    if selected_exp is None:
        return go.Figure()

    frame_df=reader.data['tps'].iloc[selected_frame,3:]
    header=list(reader.data['tps'].columns)[3:]   

    fig = go.Figure( [go.Bar(x=header, 
                             y=frame_df,
                             marker_color='rgb(100, 118, 255)',
                             opacity=0.3,
                             textposition='auto',   )])

    y_max=reader.data['tps'].iloc[:,2:].max().max()

    fig.update_layout(
       
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Y axis',
            titlefont_size=16,
            tickfont_size=14,
            range=[0,y_max],
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
       
        bargap=0.15, # gap between bars of adjacent location coordinates.
        template='plotly_dark',
        paper_bgcolor='rgba(150, 150 , 200, 0.1)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode='x',
        autosize=True,
        title={'text': 'TPS signals', 'font': {'color': 'white'}, 'x': 0.5},
        uirevision='true',
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)