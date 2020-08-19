import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from surgeon_recording.recorder import Recorder
from os.path import join
import cv2
import base64
import time
import pyrealsense2 as rs

recorder = None

def intialize_recorder():
    return Recorder('data')

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='three columns div-user-controls',
                             children=[
                                 html.H2('SURGEON RECORDING APP'),
                                 html.P('Surgeon recording and visualization app'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                        dcc.Interval(id='emg-stepper',
                                                    interval=400, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                        dcc.Interval(id='image-stepper',
                                                    interval=200, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                     ],
                                     style={'color': '#1E1E1E'}),
                                 html.Div(
                                     className="buttons-bar",
                                     children=[
                                      dcc.Input(id="export_folder", type="text", placeholder=""),
                                      html.Button('Record', id='btn-record', n_clicks=0),
                                      html.Button('Stop', id='btn-stop', n_clicks=0),
                                      html.Div(id='output_text', children='Not recording')]
                                  ),
                                 html.Div(className='graphs',
                                         children=[dcc.Graph(id='tps',config={'displayModeBar': False, 'autosizable': True}, animate=False)])
                                ]
                             ),
                      html.Div(className='nine columns div-for-charts bg-grey',
                               children=[
                                html.Div(className='images',
                                         children=[html.Img(id='rgb_image', height="480", width="640", style={'display': 'inline-block'}),
                                                   dcc.Graph(id='opt',config={'displayModeBar': False}, animate=False, style={'display': 'inline-block'})]
                                ),
                                html.Div(className='graphs',
                                         children=[dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=False)])
                               ])
                 ])
        ]
)

@app.callback(Output('output_text', 'children'),
              [Input('btn-record', 'n_clicks'),
               Input('btn-stop', 'n_clicks')],
              [State('export_folder', 'value')])
def export(record_click, stop_click, value):
    if value is None:
        return 'Empty folder specified, please enter a valid name'
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-record' in changed_id:
        if not recorder.recording:
            recorder.record(value)
        return 'Recording in {} folder, press stop to stop recording'.format(value)
    elif 'btn-stop' in changed_id:
        recorder.stop_recording()
        return 'Recording finished, check {} folder'.format(value)
    return 'Not recording'

@app.callback(Output('rgb_image', 'src'),
              [Input('image-stepper', 'n_intervals')])
def update_rgb_image_src(step):
    image = recorder.get_buffered_rgb()
    encoded_image = base64.b64encode(image)
    return 'data:image/png;base64,{}'.format(encoded_image.decode())

@app.callback(Output('depth_image', 'src'),
              [Input('image-stepper', 'n_intervals')])
def update_depth_image_src(step):
    image = recorder.get_buffered_depth()
    encoded_image = base64.b64encode(image)
    return 'data:image/png;base64,{}'.format(encoded_image.decode())

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('emg-stepper', 'n_intervals')])
def emg_graph(step):
    emg_data = recorder.get_buffered_data("emg")
    trace1 = []
    emg_labels = ["channel " + str(i) for i in range(len(emg_data.columns) -2)]
    for i, emg in enumerate(emg_labels):
        trace1.append(go.Scatter(x=emg_data["relative_time"],
                                 y=emg_data["emg" + str(i)],
                                 mode='lines',
                                 opacity=0.7,
                                 name=emg,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'EMG signals', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [emg_data["relative_time"].iloc[0], emg_data["relative_time"].iloc[-1]]},
              ),

              }

    return figure

# Callback for opt price
@app.callback(Output('opt', 'figure'),
              [Input('emg-stepper', 'n_intervals')])
def opt_graph(step):
    opt_data = recorder.get_buffered_data("optitrack")
    header=list(opt_data.columns)[2:]
    nb_frames=int(len(header)/7)
    names=[]
    for i in range(nb_frames):
      names.append(header[i*7].replace('_x', ''))
    opt_labels = names

    fig = go.Figure()
      #5 frame centered on current frame
    for i, opt in enumerate(opt_labels):
      multiplier0=str(i*100)
      multiplier1=str(100-i*50)
      multiplier2=str(50+i*25)

      #current frame
      fig.add_trace(go.Scatter3d(
          x=[opt_data[names[i]+"_x"].iloc[-1]],
          y=[opt_data[names[i]+"_y"].iloc[-1]],
          z=[opt_data[names[i]+"_z"].iloc[-1]],
          name="current "+opt,
          mode='markers',
          showlegend = True,
          marker_color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)',
          marker=dict(
              size=20,
              opacity=1)
          ))

    fig.update_layout(
                        scene = dict(
                          xaxis = dict(
                               backgroundcolor="rgb(200, 200, 230)",
                               gridcolor="white",
                               showbackground=True,
                               zerolinecolor="white",
                               nticks=10,
                               range=[-3,3]),
                          yaxis = dict(
                              backgroundcolor="rgb(230, 200,230)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              nticks=10,
                              range=[-3,3]),
                          zaxis = dict(
                              backgroundcolor="rgb(230, 230,200)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                               nticks=10,
                               range=[-3,3]),
                          xaxis_title='X AXIS ',
                          yaxis_title='Y AXIS ',
                          zaxis_title='Z AXIS '),
                        width=450,
                        margin=dict(r=20, b=100, l=10, t=50),
                        title={'text': 'Optitrack signals', 'font': {'color': 'white'}, 'x': 0.5},
                        hovermode='x',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        template='plotly_dark',
                        scene_aspectmode='cube'
                      )
    return fig

    # Callback for tps price
@app.callback(Output('tps', 'figure'),
              [Input('emg-stepper', 'n_intervals')])
def tps_graph(step):
    tps_data = recorder.get_buffered_data("tps")
    header=list(tps_data.columns)[2:]
    fig = go.Figure( [go.Bar(x=header,
                             y=tps_data.iloc[-1, 2:],
                             marker_color='rgb(50,50,100)',
                             textposition='auto',   )])

    y_max=12000

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
        paper_bgcolor='rgba(0, 50, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        hovermode='x',
        autosize=True,
        title={'text': 'TPS signals', 'font': {'color': 'white'}, 'x': 0.5},
        uirevision='true',
    )



    return fig


if __name__ == '__main__':
    if recorder is None:
        recorder = intialize_recorder()

    app.run_server(debug=False, use_reloader=False, host='0.0.0.0', port=8080)
    