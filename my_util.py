from wtforms import Form, BooleanField, TextField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from dbconnect import *
import random, string

def generate_pid(c, conn, length):
	pid = ''
	while pid == '':
		pid = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for i in range(length))
		if GET_playlist_request(c, conn, pid) is not None:
			pid = ''
	return pid

def validate_song_request(is_pid_exist, is_song_exist, yt_id):
	error = None
	if is_pid_exist is None:
		error = 'That Playlist does not Exist, please create a Playlist First'
	elif is_song_exist is not None:
		error = 'That song has already been requested'
	elif len(yt_id) != 11:
		error = 'Please enter a valid YouTube URL'
	return error


class GeneratePlaylistForm(Form):
	email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
	password = PasswordField('New Playlist Password', [
		validators.Required(), 
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password')