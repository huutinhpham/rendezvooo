from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/generate-playlist/')
def generate_playlist():
	return render_template("generate-playlist.html")

@app.route('/playlist/')
def playlist():
	return render_template("playlist.html")




if __name__ == "__main__":
    app.run()
