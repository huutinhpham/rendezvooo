from flask import Flask, render_template, url_for, redirect, request, flash, session, jsonify
from passlib.hash import pbkdf2_sha256
from functools import wraps

from dbconnect import *
from my_util import *

import bleach, random, string

app = Flask(__name__)

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("Please enter a playlist first")
			return redirect(url_for('homepage'))
	return wrap

@app.route('/logout/')
@login_required
def logout():
	session.clear()
	return redirect(url_for('homepage'))

@app.route('/how-it-works/')
def how_it_works():
	return render_template('how-it-works.html')

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
			playlist = None
			playlist_error = None
			if len(pid) != 8:
				error = "Playlist Code should have exactly 8 characters."
				return render_template("homepage.html", error=error, form=form)
			else:
				playlist = GET_playlist_request(c, conn, pid)
				playlist_error = validate_playlist_request(playlist)

			### VERIFY USER IF USER IS NOT NEW ###
			is_name_exist = GET_collaborator_request(c, conn, pid, collaborator)
			collaborator_error = None
			if is_name_exist != None:
				collaborator_error = validate_name_request(collaborator, is_name_exist[2], form.opt_pw.data)
			else:
				POST_collaborator_request(c, conn, pid, collaborator, encrypted_opt_pw, None)

			error = playlist_error or collaborator_error
			conn.close()

			if error is None:
				session['pid'] = pid
				session['collaborator'] = collaborator
				session['admin'] = False
				session['logged_in'] = True
				if playlist[1] == collaborator:
					session['admin'] = True
				return redirect(url_for('playlist'))
			return render_template("homepage.html", error=error, form=form)
	except Exception as e:
		flash(e)

	return render_template("homepage.html", error=error, form=form)

@app.route('/generate-playlist/', methods=['GET', 'POST'])
def generate_playlist():
	try:
		form = GeneratePlaylistForm(request.form)	
		if request.method == "POST" and form.validate():
			collaborator = bleach.clean(form.name.data)
			email = bleach.clean(form.email.data)
			encrypted_pw = pbkdf2_sha256.encrypt((str(form.password.data)))

			c, conn = connection()
			pid = generate_pid(c, conn, 8)
			POST_playlist_request(c, conn, pid, collaborator, email, False)
			POST_collaborator_request(c, conn, pid, collaborator, encrypted_pw, None)
			conn.close()

			session['logged_in'] = True
			session['pid'] = pid
			session['admin'] = True
			session['collaborator'] = collaborator


			return redirect(url_for('playlist'))

	except Exception as e:
		flash(e)
	return render_template("generate-playlist.html", form=form)

@app.route('/playlist/', methods=['GET', 'POST'])
@login_required
def playlist():
	try:
		c, conn = connection()
		if request.method == 'POST':

			yt_id = bleach.clean(request.form['yt_id'])
			pid = session['pid']
			collaborator = session['collaborator']

			is_pid_exist = GET_playlist_request(c, conn, pid)
			is_song_exist = GET_song_request(c, conn, pid, yt_id)
			error = validate_song_request(is_pid_exist, is_song_exist, yt_id)
			if error is None: 
				POST_song_request(c, conn, pid, yt_id, collaborator, 0)
				error = 'your song request has been added'
			return jsonify(error=error)
		conn.close()
	except Exception as e:
		flash(e)
	return render_template("playlist.html", pid=session['pid'])

@app.route('/load_first_song/', methods=['GET'])
@login_required
def load_first_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']
		c, conn = connection()
		song = GET_collaborator_request(c, conn, pid, collaborator)[3]

		#initial request, where collaborator has no current song
		if song is None:
			playlist_songs = GET_all_songs_request_sorted(c, conn, pid)
			if len(playlist_songs) > 0:
				song = playlist_songs[0][1]
				UPDATE_collaborator_song_request(c, conn, pid, collaborator, song)
		conn.close()
		return jsonify(song)

#get next song, return current song along with next song
@app.route('/next_song/', methods=['GET'])
@login_required
def next_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']

		c, conn = connection()
		curr_song = GET_collaborator_request(c, conn, pid, collaborator)[3]
		playlist_songs = GET_all_songs_request_sorted(c, conn, pid)

		index = 0;
		for song in playlist_songs:
			index += 1
			if song[1] == curr_song:
				break
		if index >= len(playlist_songs):
			index = 0

		UPDATE_collaborator_song_request(c, conn, pid, collaborator, playlist_songs[index][1])
		conn.close()
		return jsonify([curr_song, playlist_songs[index][1]])

