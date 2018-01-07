from flask import Flask, render_template, url_for, redirect, request, flash, session, jsonify
from passlib.hash import sha256_crypt

from dbconnect import *
from my_util import *

import bleach, random, string

app = Flask(__name__)

@app.route('/test/')
def test():
	return "test homie"

@app.route('/', methods=['GET', 'POST'])
def homepage():
	try:
		c, conn = connection()
		if request.method == 'POST':

			pid = bleach.clean(request.form['pid'])
			pid = trim_pid(pid)

			is_pid_exist = GET_playlist_request(c, conn, pid)
			error = validate_playlist_request(is_pid_exist)
			response = error
			if error is None:
				session['pid'] = pid
				session['playlist'] = True
				session['admin'] = False
				response={'redirect': 1, 'redirect_url': '/playlist/'}
			return jsonify(response)
	except Exception as e:
		return str(e)
	return render_template("homepage.html")

@app.route('/generate-playlist/', methods=['GET', 'POST'])
def generate_playlist():
	try:
		form = GeneratePlaylistForm(request.form)	
		if request.method == "POST" and form.validate():
			email = bleach.clean(form.email.data)
			playlist_pw = sha256_crypt.encrypt((str(form.password.data)))

			c, conn = connection()
			pid = generate_pid(c, conn, 8)
			POST_playlist_request(c, conn, pid, playlist_pw, email, False)
			conn.close()

			session['admin'] = True
			session['pid'] = pid

			return jsonify(pid=pid)

	except Exception as e:
		flash(e)
	return render_template("generate-playlist.html", form=form)

@app.route('/playlist/', methods=['GET', 'POST'])
def playlist():
	try:
		c, conn = connection()
		if request.method == 'POST':

			yt_id = bleach.clean(request.form['yt_id'])
			pid = session['pid']

			is_pid_exist = GET_playlist_request(c, conn, pid)
			is_song_exist = GET_song_request(c, conn, pid, yt_id)
			error = validate_song_request(is_pid_exist, is_song_exist, yt_id)
			if error is None: 
				POST_song_request(c, conn, pid, yt_id, 0)
				error = 'your song request has been added'
			return jsonify(error=error)
		conn.close()
	except Exception as e:
		flash(e)
	return render_template("playlist.html")

@app.route('/_get_all_songs/', methods=['GET'])
def _get_all_songs():
	c, conn = connection()
	if request.method == 'GET':
		pid = session['pid']
		result = GET_all_songs_request(c, conn, pid)
		return jsonify(result=result)


@app.errorhandler(500)
def internal_server_error(e):
	return str(e)

@app.errorhandler(400)
def internal_server_error(e):
	return str(e)





if __name__ == "__main__":
    app.run(debug=True)
