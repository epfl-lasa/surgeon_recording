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
                                                    interval=200, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                        dcc.Interval(id='image-stepper',
                                                    interval=100, # 25 fps in milliseconds
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
                                  )
                                ]
                             ),
                      html.Div(className='nine columns div-for-charts bg-grey',
                               children=[
                                html.Div(className='images',
                                         children=[html.Img(id='rgb_image', height="480", width="640"),
                                                   html.Img(id='depth_image', height="480", width="640")]
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

# @app.callback(Output('3d-scatter', 'children'),
#               [Input('frame_selector', 'value')])
# def update_3d_scatter(selected_percentage):
#   selected_frame = int(selected_percentage * reader.get_nb_frames())
#     trace1 = []
#     opt_data,_ = reader.get_frame(selected_frame, window_width=25)
#     opt_labels = ["test"]
#     for i, opt in enumerate(opt_labels):
#         trace1.append(go.Scatter(x=emg_data["relative_time"],
#                                  y=emg_data["emg" + str(i)],
#                                  mode='lines',
#                                  opacity=0.7,
#                                  name=emg,
#                                  textposition='bottom center'))
#     traces = [trace1]    
#     f = go.FigureWidget(px.scatter_3d(df, x = 'x_val', y = 'y_val', z = 'z_val', hover_name = 'company_nm'))

#     f.layout.clickmode = 'event+select'
#     f.data[0].on_click(handle_click) # if click, then update point/df.      

#     return dcc.Graph(id = '3d_scat', figure=f)

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
    emg_data = recorder.get_buffered_emg()
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


if __name__ == '__main__':
    if recorder is None:
        recorder = intialize_recorder()

    app.run_server(debug=False, use_reloader=False)