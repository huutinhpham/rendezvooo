from wtforms import Form, BooleanField, TextField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from passlib.hash import pbkdf2_sha256
from dbconnect import *
import random, string

def generate_pid(c, conn, length):
	pid = ''
	while pid == '':
		pid = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for i in range(length))
		if GET_playlist_request(c, conn, pid) is not None:
			pid = ''
	return pid

def trim_pid(pid):
	return ''.join(pid.split())

def validate_playlist_request(is_pid_exist):
	error = None
	if is_pid_exist is None:
		error='That playlist does not exist. Forgot playlist code?'
	return error

def validate_song_request(is_pid_exist, is_song_exist, yt_id):
	error = validate_playlist_request(is_pid_exist)
	if is_song_exist is not None:
		error = 'That song has already been requested'
	elif len(yt_id) != 11:
		error = 'Please enter a valid YouTube URL'
	return error

def validate_name_request(collaborator, db_encrypted_opt_pw, password):
	error = None
	if db_encrypted_opt_pw == None and password != '':
		error = "Name is taken. Please try again"
	if (db_encrypted_opt_pw != None) and not (pbkdf2_sha256.verify(password, db_encrypted_opt_pw)):
		error = "Password is incorrect, or name is taken. Please try again."
	return error


def check_opt_pw(opt_pw):
	if opt_pw != '':
		return pbkdf2_sha256.encrypt((str(opt_pw)))
	return None


class AccessPlaylistForm(Form):
	name = TextField('Name')
	pid = TextField('Playlist Code')
	opt_pw = PasswordField('Password (Optional)')


class GeneratePlaylistForm(Form):
	email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
	password = PasswordField('New Playlist Password', [
		validators.Required(), 
		validators.EqualTo('confirm', message='Passwords must match'),
		validators.Length(min=7)
	])
	confirm = PasswordField('Confirm Password')