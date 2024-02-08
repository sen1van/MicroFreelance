from flask import Flask, render_template
import fish

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('base/base.html')

@app.route('/login/')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
def my_tasks(filter = None):
    buff = fish.tasks
    if filter == 'from-me':
        buff = [buff[0]]
    return render_template('my_tasks.html', tasks = buff, me = fish.me)


@app.route('/profile')
@app.route('/profile/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

