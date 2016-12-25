from flask import Flask, render_template, request
import requests, random
import pandas as pd
from bokeh.plotting import figure,output_file,show
from bokeh.embed import components

# initialize the Flask application
app = Flask(__name__)

def get_data(ticker):
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % ticker
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    response = session.get(api_url)
    data = response.json()
    #data.keys()
    column_names = data['column_names']
    dataset = data['data']
    df = pd.DataFrame(dataset,columns = column_names)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Bokeh tools
TOOLS = "resize,pan,wheel_zoom,box_zoom,reset,previewsave"

def rand_color():
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())

def make_figure(stock,df,features):
    plot=figure(width=1000,height=500,x_axis_type="datetime",responsive=True)

    for feature in features:
        plot.line(df["Date"],df[str(feature)],color = rand_color(), legend = '%s %s' %(stock, str(feature)),alpha=0.5)
    
    plot.legend.label_text_font = 'times'
    plot.legend.label_text_font_style = 'italic'
    plot.legend.label_text_color = 'navy'

    return plot

# define a route for the default URL, which loads the submi form
@app.route('/')
def form():
    return render_template('index.html')

# define a route for the action of the form, for example /hello/
@app.route('/hello/', methods = ['POST'])
def hello():
    stock = request.form['ticker']
    features = request.form.getlist('features')
    df = get_data(stock)
    plot = make_figure(stock, df,features)
    script, div = components(plot)
    return render_template('graph.html',script=script, div=div,stock = stock.upper())

if __name__ == '__main__':
    app.run(port=33507)