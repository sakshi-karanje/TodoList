#!flask/bin/python
from flask import Flask
from flaskrun import flaskrun

application = Flask(__name__)


@application.route('/', methods=['GET'])
def get():
    return '{"Output":"Hello Worl,njbvhd"}'


@application.route('/', methods=['POST'])
def post():
    return '{"Output":"Hello World"}'

if __name__ == '__main__':
    flaskrun(application)
