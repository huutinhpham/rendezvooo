from flask import Blueprint, render_template, url_for, redirect, request, flash, session, jsonify
from passlib.hash import pbkdf2_sha256
from functools import wraps

from dbconnect import *
from my_util import *

import bleach

rendezvooo = Blueprint('rendezvooo', __name__, template_folder='templates', static_folder='static')

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("Please enter a playlist first")
			return redirect(url_for('homepage'))
	return wrap

@rendezvooo.route('/logout/')
@login_required
def logout():
	session.clear()
	return redirect(url_for('homepage'))

@rendezvooo.route('/how-it-works/')
def how_it_works():
	return render_template('how-it-works.html')

@rendezvooo.route('/', methods=['GET', 'POST'])
def homepage():
	error = ''
	form = AccessPlaylistForm(request.form)
	if session.get('pid'):
		return redirect(url_for('playlist', pid=session['pid']))
	elif request.method == 'POST' and form.validate():

		collaborator = bleach.clean(form.name.data)
		pid = bleach.clean(form.pid.data)
		encrypted_opt_pw = check_opt_pw(form.opt_pw.data)

		c, conn = connection()

		### VERIFY IF PLAYLIST EXISTS ###
		playlist = None
		playlist_error = None
		if len(pid) != 8:
			error = "The Playlist URL or playlist code is invalid. it should have exactly 8 characters."
			return render_template("homepage.html", error=error, form=form)
		else:
			playlist = GET_playlist_request(c, conn, pid)
			playlist_error = validate_playlist_request(playlist)

		### VERIFY USER IF USER IS NOT NEW ###
		is_name_exist = GET_collaborator_request(c, conn, pid, collaborator)
		collaborator_error = None
		if is_name_exist != None:
			collaborator_error = validate_collaborator_pass_request(is_name_exist[2], form.opt_pw.data)
		else:
			if (validate_collaborator_name_request(collaborator) is None):
				POST_collaborator_request(c, conn, pid, collaborator, encrypted_opt_pw, None)

		error = playlist_error or collaborator_error

		conn.close()
		if error is None:
			session['pid'] = pid
			session['collaborator'] = collaborator
			session['admin'] = False
			session['logged_in'] = True
			session['mode'] = 'order'
			if playlist[1] == collaborator:
				session['admin'] = True
			return redirect(url_for('playlist', pid=pid))
		return render_template("homepage.html", error=error, form=form)
	return render_template("homepage.html", form=form)

@rendezvooo.route('/generate-playlist/', methods=['GET', 'POST'])
def generate_playlist():
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
		session['mode'] = 'order'


		return redirect(url_for('playlist'))
	return render_template("generate-playlist.html", form=form)

@rendezvooo.route('/<pid>', methods=['GET', 'POST'])
def playlist(pid):
	if session.get('logged_in') is not True:
		form = AccessPlaylistForm(request.form)
		form.pid.data = pid
		return render_template('homepage.html', form=form)
	else:
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
		return render_template("playlist.html", pid=session['pid'])


@rendezvooo.route('/load_curr_song/', methods=['GET'])
@login_required
def load_curr_song():
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

#===== GET SONG functions return result song along with previous songs
@rendezvooo.route('/first_song/', methods=['GET'])
@login_required
def first_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']
		c, conn = connection()

		curr_song = GET_collaborator_request(c, conn, pid, collaborator)[3]
		song = GET_all_songs_request_sorted(c, conn, pid)[0][1]
		UPDATE_collaborator_song_request(c, conn, pid, collaborator, song)
		conn.close()
		return jsonify(curr_song, song)


@rendezvooo.route('/next_song/', methods=['GET'])
@login_required
def next_song():
	mode = session['mode']
	if mode == 'shuffle':
		return next_shuffle_song()
	return next_order_song()

def next_order_song():
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

def next_shuffle_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']

		c, conn = connection()
		curr_song = GET_collaborator_request(c, conn, pid, collaborator)[3]
		playlist_songs = GET_all_songs_request_sorted(c, conn, pid)

		playlist_len = len(playlist_songs)
		index = 0
		while True:
			index = int(round(random.uniform(0, 1)*playlist_len)) - 1
			if playlist_songs[index][1] != curr_song:
				break;

		UPDATE_collaborator_song_request(c, conn, pid, collaborator, playlist_songs[index][1])
		conn.close()
		return jsonify([curr_song, playlist_songs[index][1]])

@rendezvooo.route('/prev_song/', methods=['GET'])
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

@rendezvooo.route('/change_current_song/', methods=['POST'])
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

@rendezvooo.route('/change_mode/', methods=['POST'])
@login_required
def change_mode():
	if request.method == 'POST':
		curr_mode = request.form['curr_mode']
		if (curr_mode == 'shuffle'):
			session['mode'] = 'order'
		else:
	 		session['mode'] = 'shuffle'

@rendezvooo.route('/get_mode/', methods=['GET'])
@login_required
def get_mode():
	return jsonify(session['mode'])

@rendezvooo.route('/get_playlist_data/', methods=['GET'])
@login_required
def get_playlist_data():
	if request.method == 'GET':
		c, conn = connection()
		playlist_songs = GET_all_songs_request_sorted(c, conn, session['pid'])
		is_admin = session['admin']
		conn.close()
		return jsonify([is_admin, playlist_songs])

@rendezvooo.route('/get_collaborator/', methods=['GET'])
@login_required
def get_collaborator():
	collaborator = session['collaborator']
	is_admin = session['is_admin']
	return jsonify([is_admin, collaborator])

@rendezvooo.route('/delete_song/', methods=['POST'])
@login_required
def delete_song():
	if request.method == 'POST':
		c, conn = connection()
		yt_id = request.form['yt_id']
		pid = session['pid']
		DELETE_song_request(c, conn, pid, yt_id);
		conn.close()

@rendezvooo.route('/is_liked/', methods=['POST'])
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

@rendezvooo.route('/liked/', methods=['POST'])
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

@rendezvooo.route('/unliked/', methods=['POST'])
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

@rendezvooo.errorhandler(404)
def page_not_found(e):
    return str(e)

@rendezvooo.errorhandler(400)
def page_not_found(e):
    return str(e)

@rendezvooo.errorhandler(500)
def page_not_found(e):
    return str(e)
