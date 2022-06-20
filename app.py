"""
app.py initializes the application and server.
"""
import dash

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                )

server = app.server