CREATE TABLE IF NOT EXISTS stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(20),
    nom VARCHAR(255),
    adresse VARCHAR(255),
    ville VARCHAR(100),
    departement VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    carburant VARCHAR(20),
    prix FLOAT,
    date_maj TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT prix_unique UNIQUE (station_id, carburant, date_maj)
);
