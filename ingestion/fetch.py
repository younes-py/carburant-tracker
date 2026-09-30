import requests
from psycopg2.extras import execute_values
from db.models import get_connection

URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/json"
CARBURANTS = ["gazole", "sp95", "sp98", "e10", "e85", "gplc"]


def fetch_stations():
    response = requests.get(URL, timeout=120)
    response.raise_for_status()
    return response.json()


def to_rows(stations):
    rows = []
    for station in stations:
        geom = station.get("geom") or {}
        for carburant in CARBURANTS:
            prix = station.get(f"{carburant}_prix")
            if prix is None:
                continue
            rows.append((
                str(station["id"]),
                station.get("adresse"),
                station.get("ville"),
                station.get("code_departement"),
                geom.get("lat"),
                geom.get("lon"),
                carburant,
                prix,
                station.get(f"{carburant}_maj"),
            ))
    return rows


def load(rows):
    connection = get_connection()
    cursor = connection.cursor()
    execute_values(
        cursor,
        """
        INSERT INTO stations (station_id, adresse, ville, departement, latitude, longitude, carburant, prix, date_maj)
        VALUES %s
        ON CONFLICT (station_id, carburant, date_maj) DO NOTHING
        """,
        rows,
    )
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    stations = fetch_stations()
    rows = to_rows(stations)
    load(rows)
    print(f"{len(stations)} stations récupérées, {len(rows)} prix chargés")
    