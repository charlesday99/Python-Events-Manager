from flask import redirect, url_for, render_template, abort, send_from_directory, send_file, jsonify, request
from flask import Flask

from gevent.pywsgi import WSGIServer
import events
import json
import os


#Create app
app = Flask(__name__,static_url_path='')
app.debug = False


#Global variables
EventsDB = events.EventsDB()


#Landing page
@app.route('/')
def landing():    
    return render_template('home.html')


#Serve favicon for all calls
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


#Start point
if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 80), app)
    print("Loaded as HTTP Server on port 80, running forever:")
    http_server.serve_forever()
