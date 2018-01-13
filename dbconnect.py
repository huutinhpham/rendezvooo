import psycopg2

def connection():
    conn = psycopg2.connect(host="localhost",
                           user = "postgres",
                           password = "rendezvooo",
                           dbname = "rendezvooo")
    c = conn.cursor()

    return c, conn

def GET_song_request(c, conn, pid, yt_id):
	c.execute("SELECT * FROM song WHERE pid=(%s) AND yt_id=(%s)", (pid, yt_id))
	return c.fetchone()

def GET_all_songs_request_sorted(c, conn, pid):
	c.execute("SELECT * FROM song WHERE pid=(%s) ORDER BY vote DESC", (pid,))
	return c.fetchall()

def POST_song_request(c, conn, pid, yt_id, requester, vote):
	c.execute("INSERT INTO song (pid, yt_id, requester, vote) VALUES (%s, %s, %s, %s)", (pid, yt_id, requester, vote))
	conn.commit()

def DELETE_song_request(c, conn, pid, yt_id):
	c.execute("DELETE FROM song WHERE pid=(%s) AND yt_id=(%s)", (pid, yt_id))
	conn.commit()

def UPDATE_song_likes_request(c, conn, pid, yt_id, like):
	if (like):
		c.execute("UPDATE song SET vote = vote + 1 WHERE pid=(%s) AND yt_id=(%s)", (pid, yt_id))
	else:
		c.execute("UPDATE song SET vote = vote - 1 WHERE pid=(%s) AND yt_id=(%s)", (pid, yt_id))
	conn.commit()

def GET_playlist_request(c, conn, pid):
	c.execute("SELECT * FROM playlist WHERE pid=(%s)", (pid,))
	return c.fetchone()

def POST_playlist_request(c, conn, pid, admin_name, email, dirty):
	c.execute("INSERT INTO playlist (pid, admin_name, email, dirty) VALUES (%s, %s, %s, %s)", (pid, admin_name, email, dirty))
	conn.commit()

def GET_collaborator_request(c, conn, pid, collaborator):
	c.execute("SELECT * FROM collaborator WHERE pid=(%s) AND collaborator=(%s)", (pid, collaborator))
	return c.fetchone()

def POST_collaborator_request(c, conn, pid, collaborator, encrypted_opt_pw, current_song):
	c.execute("INSERT INTO collaborator (pid, collaborator, encrypted_opt_pw, current_song) VALUES (%s, %s, %s, %s)", (pid, collaborator, encrypted_opt_pw, current_song))
	conn.commit()

def UPDATE_collaborator_song_request(c, conn, pid, collaborator, current_song):
	c.execute("UPDATE collaborator SET current_song=(%s) WHERE pid=(%s) AND collaborator=(%s)", (current_song, pid, collaborator))
	conn.commit()

def GET_like_request(c, conn, pid, yt_id, collaborator):
	c.execute("SELECT * FROM vote WHERE pid=(%s) AND yt_id=(%s) AND collaborator=(%s)", (pid, yt_id, collaborator))
	return c.fetchone()

def POST_like_request(c, conn, pid, yt_id, collaborator):
	c.execute("INSERT INTO vote (pid, yt_id, collaborator) VALUES (%s, %s, %s)", (pid, yt_id, collaborator))
	conn.commit()

def DELETE_like_request(c, conn, pid, yt_id, collaborator):
	c.execute("DELETE FROM vote WHERE pid=(%s) AND yt_id=(%s) AND collaborator=(%s)", (pid, yt_id, collaborator))
	conn.commit()