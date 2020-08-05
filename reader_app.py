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
                                 html.H2('SURGEON RECORDING APP'),
                                 html.P('Experiment data selection'),
                                 html.Div(

                                     className='div-for-dropdown',
                                     children=[
                                        dcc.Dropdown(id='exp_folder',
                                                     options=[{'label': key, 'value': path} for key, path in reader.get_experiment_list(data_folder).items()]),
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

                                        dcc.Store(id='selected_opt_frame'),
                                        dcc.Store(id='opt_start_index'),
                                        dcc.Store(id='opt_stop_index'),
                                        dcc.Store(id='current_opt_start'),
                                        dcc.Store(id='current_opt_stop'),

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


                                  ),
                                 html.Div(className='graphs',
                                         children=[dcc.Graph(id='opt',config={'displayModeBar': False}, animate=False)])
                                ]
                             ),
                      html.Div(className='nine columns div-for-charts bg-grey',
                               children=[
                                html.Div(className='images',
                                         children=[html.Img(id='rgb_image', height="480", width="640"),
                                                   html.Img(id='depth_image', height="480", width="640")]),
                                html.Div(className='graphs',
                                         children=[dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=False)]),

                                #html.Div(className='graphs',
                                 #        children=[dcc.Graph(id='optitrack', config={'displayModeBar': False}, animate=False)]),
                                #html.Div(className='graphs',
                                #         children=[dcc.Graph(id='opt',config={'displayModeBar': False}, animate=False)])

                               ])
                 ])
        ]

)




'''
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
            hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
            )

    fig.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig
'''







def handle_click(trace, points, selector):
    #c = list(f.data[0].marker.color)
    #s = list(f.data[0].marker.size)
    #for i in points.point_inds:
    #    c[i] = '#bae2be'
    #    s[i] = 20
    #    with f.batch_update():
    #        f.data[0].marker.color = c
    #        f.data[0].marker.size = s
    return 0 # f.data[0]


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
               Output('auto-stepper', 'n_intervals'),

               Output('opt_start_index', 'data'),
               Output('opt_stop_index', 'data')
               ],

              [Input('slider_frame', 'value'),
               Input('selected_exp', 'data')])
