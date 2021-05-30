import re
import os
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

pattern = re.compile(r'(?:(?:1[0-9][0-9]\.)|(?:2[0-4][0-9]\.)|(?:25[0-5]\.)|(?:[1-9][0-9]\.)|(?:[0-9]\.)){3}(?:(?:1[0-9][0-9])|(?:2[0-4][0-9])|(?:25[0-5])|(?:[1-9][0-9])|(?:[0-9]))')

@app.route('/ping')
def ping():
    host = request.args.get("host")
    print(host)
    if host is None:
        return ""
    if pattern.match(host) is None:
        return ""    
    f = os.popen("ping {} -c 4".format(host) , "r")
    ret = f.read()
    return "<div> {} </div>".format(ret).replace("\n", "<br/>")



@app.route('/chat')
def chat():
    word = request.args.get("word")
    if word is None:
        return ""
    path = os.path.dirname(os.path.abspath(__file__)) + "/chat.py"
    print(path)
    f = os.popen("python {} {}".format(path, word) , "r")
    ret = f.read()
    return "<div> {} </div>".format(ret).replace("\n", "<br/>")



if __name__ == '__main__':
    app.run()
