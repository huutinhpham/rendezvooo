import psycopg2

def connection():
    conn = psycopg2.connect(host="localhost",
                           user = "postgres",
                           password = "rendezvooo",
                           dbname = "rendezvooo")
    c = conn.cursor()

    return c, conn

def GET_song_request(c, conn, pid, yt_id):
	c.execute("SELECT * FROM song WHERE pid = (%s) AND yt_id = (%s)", (pid, yt_id))
	return c.fetchone()

def GET_all_songs_request_sorted(c, conn, pid):
	c.execute("SELECT * FROM song WHERE pid =(%s) ORDER BY vote ASC", (pid,))
	return c.fetchall()

def POST_song_request(c, conn, pid, yt_id, vote):
	c.execute("INSERT INTO song (pid, yt_id, vote) VALUES (%s, %s, %s)", (pid, yt_id, vote))
	conn.commit()

def GET_playlist_request(c, conn, pid):
	c.execute("SELECT * FROM playlist WHERE pid = (%s)", (pid,))
	return c.fetchone()

def POST_playlist_request(c, conn, pid, playlist_pw, email, dirty):
	c.execute("INSERT INTO playlist (pid, playlist_pw, email, dirty) VALUES (%s, %s, %s, %s)", (pid, playlist_pw, email, dirty))
	conn.commit()