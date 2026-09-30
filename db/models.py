import os
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=5432,
        database="carburant",
        user="younes",
        password="carburant123",
    )
