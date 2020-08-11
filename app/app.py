from PIL import Image
import functools
import datetime
import urllib
import glob
import os
import re

from flask import (Flask, flash, Markup, redirect, render_template, request,
                   Response, session, url_for, abort, jsonify, send_file)
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *
from gevent.pywsgi import WSGIServer

from passlib.hash import sha256_crypt
import links


# Blog configuration values.

# You may consider using a one-way hash to generate the password, and then
# use the hash again in the login view to perform the comparison. This is just
# for simplicity.
HASHED_PASS = "$5$rounds=535000$94W0HLA2Sde5yC.A$F.H1Y6Qi19ELOzFhH4vbwTdA7P8QrPZk.C54Cby47S7"
APP_DIR = os.path.dirname(os.path.realpath(__file__))

# The playhouse.flask_utils.FlaskDB object accepts database URL configuration.
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')
DEBUG = False

# The secret key is used internally by Flask to encrypt session data stored
# in cookies. Make this unique for your app.
SECRET_KEY = 'shhh, secret!'

# This is used by micawber, which will attempt to generate rich media
# embedded objects with maxwidth=800.
SITE_WIDTH = 800

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__,static_url_path='')
app.config.from_object(__name__)

# FlaskDB is a wrapper for a peewee database that sets up pre/post-request
# hooks for managing database connections.
flask_db = FlaskDB(app)

# The `database` is the actual peewee database, as opposed to flask_db which is
# the wrapper.
database = flask_db.database

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())

#Initalise affilate links database
LinkDB = links.LinksDB()

#Paths
IMAGE_PATH = os.path.join(APP_DIR,"static","content")
THUMBNAIL_PATH = os.path.join(APP_DIR,"static","content","thumbnails")

# Categories (should probably store these in db).
categories = ["art", "history", "outdoor", "food"]

class Entry(flask_db.Model):
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    category = CharField()
    link_id = CharField()

    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)

    def save(self, *args, **kwargs):
        # Generate a URL-friendly representation of the entry's title.
        if not self.slug:
            self.slug = re.sub(r'[^\w]+', '-', self.title.lower()).strip('-')
        ret = super(Entry, self).save(*args, **kwargs)

        # Store search content.
        self.update_search_index()
        return ret

    def update_search_index(self):
        # Create a row in the FTSEntry table with the post content. This will
        # allow us to use SQLite's awesome full-text search extension to
        # search our entries.
        exists = (FTSEntry
                  .select(FTSEntry.docid)
                  .where(FTSEntry.docid == self.id)
                  .exists())
        content = '\n'.join((self.title, self.content))
        if exists:
            (FTSEntry
             .update({FTSEntry.content: content})
             .where(FTSEntry.docid == self.id)
             .execute())
        else:
            FTSEntry.insert({
                FTSEntry.docid: self.id,
                FTSEntry.content: content}).execute()

    @classmethod
    def public(cls):
        return Entry.select().where(Entry.published == True)

    @classmethod
    def drafts(cls):
        return Entry.select().where(Entry.published == False)

    @classmethod
    def search(cls, query):

        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return an empty query.
            return Entry.noop()
        else:
            search = ' '.join(words)

        # Query the full-text search index for entries matching the given
        # search query, then join the actual Entry data on the matching
        # search result.
        return (Entry
                .select(Entry, FTSEntry.rank().alias('score'))
                .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
                .where(
                    FTSEntry.match(search) &
                    (Entry.published == True))
                .order_by(SQL('score')))

class FTSEntry(FTSModel):
    content = TextField()

    class Meta:
        database = database

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if sha256_crypt.verify(password, app.config['HASHED_PASS']):
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog/')
def blog():

    search_query = request.args.get('q').lower()

    if search_query:
        category_type = None
        if search_query in categories:
            search_query = search_query.capitalize()
            query = (Entry).select(Entry).where(Entry.category == search_query)
            category_type = search_query
        else:
            query = Entry.search(search_query)
    else:
        query = Entry.public().order_by(Entry.timestamp.desc())

    # The `object_list` helper will take a base query and then handle
    # paginating the results if there are more than 20. For more info see
    # the docs:
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#object_list
    return object_list(
        'blog.html',
        query,
        search=search_query,
        category=category_type,
        check_bounds=False)

@app.route('/projects/')
def projects():
    return render_template('projects.html')

@app.route('/about/')
def about():
    return render_template('about.html')


