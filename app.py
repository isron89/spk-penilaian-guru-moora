import warnings
warnings.filterwarnings("ignore")

from flask_login import logout_user, current_user

from dash import dcc,html
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output

from pages import main, login, error, kelola,nilai
from server import app, server
from src.config import DEV
from src.db import db


content = html.Div(id='pageContent')

app.layout = html.Div([
    dcc.Location(id='url'),
    content
])

@app.callback(
    Output('pageContent', 'children'),
    [
        Input('url', 'pathname'),
    ]
)
def displayPage(pathname):
    if DEV:
        # if pathname == '/main':
        return main.layout
        # else:
        # return kelola.layout()
    else:
        if pathname == '/main':
            if current_user.is_authenticated:
                return main.layout
            else:
                return login.layout
        elif pathname == '/logout':
            if current_user.is_authenticated:
                logout_user()
                return login.layout
            else:
                return login.layout
        else:
            if current_user.is_authenticated:
                return main.layout
            else:
                return login.layout

if __name__ == '__main__':
    app.run_server(debug=True)


