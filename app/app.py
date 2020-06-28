from flask import redirect, url_for, render_template, abort, send_from_directory, send_file, jsonify, request
from flask import Flask

from gevent.pywsgi import WSGIServer
import glob
import json
import os


#Create app
app = Flask(__name__,static_url_path='')
app.debug = False


#Global variables
EVENTS_PATH = "events"
EVENTS_LIST = {}

#Landing page
@app.route('/')
def landing():    
    return render_template('home.html')


#Landing page
@app.route('/event/<string:name>')
def event_page(name):
    content = open(os.path.join(EVENTS_PATH,(name + ".html"))).read()
    print(content)
    return render_template('event.html', content=content, title="Test")


#Serve favicon for all calls
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


#Start point
if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 80), app)

    for event in glob.glob(os.path.join(EVENTS_PATH, "*.html")):
        EVENTS_LIST[(os.path.split(event)[1].split('.')[0])] = event
    
    print("Loaded as HTTP Server on port 80, running forever:")
    http_server.serve_forever()
