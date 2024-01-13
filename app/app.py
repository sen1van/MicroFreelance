from flask import Flask, render_template
from random import randint
from flask_login import LoginManager
from conifg import Config


app = Flask(__name__, static_url_path='/static')
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(Config)

import routes


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

