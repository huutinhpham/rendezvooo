from flask import Blueprint, render_template, url_for, redirect, request, flash, session, jsonify
from passlib.hash import pbkdf2_sha256
from functools import wraps

from dbconnect import *
from my_util import *

import bleach

rendezvooo = Blueprint(
				'rendezvooo',
				__name__,
				template_folder='templates',
				static_folder='static')

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("Please enter a playlist first")
			return redirect(url_for('rendezvooo.homepage'))
	return wrap

@rendezvooo.route('/logout/')
@login_required
def logout():
	session.clear()
	return redirect(url_for('rendezvooo.homepage'))

@rendezvooo.route('/how-it-works/')
def how_it_works():
	return render_template('how-it-works.html')

@rendezvooo.route('/', methods=['GET', 'POST'])
def homepage():
	error = ''
	form = AccessPlaylistForm(request.form)
	# USER IS LOGGED IN
	if (session.get('pid')) and (session.get('logged_in') == True):
		return redirect(url_for('rendezvooo.playlist', pid=session['pid']))

	# USER ATTEMPTING TO LOGIN
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
			session['is_admin'] = False
			session['logged_in'] = True
			session['mode'] = 'order'
			if playlist[1] == collaborator:
				session['is_admin'] = True
			return redirect(url_for('rendezvooo.playlist', pid=pid))

	return render_template("homepage.html", error=error, form=form)

@rendezvooo.route('/<pid>', methods=['GET', 'POST'])
def playlist(pid):
	if session.get('logged_in') is not True:
		form = AccessPlaylistForm(request.form)
		form.pid.data = pid
		return render_template('homepage.html', form=form)
	else:
		return render_template("playlist.html", pid=session['pid'])


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
		session['is_admin'] = True
		session['collaborator'] = collaborator
		session['mode'] = 'order'


		return redirect(url_for('rendezvooo.playlist', pid=pid))
	return render_template("generate-playlist.html", form=form)

@rendezvooo.errorhandler(404)
def page_not_found(e):
    return str(e)

@rendezvooo.errorhandler(400)
def page_not_found(e):
    return str(e)

@rendezvooo.errorhandler(500)
def page_not_found(e):
    return str(e)
