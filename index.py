"""
Run this app with `python index.py` and
visit http://127.0.0.1:8050/ in your web browser.
index.py acts as a directory, rendering the required content based on the URL.
"""
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app, server
import pages
import os
# os.system('python3 dataRefresher.py &')


server = server # required for deployment

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div('Price Dashboard'),
    html.Div(id='page-content'),
],id='page-load')

@app.callback(Output('page-content','children'),
              Input('url','pathname'),
              )
def render_content(url):
    if url in ['/']:
        return pages.prices.layout
    else:
        return pages.error_404.layout

if __name__ == '__main__':
    app.run_server(debug=False)
