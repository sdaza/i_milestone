from flask import Flask, render_template, request
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Select, CheckboxGroup, Legend, HoverTool
import pandas as pd
import datetime
import dateutil.relativedelta
from bokeh.layouts import column, widgetbox
from bokeh.embed import components
import quandl

app = Flask(__name__)

# get date and list of tickers

# get dates
today = datetime.datetime.today()
today = today - dateutil.relativedelta.relativedelta(days=1)
start = today - dateutil.relativedelta.relativedelta(months=1)
today_str = today.strftime('%Y-%m-%d')
start_str = start.strftime('%Y-%m-%d')

# get data
import quandl
quandl.ApiConfig.api_key = '5Yj_Fcq66uKbMsC5-9PJ'
df = quandl.get_table('WIKI/PRICES',
                      qopts = { 'columns': ['ticker', 'date', 'open','close'] },
                    #   ticker = ['AAPL', 'MSFT'],
                      date = {'gte': start_str, 'lte': today_str}, paginate=True)

list_tickers = list(df.ticker.unique())

# create plot
def create_figure(selected_ticker):
    source = ColumnDataSource(
        data = {
             'x' : df.loc[df.ticker==selected_ticker, 'date'],
             'o' : df.loc[df.ticker==selected_ticker, 'open'],
             'c' : df.loc[df.ticker==selected_ticker, 'close']
            })


    title = selected_ticker + ' Quandl WIKI Stock Prices, ' + start_str + ' to ' + today_str
    plot = figure(title = title, plot_height = 400, plot_width = 700,
                  x_axis_type = 'datetime', toolbar_location = None)

    line_open = plot.line(x='x', y='o', source = source, color = 'blue',  line_alpha=0.6,
                  line_width = 1.5)
    line_close = plot.line(x='x', y='c', source = source, color = 'red',  line_alpha=0.6,
                  line_width = 1.5)

    lines = [line_open, line_close]

    legend = Legend(items=[
        ('Opening price', [line_open]),
        ('Closing price', [line_close])],
                    location=(0, -30))

    plot.add_layout(legend, 'right')

    hover = HoverTool(tooltips =[
        ('Opening', '@o'),
        ('Closing', '@c')])

    plot.add_tools(hover)
    plot.xaxis.axis_label = "Date"
    plot.yaxis.axis_label = "Stock price"
    return plot

# Index page
@app.route('/')
def index():
    # Determine the selected feature
	selected_ticker = request.args.get("feature_ticker")
	if selected_ticker == None:
		selected_ticker = "AAPL"

    # Create the plot
	plot = create_figure(selected_ticker)

	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("index.html", script=script, div=div,
		list_tickers=list_tickers,  selected_ticker=selected_ticker)

# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=33507)
