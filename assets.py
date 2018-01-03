from wtforms import Form, BooleanField, TextField, PasswordField, validators
from wtforms.fields.html5 import EmailField



class GeneratePlaylistForm(Form):
	email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
	password = PasswordField('New Playlist Password', [
		validators.Required(), 
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password')