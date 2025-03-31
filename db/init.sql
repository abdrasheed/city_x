-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- Create staging table for raw crime data
CREATE TABLE IF NOT EXISTS staging.raw_crime_data (
    id SERIAL PRIMARY KEY,
    district_id INTEGER,
    timestamp TIMESTAMP,
    crime_type TEXT,
    nearest_police_patrol TEXT
);

-- Create staging table for raw district data
CREATE TABLE IF NOT EXISTS staging.raw_district_data (
    id SERIAL PRIMARY KEY,
    district_id INTEGER,
    district TEXT,
    population INTEGER,
    governor TEXT
);

-- Create core table for transformed data
CREATE TABLE IF NOT EXISTS core.transformed_crime_data (
    id SERIAL PRIMARY KEY,
    district_id INTEGER NOT NULL,
    crime_type TEXT NOT NULL,
    nearest_police_patrol FLOAT NOT NULL,
    day_of_week TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    district_name TEXT NOT NULL,
    population INTEGER NOT NULL,
    governor TEXT NOT NULL
);
