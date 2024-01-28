from flask import Flask, render_template
from random import randint
from conifg import Config


app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('base/base.html')

@app.route('/login/')
@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

