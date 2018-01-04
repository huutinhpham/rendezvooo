from wtforms import Form, BooleanField, TextField, PasswordField, validators
from wtforms.fields.html5 import EmailField
import random, string

def random_playlist_id(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for i in range(length))

def validate_song_request(pid_exist, ytid, song_exist):
	error = None
	if pid_exist is not None:
		error = 'That Playlist does not Exist, please create a Playlist First'
	elif song_exist is not None:
		error = 'That song has already been requested'
	elif len(ytId) != 11:
		error = 'Please enter a valid YouTube URL'
	return error


class GeneratePlaylistForm(Form):
	email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
	password = PasswordField('New Playlist Password', [
		validators.Required(), 
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password')