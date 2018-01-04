import psycopg2

def connection():
    conn = psycopg2.connect(host="localhost",
                           user = "postgres",
                           password = "rendezvooo",
                           dbname = "rendezvooo")
    c = conn.cursor()

    return c, conn

def GET_song_request(c, conn, pid, ytid):
	c.execute("SELECT * FROM song WHERE pid = (%s) AND ytid = (%s)", (pid, ytid))
	return c.fetchone()

def POST_song_request(c, conn, pid, ytid, vote):
	c.execute("INSERT INTO song (pid, ytid, vote) VALUES (%s, %s, %s)", (pid, ytId, vote))

def GET_playlist_request(c, conn, pid):
	c.execute("SELECT * FROM playlist WHERE pid = (%s)", (pid,))
	return c.fetchone()

def POST_playlist_request(c, conn, pid, admin_pw, email, dirty):
	c.execute("INSERT INTO playlist (pid, playlist_pw, email, dirty) VALUES (%s, %s, %s, %s)", (pid, playlist_pw, email, dirty))