def select_frame(selected_percentage, selected_exp):
  if selected_exp is None:
    return 0, 0, 0, 0, 0, 0, 0
  start_index = int(selected_percentage[0] / 100 * (reader.get_nb_frames() - 1))
  stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_frames() - 1))

  emg_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_sensor_frames("emg") - 1))
  emg_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_sensor_frames("emg") - 1))
  opt_start_index = int(selected_percentage[0] / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
  opt_stop_index = int(selected_percentage[1] / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
  return start_index, stop_index, emg_start_index, emg_stop_index, start_index, opt_start_index, opt_stop_index


@app.callback([Output('current_emg_start', 'data'),
               Output('current_emg_stop', 'data')
                
              ],
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
               Output('selected_emg_frame', 'data'),
               Output('selected_opt_frame', 'data')],
              [Input('auto-stepper', 'n_intervals'),
               Input('slider_frame', 'value'),
               Input('slider_frame', 'step')],
              [State('selected_exp', 'data')])
def on_click(n_intervals, limits, step, selected_exp):
  if selected_exp is None:
    return 0, 0 ,0
  d = limits[1] - limits[0]
  selected_percentage = ((n_intervals * step - limits[0]) % d + d) % d + limits[0]
  selected_frame = int(selected_percentage / 100 * (reader.get_nb_frames() - 1))

  selected_emg_frame = int(selected_percentage / 100 * (reader.get_nb_sensor_frames("emg") - 1))
  selected_opt_frame = int(selected_percentage / 100 * (reader.get_nb_sensor_frames("optitrack") - 1))
  return selected_frame, selected_emg_frame, selected_opt_frame


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



    print('printing emg graph')

    

    emg_data = reader.data["emg"].iloc[current_emg_start:current_emg_stop+1]
    trace1 = []
    emg_labels = ["channel " + str(i) for i in range(len(emg_data.columns) -2)]
    for i, emg in enumerate(emg_labels):
        trace1.append(go.Scatter(x=emg_data["relative_time"],
                                 y=emg_data["emg" + str(i)],
                                 mode='lines',
                                 opacity=0.7,
                                 name=emg,
                                 textposition='bottom center'))

    time = reader.data["emg"].iloc[selected_frame]["relative_time"]

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



# Callback for opt price
@app.callback(Output('opt', 'figure'),
              [Input('selected_opt_frame', 'data')
               #Input('current_opt_start', 'data'),
               #Input('current_opt_stop', 'data')
               ],
              [State('selected_exp', 'data')])
def opt_graph(selected_frame, selected_exp):

    print('printing opt  graph')

    range_frame=3


    selected_frame=selected_frame+3
    opt_data = reader.data['optitrack'].iloc[selected_frame-range_frame:selected_frame+range_frame-1]



    print(())


    print('selected_opt_frame')
    print(selected_frame)

    print('opt_data')
    #print(opt_data)
    
  

    lenght= int(((len(opt_data.columns)-2)/7))

    print('lenght')
    print(lenght)
    
      
    header=list(opt_data.columns)[2:]



    nb_frames=int(len(header)/7)
    names=[]

    for i in range(nb_frames):
      names.append(header[i*7].replace('_x', ''))
    
    print(names)  

    
    #df = px.data.iris()
    #print('df')
    #print(df)
    opt_labels = ["channel " + str(i) for i in range (0,lenght)]


    print(opt_labels)


    fig = go.Figure()
      #5 frame centered on current frame
    for i, opt in enumerate(opt_labels):
     

      multiplier0=str(i*100)
      multiplier1=str(100-i*50)
      multiplier2=str(50+i*25)
      print('jesuis la')
    
      fig.add_trace(go.Scatter3d(
          x=opt_data[names[i]+"_x"], y=opt_data[names[i]+"_y"], z=opt_data[names[i]+"_z"],
          name='history '+opt,
          mode='markers',
          showlegend = True,
          marker_color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, .8)',
             
          marker=dict(
              size=[5, 8, 11, 14,17 ], 
                          # set color to an array/list of desired values   
              #colorscale='Bluered',   # choose a colorscale
              opacity=0.5)
          ))


      print('jesuis la  1')
    
        #current frame
      fig.add_trace(go.Scatter3d(
          x=[opt_data[names[i]+"_x"][selected_frame]], y=[opt_data[names[i]+"_y"][selected_frame]], 
          z=[opt_data[names[i]+"_z"][selected_frame]],
          name="current "+opt,
          mode='markers',
          showlegend = True,
          marker_color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)',
         
          marker=dict(
              size=20, 
             # color=[i],                # set color to an array/list of desired values   
              #colorscale='Bluered',   # choose a colorscale
              opacity=1)
          ))



      print('yolo')




    fig.update_layout(
                        scene = dict(
                        xaxis = dict(
                             backgroundcolor="rgb(200, 200, 230)",
                             gridcolor="white",
                             showbackground=True,
                             zerolinecolor="white",),
                        yaxis = dict(
                            backgroundcolor="rgb(230, 200,230)",
                            gridcolor="white",
                            showbackground=True,
                            zerolinecolor="white"),
                        zaxis = dict(
                            backgroundcolor="rgb(230, 230,200)",
                            gridcolor="white",
                            showbackground=True,
                            zerolinecolor="white",),),
                        title={'text': 'Optitrack signals', 'font': {'color': 'white'}, 'x': 0.5},
                        hovermode='x',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        template='plotly_dark'

                      )

    fig.update_layout(scene = dict(
                        xaxis_title='X AXIS ',
                        yaxis_title='Y AXIS ',
                        zaxis_title='Z AXIS '),
                        width=450,
                        margin=dict(r=20, b=100, l=10, t=50))


    maxim_x=[0  for y in range(lenght)]
    maxim_y=[0  for y in range(lenght)]
    maxim_z=[0  for y in range(lenght)]

    min_x=[0  for y in range(lenght)]
    min_y=[0  for y in range(lenght)]
    min_z=[0  for y in range(lenght)]

    








    for i in range (0,nb_frames):
        
          maxim_x[i]=max(reader.data['optitrack'][names[i]+"_x"])
          maxim_y[i]=max(reader.data['optitrack'][names[i]+"_y"])
          maxim_z[i]=max(reader.data['optitrack'][names[i]+"_z"])
          
          min_x[i]=min(reader.data['optitrack'][names[i]+"_x"])
          min_y[i]=min(reader.data['optitrack'][names[i]+"_y"])
          min_z[i]=min(reader.data['optitrack'][names[i]+"_z"])

    print('maxim_x')     

    print(maxim_x)     


    print('maxim_x')
    print(maxim_x)


    #range of the axes
    fig.update_layout(
        scene = dict(
                        xaxis = dict(nticks=10, range=[min(min_x)-0.5,max(maxim_x)+0.5],),
                        yaxis = dict(nticks=10, range=[min(min_y)-0.5,max(maxim_y)+0.5],),
                        zaxis = dict(nticks=10, range=[min(min_z)-0.5,max(maxim_z)+0.5],),),
       )

    fig.update_layout(scene_aspectmode='cube')
             

    #fig = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width',
    #          color='species')

    # fig = px.scatter_3d(opt_data, x='test_x', y='test_y', z='test_z',
              # color='species')
    #fig = go.Figure(data=[go.Scatter3d(x=[opt_dot[:,0]], y=[opt_dot[:,1]], z=[opt_dot[:,2]], mode='markers')])
    #fig = go.Figure(data=[go.Scatter3d(x=[opt_data["test_x"]], y=[opt_data["test_y"]], z=[opt_data["test_z"]], mode='markers')])
    
    #print('opt_data[test]')
    
   
  #trace1=go.Scatter3d(x=opt_data['x_test'], y=opt_data['y_test'], z=opt_data['z_test'], mode='markers')
  #print('newcallback')
  #print(opt_data['x_test'])
  #layout= go.Layout(margin=dict(
  #  l=0,
  #  r=0,
  #  b=0,
  #  t=0))

    #on recupere les donnees
   

    


   # fig = px.scatter_3d(opt_data, x="test_x", y="test_y", z="test_z",
    #          color='species')


    
   # trace1 = []

    #opti label
  #opti_labels = ["no label for now"]
    

    
    #fig.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    #fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

    #fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')

    #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

  
   

  #fig = {'data': trace1,
  #            'layout': layout
  #                }               

  #  fig = go.Figure(
  #      data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
  #      layout=go.Layout(
  #        title=go.layout.Title(text="A Figure Specified By A Graph Object")
  #      )
  #  )
  
    return fig




if __name__ == '__main__':
    app.run_server(debug=True)