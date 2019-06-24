from flask import Flask, render_template, request,flash
import pandas as pd
import io
import requests

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.tickers import FixedTicker


app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')

# Create the main plot

def create_figure(df,stock):
	data=ColumnDataSource(df.loc[:30,['timestamp','open']])

	p = figure(plot_width=700, plot_height=400,x_axis_type='datetime',title="30-Day Performance of "+stock)
	p.title.text_font_size = '25pt'

	p.xaxis.axis_label="Date"
	p.xaxis.axis_label_text_font_size="15pt"
	p.xaxis.major_label_text_font_size = "10pt"

	p.yaxis.axis_label="Opening price"
	p.yaxis.axis_label_text_font_size="15pt"
	p.yaxis.major_label_text_font_size = "10pt"

	p.line(x='timestamp', y='open', line_width=2, alpha=0.6, source=data)

	p.xaxis.major_label_orientation = 1.2
	return p

# Index page
@app.route('/')
def index():
	# Determine the selected feature
	
	stock = request.args.get("stock")
	error=None

	if stock == None:
		stock = "MSFT"

	url="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+stock+"&apikey= 6V7OLNYV313CF0UT&datatype=csv"
	s=requests.get(url).content
	c=pd.read_csv(io.StringIO(s.decode('utf-8')))
	try:
		c['timestamp']=pd.to_datetime(c['timestamp'])

	except:
		error="Enter a valid stock symbol"
		
	if error is not None:
		stock="MSFT"
		url="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+stock+"&apikey= 6V7OLNYV313CF0UT&datatype=csv"
		s=requests.get(url).content
		c=pd.read_csv(io.StringIO(s.decode('utf-8')))
		c['timestamp']=pd.to_datetime(c['timestamp'])
	else:
		error="Successfully loaded {} data".format(stock)	

	# Create the plot
	plot = create_figure(c, stock)
	url="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+stock+"&apikey= 6V7OLNYV313CF0UT&datatype=csv"
	s=requests.get(url).content
	c=pd.read_csv(io.StringIO(s.decode('utf-8')))
		
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	flash(error)
	return render_template("index.html", script=script, div=div)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)