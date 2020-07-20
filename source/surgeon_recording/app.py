import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from surgeon_recording.reader import Reader
from os.path import join
import cv2
import base64
import time


# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

reader = Reader()
exp_folder = join('data', 'data15')
reader.play(exp_folder)

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
                                        dcc.Interval(id='auto-stepper',
                                                    interval=1000, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                        dcc.RangeSlider(
                                          id="slider_frame",
                                          min=0,
                                          max=1,
                                          step=0.01,
                                          value=[0.,1.]
                                        ),
                                        dcc.Store(id='start_index'),
                                        dcc.Store(id='stop_index'),
                                        dcc.Store(id='selected_frame')
                                     ],
                                     style={'color': '#1E1E1E'}),
                                 html.Div(
                                     className="buttons-bar",
                                     children=[
                                      html.Button('Play', id='btn-play', n_clicks=0, n_clicks_timestamp=0),
                                      html.Button('Pause', id='btn-pause', n_clicks=0, n_clicks_timestamp=0),
                                      html.Button('Stop', id='btn-stop', n_clicks=0, n_clicks_timestamp=0),
                                      html.Button('Export', id='btn-export', n_clicks=0),
                                      dcc.Store(id='animate', data=True)],
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
                                         children=[dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                                   html.Div(id='3d-scatter')])
                               ])
                 ])
        ]

)

@app.callback([Output('start_index', 'data'), Output('stop_index', 'data')],
              [Input('slider_frame', 'value')])
def select_frame(selected_percentage):
  start_index = int(selected_percentage[0] * (reader.get_nb_frames() - 1))
  stop_index = int(selected_percentage[1] * (reader.get_nb_frames() - 1))
  reader.set_current_frame(start_index)
  return start_index, stop_index

# @app.callback(Output('animate', 'data'),
#               [Input('btn-play', 'n_clicks_timestamp')])
# def play(timestamp):
#   print(timestamp)
#   if time.time() - timestamp < 1e-2:
#     return True

# @app.callback(Output('animate', 'data'),
#               [Input('btn-pause', 'n_clicks')])
# def pause(btn):
#   return False

# @app.callback(Output('animate', 'data'),
#               [Input('btn-stop', 'n_clicks'),
#                Input('slider_frame', 'value')])
# def stop(btn, selected_percentage):
#   selected_frame = int(selected_percentage * reader.get_nb_frames())
#   reader.set_current_frame(selected_frame)
#   return False

@app.callback(Output('selected_frame', 'data'),
              [Input('auto-stepper', 'n_intervals'),
               Input('start_index', 'data'),
               Input('stop_index', 'data')])
def on_click(n_intervals, start_index, stop_index):
  selected_frame = (n_intervals + 1) % stop_index
  reader.get_next_frame()
  return selected_frame

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
              [Input('selected_frame', 'data')])
def update_rgb_image_src(selected_frame):
    image = reader.get_image("rgb", selected_frame)
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

@app.callback(Output('depth_image', 'src'),
              [Input('selected_frame', 'data')])
def update_depth_image_src(selected_frame):
    image = reader.get_image("depth", selected_frame)
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('selected_frame', 'data'),
               Input('start_index', 'data'),
               Input('stop_index', 'data')])
def emg_graph(selected_frame, start_frame, stop_frame):
    _, emg_data = reader.get_data(start_frame, stop_frame)
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
    app.run_server(debug=True)