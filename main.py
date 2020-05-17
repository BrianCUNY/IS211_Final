#! /usr/bin/env python3

#IS211 Assignment FINAL - "main.py"


from flask import Flask, render_template, request, redirect, g, url_for, abort, session, flash
import json
import urllib.request
import urllib.error
from contextlib import closing
import time, os, sqlite3, re

DATABASE = '/tmp/books.db'
DEBUG = True
SECRET_KEY = 'dd50b560b1ba65dadefbcb6e35963715ed92a79643677744'
USERNAME = 'admin'
PASSWORD = 'password'

API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
	
def init_db():
	with closing(connect_db()) as db:
		with app.open_resources('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()
	
@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
		
@app.route('/lookup', methods=['POST','GET'])
def lookup():
	if request.method == 'POST':
		isbn = request.form['ISBN']
		if isbn == "":
			flash("Please enter a valid ISBN")
			return redirect(url_for('lookup'))
		else:
			try:
				url = API_URL + isbn
				html = urllib.urlopen(url)
				data = html.read()
				data = json.loads(data)
				volumeinfo = data['items'][0]['volumeInfo']
				title = volumeinfo['title']
				author = volumeinfo['author'][0]
				pagecount = volumeinfo['pageCount']
				averagerating = volumeinfo['averageRating']
				tumbnail = volumeinfo['imageLinks']['smallThumbnail']
				return render_template('lookup.html', thumbnail=thumbnail, title=title, author=author, pagecount=pagecount, averagerating=averagerating, isbn=isbn)
			except LookupError:
					flash("ISBN search Invalid")
					return redirect(url_for('lookup')
	if request.method == 'GET':
		return render_template('lookup.html')
		
@app.route('/add', methods=['POST'])
def add():
	if not session.get('logged_in'):
		abort(401)
	try:
		g.db.execute('INSERT INTO books (ISBN, TITLE, AUTHOR, PAGECOUNT, '
					 'AVERAGERATING, THUMBNAIL) values (?, ?, ?, ?, ?, ?)',
					 (request.form['isbn'], request.form['title'],
					  request.form['author'], request.form['pagecount'],
					  request.form['averagerating'], request.form['thumbnail']))
		g.db.commit()
		flash("Book successfully added")
		return redirect(url_for('homepage'))
	except():
		flash("Error adding book")
		return redirect(url_for('homepage'))
		
@app.route('/delete', methods=['GET'])
def delete():
	book_id = request.args.get('id')
	g.db.execute('DELETE FROM books WHERE ID = ?', book_id)
	g.db.commit()
	flash("Deleted Book")
	return redirect(url_for('homepage'))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = "Invalid username"
			flash("Invalid username")
		elif request.form['password'] != app.config['PASSWORD']:
			error = "Invalid password"
			flash("Invalid password")
		else:
			session['logged_in'] = True
			flash("You are now logged in.")
			return redirect(url_for('homepage'))
	return render_template('login.html', error=error)
	
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash("You are now logged out")
	return redirect(url_for('homepage'))
	
@app.route('/')
def homepage():
	cur = g.db.execute('SELECT ID, ISBN, TITLE, AUTHOR, PAGECOUNT, AVERAGERATING, THUMBNAIL FROM books')
	books = [dict(id=row[0], isbn=row[1], title=row[2], author=row[3], pagecount=row[4], averagerating=row[5], thumbnail=row[6]) for row in cur.fetchall()]
	return render_template('index.html', books=books)
	
if __name__ == "__main__":
	app.run()
						
			
		
		
