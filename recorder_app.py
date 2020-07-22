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


# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

recorder = Recorder('data')

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
                                                    interval=200, # 25 fps in milliseconds
                                                    n_intervals=0
                                        ),
                                     ],
                                     style={'color': '#1E1E1E'}),
                                 html.Div(
                                     className="buttons-bar",
                                     children=[
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

@app.callback(Output('output_text', 'children'),
              [Input('btn-export', 'n_clicks')],
              [State('export_folder', 'value')])
def export(n_clicks, value, start_index, stop_index):
    if value is None:
        return 'Empty folder specified, please enter a valid name'
    reader.export(value, start_index, stop_index)
    return 'Sequence exported to {} folder'.format(value)

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
              [Input('auto-stepper', 'n_intervals')])
def update_rgb_image_src(step):
    image = recorder.get_buffered_rgb()
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

@app.callback(Output('depth_image', 'src'),
              [Input('auto-stepper', 'n_intervals')])
def update_depth_image_src(step):
    image = recorder.get_buffered_depth()
    encoded_image = base64.b64encode(image)
    return 'data:image/jpg;base64,{}'.format(encoded_image.decode())

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('auto-stepper', 'n_intervals')])
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