@app.route('/prev_song/', methods=['GET'])
@login_required
def prev_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']

		c, conn = connection()
		curr_song = GET_collaborator_request(c, conn, pid, collaborator)[3]
		playlist_songs = GET_all_songs_request_sorted(c, conn, pid)

		index = 0;
		for song in playlist_songs:
			if song[1] == curr_song:
				index -= 1;
				break
			index += 1
		if index < 0:
			index = len(playlist_songs) - 1

		UPDATE_collaborator_song_request(c, conn, pid, collaborator, playlist_songs[index][1])
		conn.close()
		return jsonify([curr_song, playlist_songs[index][1]])

#update the current song and return previous song
@app.route('/change_current_song/', methods=['POST'])
@login_required
def change_current_song():
	if request.method == 'POST':
		c, conn = connection()
		collaborator = session['collaborator']
		yt_id = request.form['yt_id']
		pid = session['pid']
		previousSong = GET_collaborator_request(c, conn, pid, collaborator)[3]
		UPDATE_collaborator_song_request(c, conn, pid, collaborator, yt_id)
		conn.close()
		return jsonify(previousSong)


#Returns admin status along with songs within the playlist
@app.route('/get_playlist_data/', methods=['GET'])
@login_required
def get_playlist_data():
	if request.method == 'GET':
		c, conn = connection()
		playlist_songs = GET_all_songs_request_sorted(c, conn, session['pid'])
		is_admin = session['admin']
		conn.close()
		return jsonify([is_admin, playlist_songs])

@app.route('/get_collaborator/', methods=['GET'])
@login_required
def get_collaborator():
	collaborator = session['collaborator']
	is_admin = session['is_admin']
	return jsonify([is_admin, collaborator])

@app.route('/delete_song/', methods=['POST'])
@login_required
def delete_song():
	if request.method == 'POST':
		c, conn = connection()
		yt_id = request.form['yt_id']
		pid = session['pid']
		DELETE_song_request(c, conn, pid, yt_id);
		conn.close()

@app.route('/is_liked/', methods=['POST'])
@login_required
def is_liked():
	if request.method == 'POST':
		c, conn = connection()
		pid = session['pid']
		collaborator = session['collaborator']
		yt_id = bleach.clean(request.form['yt_id'])
		is_like_exist = GET_like_request(c, conn, pid, yt_id, collaborator)
		conn.close()
		if is_like_exist is None:
			return jsonify(False)
		return jsonify(True)


@app.route('/liked/', methods=['POST'])
@login_required
def liked():
	if request.method == 'POST':
		c, conn = connection()
		pid = session['pid']
		collaborator = session['collaborator']
		yt_id = bleach.clean(request.form['yt_id'])

		is_like_exist = GET_like_request(c, conn, pid, yt_id, collaborator)
		if is_like_exist is None:
			UPDATE_song_likes_request(c, conn, pid, yt_id, 1)
			POST_like_request(c, conn, pid, yt_id, collaborator)

		likes = GET_song_request(c, conn, pid, yt_id)[2]
		conn.close()
		return jsonify(likes)

@app.route('/unliked/', methods=['POST'])
@login_required
def unliked():
	if request.method == 'POST':
		c, conn = connection()
		pid = session['pid']
		collaborator = session['collaborator']
		yt_id = bleach.clean(request.form['yt_id'])

		is_like_exist = GET_like_request(c, conn, pid, yt_id, collaborator)
		if is_like_exist is not None:
			UPDATE_song_likes_request(c, conn, pid, yt_id, 0)
			DELETE_like_request(c, conn, pid, yt_id, collaborator)

		likes = GET_song_request(c, conn, pid, yt_id)[2]
		conn.close()
		return jsonify(likes)


@app.errorhandler(500)
def internal_server_error(e):
	return str(e)

@app.errorhandler(400)
def internal_server_error(e):
	return str(e)

if __name__ == "__main__":
    app.run()
