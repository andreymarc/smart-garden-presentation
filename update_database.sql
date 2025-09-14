-- Drop the existing table if it exists
DROP TABLE IF EXISTS sensor_data;

-- Create the new sensor_data table for air quality monitoring
CREATE TABLE sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    gas FLOAT,
    reducing FLOAT,
    nh3 FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on timestamp for faster queries
CREATE INDEX idx_timestamp ON sensor_data(timestamp);

-- Add some sample data
INSERT INTO sensor_data (timestamp, temperature, humidity, pressure, gas, reducing, nh3)
VALUES 
    (NOW(), 22.5, 45.0, 1013.25, 250000, 150000, 75000),
    (NOW() - INTERVAL 5 MINUTE, 23.0, 46.0, 1013.20, 245000, 148000, 74000),
    (NOW() - INTERVAL 10 MINUTE, 22.8, 44.5, 1013.30, 252000, 152000, 76000); 