import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import os
from dash.dependencies import Input, Output
from flask import Flask

df = pd.read_csv('data\\processed\\city_restaurants_filtered.csv', encoding='utf-8')

colors = ['#1f77b4','#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',  '#e377c2', '#7f7f7f',  '#bcbd22', '#17becf', 'cyan']

neighborhoods = df['Neighborhood'].value_counts().index

external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

checklist=html.Div([
        html.H4('Settings'),
        dcc.Checklist(
        options=[
            {'label':neighborhoods[i], 'value':i} for i in range(len(neighborhoods))
        ],
        value=[0],
        id='checklist',
        labelStyle={'display': 'inline-block', 'margin-right':'10px' }
    )])

description = html.Div([
        html.H4('About'),
        html.P('The following visualization shows the most popular restaurants in Panama City, Panama, ordered by their average'\
               ' price and rating. The data was scraped from the website Degusta, an app that lets users rate restaurants'\
               ' based on 3 different categories: Ambient, Food and Service. These categories are rated out of 5.'\
               ' I added the scores to create an aggregate rating (scored out of 15) for all the restaurants. '\
               'While there are over 2000+ restaurants in the city, I limited the dataset to restaurants that'\
               ' have been rated by at least 75 users. This lets us focus on the most popular restaurants, and'\
               ' yields a more representative sample for restaurant ratings.'\
               ' I\'ve also divided the restaurants by different areas in the city. I grouped some neighborhoods, such as '\
               'Albrook and Clayton, into a single area because of their proximity to each other.')
    ])

explanation = html.Div([
        html.H4('Reading the Graph'),
        html.P('Each restaurant is represented by a circle. The bigger the circle, the more users that have rated the '\
               'restaurant through the app (check-ins). Different areas are represented by different colors. You can toggle which '\
               'areas you want shown in the visualization through the radio boxes below. Hovering close to each circle'\
               ' will show detailed information for each restaurant.')
    ])

header = html.Div([html.H2('PTY Food'),
                   html.P('Eduardo Yap - 2019'),
                  html.Hr()])

graph = html.Div(dcc.Graph(id='graph'), id='content')

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name=__name__, server=server)
app.title = 'PTY Food'
app.css.config.serve_locally = False

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(description, className='row'),
            html.Div(explanation, className='row'),
            html.Div(checklist, className='row'),
            html.Div(graph, className='row')
        ])
    ],
    className='container'
)

for css in external_css:
    app.css.append_css({'external_url': css})


@app.callback(Output('graph', 'figure'), [Input('checklist', 'value')])
def make_graph(checklist_values):
    data = [go.Scatter(
        x=df[df['Neighborhood'] == neigh]['agg_rating'],
        y=df[df['Neighborhood'] == neigh]['Price'],
        mode='markers',
        hoverinfo=None,
        name=neigh,
        text=df[df['Neighborhood'] == neigh]['text'],
        visible='legendonly' if i not in checklist_values else True,
        marker=dict(
            size=df[df['Neighborhood'] == neigh]['Votes'],
            sizemode='area',
            sizeref=max(df['Votes']) / (60. ** 2),
            sizemin=4,
            color=colors[i],
            opacity=0.4,
            autocolorscale=False,
            symbol='circle'
        )) for i, neigh in enumerate(neighborhoods)]

    layout = dict(
        hovermode='closest',
        showlegend=False,
        autosize=True,
        height=750,
        title='Price vs. Rating',
        xaxis=dict(
            range=[min(df['agg_rating']) - 0.25, max(df['agg_rating']) + 0.25],
            title=dict(
                text='Total Rating (out of 15)'
            )
        ),
        yaxis=dict(
            range=[min(df['Price']) - 2.5, max(df['Price']) + 2.5],
            title=dict(
                text='Average Price (dollars)'
            )
        )
    )
    return go.Figure(data=data, layout=layout)


if __name__ == '__main__':
    app.run_server()

