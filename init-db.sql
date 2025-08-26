-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create geo_features table
CREATE TABLE IF NOT EXISTS geo_features (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geometry_type VARCHAR(50),
    geom GEOMETRY(GEOMETRY, 4326),
    properties JSONB,
    raw_geometry JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX IF NOT EXISTS idx_geo_features_geom ON geo_features USING GIST (geom);

-- Create index on geometry type for faster filtering
CREATE INDEX IF NOT EXISTS idx_geo_features_type ON geo_features (geometry_type);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_geo_features_name ON geo_features (name);

-- Create index on properties for JSON queries
CREATE INDEX IF NOT EXISTS idx_geo_features_properties ON geo_features USING GIN (properties);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_geo_features_updated_at 
    BEFORE UPDATE ON geo_features 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
INSERT INTO geo_features (name, geometry_type, geom, properties, raw_geometry) VALUES
(
    'Sample Point',
    'Point',
    ST_GeomFromGeoJSON('{"type": "Point", "coordinates": [-122.4194, 37.7749]}'),
    '{"name": "Sample Point", "description": "A sample point in San Francisco"}',
    '{"type": "Point", "coordinates": [-122.4194, 37.7749]}'
),
(
    'Sample Polygon',
    'Polygon',
    ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[-122.5, 37.7], [-122.4, 37.7], [-122.4, 37.8], [-122.5, 37.8], [-122.5, 37.7]]]}'),
    '{"name": "Sample Polygon", "description": "A sample polygon in San Francisco area"}',
    '{"type": "Polygon", "coordinates": [[[-122.5, 37.7], [-122.4, 37.7], [-122.4, 37.8], [-122.5, 37.8], [-122.5, 37.7]]]}'
);
