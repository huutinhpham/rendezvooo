from flask import Flask, render_template, url_for, redirect, request, flash, session, jsonify
from passlib.hash import pbkdf2_sha256

from dbconnect import *
from my_util import *

import bleach, random, string

app = Flask(__name__)

@app.route('/test/')
def test():
	return "test homie"

@app.route('/', methods=['GET', 'POST'])
def homepage():
	error = ''
	try:
		form = AccessPlaylistForm(request.form)

		if request.method == 'POST' and form.validate():

			collaborator = bleach.clean(form.name.data)
			pid = trim_pid(bleach.clean(form.pid.data))
			encrypted_opt_pw = check_opt_pw(form.opt_pw.data)

			c, conn = connection()

			### VERIFY IF PLAYLIST EXISTS ###
			playlist_error = None
			if len(pid) != 8:
				error = "Playlist Code should have exactly 8 characters."
				return render_template("homepage.html", error=error, form=form)
			else:
				is_pid_exist = GET_playlist_request(c, conn, pid)
				playlist_error = validate_playlist_request(is_pid_exist)

			### VERIFY USER IF USER IS NOT NEW ###
			is_name_exist = GET_collaborator_request(c, conn, pid, collaborator)
			collaborator_error = None
			if is_name_exist != None:
				collaborator_error = validate_name_request(collaborator, is_name_exist[2], form.opt_pw.data)
			else:
				POST_collaborator_request(c, conn, pid, collaborator, encrypted_opt_pw)

			error = playlist_error or collaborator_error
			conn.close()

			if error is None:
				session['pid'] = pid
				session['collaborator'] = collaborator
				session['admin'] = False
				return redirect(url_for('playlist'))
	except Exception as e:
		flash(e)

	return render_template("homepage.html", error=error, form=form)

@app.route('/generate-playlist/', methods=['GET', 'POST'])
def generate_playlist():
	try:
		form = GeneratePlaylistForm(request.form)	
		if request.method == "POST" and form.validate():
			email = bleach.clean(form.email.data)
			playlist_pw = pbkdf2_sha256.encrypt((str(form.password.data)))

			c, conn = connection()
			pid = generate_pid(c, conn, 8)
			POST_playlist_request(c, conn, pid, playlist_pw, email, False)
			conn.close()

			session['pid'] = pid
			session['admin'] = False

			return redirect(url_for('playlist'))

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
	return render_template("playlist.html", pid=session['pid'])

def _get_all_songs_sorted():
	c, conn = connection()
	pid = session['pid']
	result = GET_all_songs_request_sorted(c, conn, pid)
	conn.close()
	return result

@app.route('/get_all_songs_sorted/', methods=['GET'])
def get_all_JSON_songs_sorted():
	if request.method == 'GET':
		return jsonify(_get_all_songs_sorted())

@app.route('/get_top_song/', methods=['GET'])
def get_top_song():
	if request.method == 'GET':
		return jsonify(_get_all_songs_sorted()[0])

@app.route('/liked/', methods=['POST'])
def liked():
	c, conn = connection()
	if request.method == 'POST':
		pid = session['pid']
		collaborator = session['collaborator']
		yt_id = bleach.clean(request.form['yt_id'])

		is_like_exist = GET_like_request(c, conn, pid, yt_id, collaborator)
		if is_like_exist is None:
			UPDATE_song_likes_request(c, conn, pid, yt_id)
			POST_like_request(c, conn, pid, yt_id, collaborator)
			
		conn.close()

@app.errorhandler(500)
def internal_server_error(e):
	return str(e)

@app.errorhandler(400)
def internal_server_error(e):
	return str(e)

if __name__ == "__main__":
    app.run()
