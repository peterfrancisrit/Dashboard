import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import gc
from Scraper import CafeScraper

class Data(CafeScraper):
    def __init__(self, websites, conversions):
        CafeScraper.__init__(self,websites,conversions)
        self.getContent()
        self.cleantype()
        self.cleantime()
        self.tocsv()

class Graphs:
    def __init__(self,file):
        self.df = pd.read_csv(file)
        self.companies = ['The Barn','Drop Coffee','Five Elephant', 'Coffee Supreme','Switch Coffee','Square Mile Coffee']

        # Graph Functions
    def PriceScatter(self):
        df = self.df[self.df.beans == 1]
        data = [go.Scatter(x=list(df.updated_at),
                            y=list(df.price),
                            name="Price Plot",
                            line=dict(color='#fc8403'))]
        layout = dict(title="Price Scatter",showlegend=True)
        figure = dict(data=data,layout=layout)
        del data
        del layout
        del df
        gc.collect()
        return dcc.Graph(id="Price Scatter",figure=figure)

    def PriceUpdate(self,value):
        df = self.df[(self.df.key == value) & self.df.beans == 1]
        data = [go.Scatter(x=list(df.updated_at),
                            y=list(df.price),
                            name="Price Plot",
                            line=dict(color='#fc8403'))]
        layout = dict(title="Price Scatter",showlegend=True)
        figure = dict(data=data,layout=layout)
        del layout
        del data
        del df
        gc.collect()
        return figure


    def CompanyBarPlot(self):
        new = self.df.groupby('vendor').type_coffee.nunique()
        new = new[new > 1].drop('Kalita',axis=0)

        data = [go.Bar(x=list(new.index),
                        y=list(new.values),
                        name="Number of Varieties")]
        layout = dict(title="Unique Coffee Varieties", showlegend=True)
        figure = dict(data=data, layout=layout)
        del data
        del layout
        gc.collect()
        self.CompanyBarPlot = dcc.Graph(id="1",figure=figure)

class App(Graphs):
    def __init__(self,file):
        Graphs.__init__(self,file)
        self.app = dash.Dash(external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
        self.value = 0
        self.layout()

    def layout(self):
        self.app.layout = html.Div([
            html.H1(children="Test"),
            html.Label('Dropdown'),
            dcc.Dropdown(
            id='dropdown_roastery',
            options=[
                {'label': 'The Barn', 'value': 0},
                {'label': 'Drop Coffee', 'value': 1},
                {'label': 'Five Elephant', 'value': 2},
                {'label': 'Coffee Supreme', 'value': 3},
                {'label': 'Switch Coffee', 'value': 4},
                {'label': 'Square Mile Coffee', 'value':5}
            ],
            ),

            html.Div([
                html.Div(self.PriceScatter(), id='output_price')
            ])
        ])

        @self.app.callback(
        dash.dependencies.Output('Price Scatter', 'figure'),
        [dash.dependencies.Input('dropdown_roastery', 'value')])

        def update_price(value):
            return self.PriceUpdate(value)


    def run(self):
        self.app.run_server(debug=True)



if __name__=="__main__":
    # app.run_server(debug=True)
    websites = ['https://thebarn.de','https://www.dropcoffee.com','https://www.fiveelephant.com','https://coffeesupreme.com','https://switchcoffee.co.nz','https://shop.squaremilecoffee.com/']
    conversions = [1,0.095,1,0.62,0.60,1.18]

    # data = Data(websites, conversions)

    app = App('results.csv')
    app.run()
