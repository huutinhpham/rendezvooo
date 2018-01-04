from flask import Flask, render_template, url_for, redirect, request, flash, session
from dbconnect import connection
from passlib.hash import sha256_crypt
from assets import GeneratePlaylistForm

import bleach, random, string

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/generate-playlist/', methods=['GET', 'POST'])
def generate_playlist():
	try:
		form = GeneratePlaylistForm(request.form)
		
		if request.method == "POST" and form.validate():
			email = bleach.clean(form.email.data)
			playlist_pw = sha256_crypt.encrypt((str(form.password.data)))
			pid = ''

			c, conn = connection()

			while pid == '':
				pid = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for i in range(8))
				c.execute("SELECT * FROM Playlist WHERE pid = (%s)", (pid,))
				if c.fetchone() is not None:
					pid = ''

			c.execute("INSERT INTO Playlist (pid, playlist_pw, email, dirty) VALUES (%s, %s, %s, %s)", (pid, playlist_pw, email, False))
			conn.commit()
			conn.close
			session['admin'] = True
			session['pid'] = pid

			flash("Your New Playlist Code is " + pid)
			return redirect(url_for('homepage'))

	except Exception as e:
		flash(e)
	return render_template("generate-playlist.html", form=form)

@app.route('/playlist/', methods=['GET', 'POST'])
def playlist():
	error = ''
	try:
		c, conn = connection()
		if request.method == 'POST':
			ytId = bleach.clean(request.form['yt_id'])
			pid = '12345678'

			c.execute("SELECT * FROM Playlist WHERE pid = (%s)", (pid,))
			dbpid = 'hello'
			c.execute("SELECT * FROM Song WHERE pid = (%s) AND ytid = (%s)", (pid, ytId))
			song = c.fetchone()

			if dbpid is None:
				error = 'That Playlist does not Exist, please create a Playlist First'
			elif song is not None:
				error = 'That song has already been requested'
			elif len(ytId) != 11:
				error = 'please enter a valid YouTube URL'
			else:
				c.execute("INSERT INTO Song (pid, ytid, vote) VALUES (%s, %s, %s)", (pid, ytId, 0))
				conn.commit()
		conn.close()
		return render_template("playlist.html")
	except Exception as e:
		flash(e)
	return render_template("playlist.html")

@app.errorhandler(500)
def internal_server_error(e):
	return str(e)




if __name__ == "__main__":
    app.run()