def _create_or_edit(entry, template):
    if request.method == 'POST':
        entry.title = request.form.get('title') or ''
        entry.content = request.form.get('content') or ''
        entry.category = request.form.get('category') or ''
        entry.published = request.form.get('published') or False
        entry.link_id = request.form.get('ID') or ''
        if not (entry.title and entry.content and entry.category):
            flash('Title and Content are required.', 'danger')
        else:
            # Wrap the call to save in a transaction so we can roll it back
            # cleanly in the event of an integrity error.
            try:
                with database.atomic():
                    entry.save()
            except IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Entry saved successfully.', 'success')
                if entry.published:
                    return redirect(url_for('detail', slug=entry.slug))
                else:
                    return redirect(url_for('edit', slug=entry.slug))

    return render_template(template, entry=entry)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Entry(title='', content=''), 'create.html')

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('blog.html', query, check_bounds=False)

@app.route('/p/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Entry.select()
    else:
        query = Entry.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('detail.html', entry=entry)

@app.route('/p/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    return _create_or_edit(entry, 'edit.html')

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    # We'll use this template filter in the pagination include. This filter
    # will take the current URL and allow us to preserve the arguments in the
    # querystring while replacing any that we need to overwrite. For instance
    # if your URL is /?q=search+query&page=2 and we want to preserve the search
    # term but make a link to page 3, this filter will allow us to do that.
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)


#Handle 400 Error
@app.errorhandler(400)
def error_400(e):
    return render_template('error.html', error_code=400,
        error_info="Invalid request, try again with different values!"),400

#Handle 404 Error
@app.errorhandler(404)
def error_404(e):
    return render_template('error.html', error_code=404,
        error_info="The file/service was not found, try again!"),404

#Handle 418 Error
@app.errorhandler(418)
def error_418(e):
    return render_template('error.html', error_code=418,
        error_info="I'm a teapot. This server is a teapot, not a coffee machine."),418

#Handle 500 Error
@app.errorhandler(500)
def error_500(e):
    return render_template('error.html', error_code=500,
    error_info="Something on the server went very wrong, Sorry!"),500

#Handle image requests
@app.route('/image/',methods=['GET', 'POST', 'DELETE','UPDATE'])
def image_api():
    if request.method == 'POST':
        try:
            #Open the image from the POST request
            file = request.files['file']
            img = Image.open(file)

            #Convert to RGB if a PNG is uploaded
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            #Extract the file name
            filename = file.filename.split(".")[0] + ".jpg"

            #Save the image as a JPEG
            img.save(os.path.join(IMAGE_PATH,filename))

            #Generate and save a small thumbnail version
            img.thumbnail((140,140))
            img.save(os.path.join(THUMBNAIL_PATH,filename))
        
            #Return a success message
            flash('Image uploaded successfully.', 'success')
            return redirect(url_for('image_manager'))
        except:
            flash('Image uploaded failed.', 'danger')
            return redirect(url_for('image_manager'))
    else:
        return abort(404)

#Host image management page
@app.route('/image-manager/')
@login_required
def image_manager():
    #Find all the images in the thumbnails folder and pass
    #the paths to the template
    images = {}
    for path in glob.glob(os.path.join(IMAGE_PATH,"thumbnails", "*.jpg")):
        images[path.split("thumbnails")[1][1:]] = path.split("static")[1]
    return render_template('images.html', images=images)

#Handle links requests
@app.route('/link/<ID>')
def link_api(ID):
    if (LinkDB.hasID(ID)):
        LinkDB.addCounter(ID)
        return redirect(LinkDB.getLink(ID)[1], code=302)
    else:
        return abort(404)

#Return link info
@app.route('/link/<ID>/info')
@login_required
def link_api_info(ID):
    if (LinkDB.hasID(ID)):
        data = LinkDB.getLink(ID)
        return {"count": data[2],"URL":data[1]}
    else:
        return abort(404)

#Delete Link
@app.route('/link/<ID>/delete')
@login_required
def link_api_delete(ID):
    if (LinkDB.hasID(ID)):
        LinkDB.deleteLink(ID)
        return redirect(url_for('link_manager'))
    else:
        return abort(404)

#Update Link
@app.route('/link/<ID>/update')
@login_required
def link_api_update(ID):
    if (LinkDB.hasID(ID)):
        LinkDB.updateLink(ID,request.args.get('URL'))
        return redirect(url_for('link_manager'))
    else:
        return abort(404)
    
#Reset link counter
@app.route('/link/<ID>/reset')
@login_required
def link_api_reset(ID):
    if (LinkDB.hasID(ID)):
        LinkDB.resetCounter(ID)
        return redirect(url_for('link_manager'))
    else:
        return abort(404)

#Create new link
@app.route('/link/new', methods=['POST'])
@login_required
def link_post():
    LinkDB.createLink(request.form['URL'])
    return redirect(url_for('link_manager'))

#Create new link
@app.route('/link/dump')
@login_required
def link_dump():
    return jsonify(LinkDB.dump())

#Host image management page
@app.route('/link-manager/')
@login_required
def link_manager():
    return render_template('links.html',links=LinkDB.dump())

#Start point
if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 80), app)
    print("Loaded as HTTP Server on port 80, running forever:")
    http_server.serve_forever()
