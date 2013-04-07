from __future__ import with_statement
from contextlib import closing
# all the imports
import sqlite3, json, urllib, pprint
import pdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_entries():
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    url = "https://api.foursquare.com/v2/users/self/checkins?oauth_token=BIX22BVXBSLL32SXQCO1SCMQSRZDEPBY0W3IDGWSUK1BV5NS&v=20130407"
    output = json.load(urllib.urlopen(url))
    
    for i in output['response']['checkins']['items']:
        cat = i['venue']['categories'][0]['name']
        tmp = g.db.execute ('select category, count from entries where category=(?)', [cat])
        if len(tmp.fetchall())!=0:
            g.db.execute ('update entries set count=count+1 where category=(?)', [cat])
            print 'hi'
            g.db.commit()
        else: 
            g.db.execute ('insert into entries (category, count) values (?, ?)', [cat, 1])
            g.db.commit()
    
    
    cur = g.db.execute('select category, count from entries order by id desc')
    entries = [dict(category=row[0], count=row[1]) for row in cur.fetchall()]

    count = len(output['response']['checkins']['items'])
    #pdb.set_trace()
    test = [dict(place=i['venue']['name']) for i in output['response']['checkins']['items']]
    return render_template('show_entries.html', entries=entries, test=test, count=count)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
