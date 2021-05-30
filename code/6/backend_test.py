import time

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/calc/add/<int:a>/<int:b>')
def add(a, b):
    return str(a + b)


storage = {}


@app.route('/storage/set/<key>/<value>')
def set_storage(key, value):
    storage[key] = value
    return "OK"


@app.route('/storage/get/<key>')
def get(key):
    return storage[key]


@app.route('/time/current')
def current():
    return "<h1> {} </h1>".format(time.asctime(time.localtime(time.time())))


if __name__ == '__main__':
    app.run()
