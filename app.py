from flask import Flask, render_template
from dotenv import load_dotenv
import psycopg2
import os

app = Flask(__name__)


# Load variables from .env into the environment
load_dotenv()

# Now you can access them using os.getenv or os.environ
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', 5432),  # fallback to 5432
}



def get_tours():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM tour where onlineregtype=2 and inactive IS NOT TRUE and deleted IS NOT TRUE ")
    rows = cur.fetchall()
    print(rows)
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

@app.route("/")
def tour_list():
    tours = get_tours()
    return render_template("tours.html", tours=tours)

if __name__ == "__main__":
    app.run(debug=True)
