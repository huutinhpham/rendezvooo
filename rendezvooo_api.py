from flask import Blueprint, request, session, jsonify
from functools import wraps

from dbconnect import *
from my_util import validate_song_request

import bleach


rendezvooo_api = Blueprint(
				'rendezvooo_api',
				__name__,
				template_folder='templates',
				static_folder='static')
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session.get('logged_in'):
			return f(*args, **kwargs)
		else:
			flash("Please enter a playlist first")
			return redirect(url_for('rendezvooo.homepage'))
	return wrap

@rendezvooo_api.route('/request_song/', methods=['POST'])
def request_song():
	if request.method == 'POST':
		c, conn = connection()
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
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID'

##### SONG GETTER FUNCTIONS #####
@rendezvooo_api.route('/get_curr_song/', methods=['GET'])
@login_required
def get_curr_song():
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
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

@rendezvooo_api.route('/get_first_song/', methods=['GET'])
@login_required
def get_first_song():
	if request.method == 'GET':
		pid = session['pid']
		collaborator = session['collaborator']
		c, conn = connection()

		curr_song = GET_collaborator_request(c, conn, pid, collaborator)[3]
		song = GET_all_songs_request_sorted(c, conn, pid)[0][1]
		UPDATE_collaborator_song_request(c, conn, pid, collaborator, song)
		conn.close()
		return jsonify(curr_song, song)
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

@rendezvooo_api.route('/get_next_song/', methods=['GET'])
@login_required
def get_next_song():
	if request.method == 'GET':
		mode = session['mode']
		if mode == 'shuffle':
			return next_shuffle_song()
		return next_order_song()
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

def next_order_song():
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

@rendezvooo_api.route('/get_prev_song/', methods=['GET'])
@login_required
def get_prev_song():
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
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

##### PLAYLIST INFO GETTER FUNCTIONS #####
@rendezvooo_api.route('/get_mode/', methods=['GET'])
@login_required
def get_mode():
	if request.method == 'GET':
		return jsonify(session['mode'])
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

@rendezvooo_api.route('/get_playlist_data/', methods=['GET'])
@login_required
def get_playlist_data():
	try:
		if request.method == 'GET':
			c, conn = connection()

			playlist_songs = GET_all_songs_request_sorted(c, conn, session['pid'])
			is_admin = session['is_admin']
			conn.close()
			return jsonify([is_admin, playlist_songs])
		return 'ERROR: ONLY GET METHOD IS ALLOWED'
	except Exception as e:
		return str(e)

@rendezvooo_api.route('/get_collaborator/', methods=['GET'])
@login_required
def get_collaborator():
	if request.method == 'GET':
		collaborator = session['collaborator']
		is_admin = session['is_admin']
		return jsonify([is_admin, collaborator])
	return 'ERROR: ONLY GET METHOD IS ALLOWED'

##### UPDATE FUNCTIONS #####
@rendezvooo_api.route('/change_current_song/', methods=['POST'])
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
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID TO CHANGE SONG'

@rendezvooo_api.route('/delete_song/', methods=['POST'])
@login_required
def delete_song():
	if request.method == 'POST':
		c, conn = connection()
		yt_id = request.form['yt_id']
		pid = session['pid']
		DELETE_song_request(c, conn, pid, yt_id);
		conn.close()
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID TO DELETE SONG'

@rendezvooo_api.route('/change_mode/', methods=['POST'])
@login_required
def change_mode():
	if request.method == 'POST':
		curr_mode = request.form['curr_mode']
		if (curr_mode == 'shuffle'):
			session['mode'] = 'order'
		else:
			session['mode'] = 'shuffle'
		return 'success'
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES PREVIOUS MODE'

##### LIKING SONG FUNCTIONS #####

@rendezvooo_api.route('/is_liked/', methods=['POST'])
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
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID TO CHECK FOR LIKES'

@rendezvooo_api.route('/liked/', methods=['POST'])
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

		likes = GET_song_request(c, conn, pid, yt_id)[3]
		conn.close()
		return jsonify(likes)
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID TO LIKE SONG'

@rendezvooo_api.route('/unliked/', methods=['POST'])
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

		likes = GET_song_request(c, conn, pid, yt_id)[3]
		conn.close()
		return jsonify(likes)
	return 'ERROR: ONLY POST METHOD IS ALLOWED, REQUIRES YOUTUBE ID TO UNLIKE SONG'