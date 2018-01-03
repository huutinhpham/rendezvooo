import psycopg2

def connection():
    conn = psycopg2.connect(host="localhost",
                           user = "postgres",
                           password = "rendezvooo",
                           dbname = "rendezvooo")
    c = conn.cursor()

    return c, conn