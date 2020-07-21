import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from surgeon_recording.reader import Reader
from os.path import join
import cv2
import base64
import time


# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

reader = Reader()

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='three columns div-user-controls',
                             children=[
                                 html.H2('SURGEON RECORDING APP'),
                                 html.P('Experiment data selection'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                        dcc.Dropdown(id='exp_folder',
                                                     options=[{'label': key, 'value': path} for key, path in reader.get_experiment_list().items()]),
                                        dcc.Interval(id='auto-stepper',
                                                    interval=200, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                        dcc.Store(id='selected_exp'),
                                        dcc.Store(id='start_index'),
                                        dcc.Store(id='stop_index'),
                                        dcc.Store(id='selected_frame'),
                                        dcc.Store(id='selected_emg_frame'),
                                        dcc.Store(id='emg_start_index'),
                                        dcc.Store(id='emg_stop_index'),
                                        dcc.Store(id='current_emg_start'),
                                        dcc.Store(id='current_emg_stop'),
                                        dcc.Store(id='window_size', data=2000)
                                     ],
                                     style={'color': '#1E1E1E'}),
                                 html.P('Time sequence selection'),
                                 dcc.RangeSlider(
                                  id="slider_frame",
                                  min=0,
                                  max=100,
                                  step=0.1,
                                  value=[0.,100.]
                                  ),
                                 html.Div(
                                     className="buttons-bar",
                                     children=[
                                      html.P('Export'),
                                      dcc.Input(id="export_folder", type="text", placeholder=""),
                                      html.Button('Export', id='btn-export', n_clicks=0),
                                      html.Div(id='output_text')]
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
               State('selected_exp', 'data')])
def export(n_clicks, value, start_index, stop_index, selected_exp):
    if selected_exp is None:
      return 'No data folder selected'
    if value is None:
      return 'Empty folder specified, please enter a valid name'
    reader.export(value, start_index, stop_index)
    return 'Sequence exported to {} folder'.format(value)


@app.callback([Output('start_index', 'data'),
               Output('stop_index', 'data'),
               Output('emg_start_index', 'data'),
               Output('emg_stop_index', 'data'),
               Output('auto-stepper', 'n_intervals')],
              [Input('slider_frame', 'value'),
               Input('selected_exp', 'data')])
def select_frame(selected_percentage, selected_exp):
  if selected_exp is None:
    return 0, 0, 0, 0, 0
  start_index = int(selected_percentage[0] / 100 * (reader.get_nb_frames() - 1))
  stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_frames() - 1))
  emg_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_emg_frames() - 1))
  emg_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_emg_frames() - 1))
  return start_index, stop_index, emg_start_index, emg_stop_index, start_index

@app.callback([Output('current_emg_start', 'data'),
               Output('current_emg_stop', 'data')],
              [Input('selected_emg_frame', 'data'),
               Input('emg_start_index', 'data'),
               Input('emg_stop_index', 'data'),
               Input('window_size', 'data')],
              [State('selected_exp', 'data')])
def select_emg_frame(selected_frame, start_index, stop_index, window_size, selected_exp):
  if selected_exp is None:
    return 0, 0
  step = int(selected_frame / window_size)
  start = step * window_size
  stop = min((step + 1) * window_size, stop_index)
  return start, stop

@app.callback([Output('selected_frame', 'data'),
               Output('selected_emg_frame', 'data')],
              [Input('auto-stepper', 'n_intervals'),
               Input('slider_frame', 'value'),
               Input('slider_frame', 'step')],
              [State('selected_exp', 'data')])
def on_click(n_intervals, limits, step, selected_exp):
  if selected_exp is None:
    return 0, 0
  d = limits[1] - limits[0]
  selected_percentage = ((n_intervals * step - limits[0]) % d + d) % d + limits[0]
  selected_frame = int(selected_percentage / 100 * (reader.get_nb_frames() - 1))
  selected_emg_frame = int(selected_percentage / 100 * (reader.get_nb_emg_frames() - 1))
  return selected_frame, selected_emg_frame

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
              [Input('selected_frame', 'data')],
              [State('selected_exp', 'data')])
def update_rgb_image_src(selected_frame, selected_exp):
    if selected_exp is None:
      return
    image = reader.get_image("rgb", selected_frame)
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

@app.callback(Output('depth_image', 'src'),
              [Input('selected_frame', 'data')],
              [State('selected_exp', 'data')])
def update_depth_image_src(selected_frame, selected_exp):
    if selected_exp is None:
      return
    image = reader.get_image("depth", selected_frame)
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('selected_emg_frame', 'data'),
               Input('current_emg_start', 'data'),
               Input('current_emg_stop', 'data')],
              [State('selected_exp', 'data')])
def emg_graph(selected_frame, current_emg_start, current_emg_stop, selected_exp):
    emg_data = reader.emg_data.iloc[current_emg_start:current_emg_stop]
    trace1 = []
    emg_labels = ["channel " + str(i) for i in range(len(emg_data.columns) -2)]
    for i, emg in enumerate(emg_labels):
        trace1.append(go.Scatter(x=emg_data["relative_time"],
                                 y=emg_data["emg" + str(i)],
                                 mode='lines',
                                 opacity=0.7,
                                 name=emg,
                                 textposition='bottom center'))
    time = reader.emg_data.iloc[selected_frame]["relative_time"]
    trace1.append(go.Scatter(x=[time, time],
                             y=[-800, 800],
                             mode='lines',
                             opacity=0.7,
                             name="current frame",
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