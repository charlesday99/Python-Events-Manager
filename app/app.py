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
    if name in EVENTS_LIST:
        content = open(os.path.join(EVENTS_PATH,(name + ".html"))).read()
        return render_template('event.html', content=content, title="Test")
    else:
        return abort(404)


#Serve favicon for all calls
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


#Handle 400 Error
@app.errorhandler(400)
def error_400(e):
    return render_template('error.html',
                           code=400,
                           about="Invalid request, try again with different values!"),400
#Handle 404 Error
@app.errorhandler(404)
def error_404(e):
    return render_template('error.html',
                           code=404,
                           about="The file/service was not found, try again!"),404
#Handle 418 Error
@app.errorhandler(418)
def error_418(e):
    return render_template('error.html',
                           code=418,
                           about="I'm a teapot. This server is a teapot, not a coffee machine."),418
#Handle 500 Error
@app.errorhandler(500)
def error_500(e):
    return render_template('error.html',
                           code=500,
                           about="Something on the server went very wrong, Sorry!"),500
#Start point
if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 80), app)

    for event in glob.glob(os.path.join(EVENTS_PATH, "*.html")):
        EVENTS_LIST[(os.path.split(event)[1].split('.')[0])] = event
    
    print("Loaded as HTTP Server on port 80, running forever:")
    http_server.serve_forever()
