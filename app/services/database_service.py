import os
import logging
import json
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for handling database operations with PostgreSQL/PostGIS"""
    
    def __init__(self):
        self.connection: Optional[connection] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Database configuration from environment variables
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'geospatial'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'sslmode': os.getenv('DB_SSLMODE', 'prefer')
        }
    
    async def connect(self):
        """Establish database connection"""
        try:
            # Run connection in thread pool since psycopg2 is synchronous
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(
                self.executor, 
                self._create_connection
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish database connection: {e}")
            raise
    
    def _create_connection(self) -> connection:
        """Create synchronous database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    self.connection.close
                )
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
    
    async def create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist"""
        create_tables_sql = """
        -- Enable PostGIS extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS postgis;
        
        -- Drop and recreate geo_features table to ensure correct schema
        DROP TABLE IF EXISTS geo_features CASCADE;
        
        -- Create geo_features table
        CREATE TABLE geo_features (
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
        CREATE INDEX idx_geo_features_geom ON geo_features USING GIST (geom);
        
        -- Create index on geometry type for faster filtering
        CREATE INDEX idx_geo_features_type ON geo_features (geometry_type);
        
        -- Create index on name for faster searches
        CREATE INDEX idx_geo_features_name ON geo_features (name);
        
        -- Create index on properties for JSON queries
        CREATE INDEX idx_geo_features_properties ON geo_features USING GIN (properties);
        """
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._execute_sql,
                create_tables_sql
            )
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def _execute_sql(self, sql: str, params: tuple = None):
        """Execute SQL statement synchronously"""
        if not self.connection:
            raise Exception("No database connection")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            return cursor
        except Exception as e:
            self.connection.rollback()
            logger.error(f"SQL execution failed: {e}")
            raise
    
    async def insert_feature(self, feature: Dict[str, Any]) -> int:
        """
        Insert a GeoJSON feature into the database
        
        Args:
            feature: Validated GeoJSON feature
            
        Returns:
            ID of the inserted feature
        """
        try:
            # Extract feature data
            feature_data = await self._extract_feature_data(feature)
            
            # Insert into database
            insert_sql = """
            INSERT INTO geo_features (name, geometry_type, geom, properties, raw_geometry)
            VALUES (%s, %s, ST_GeomFromGeoJSON(%s), %s, %s)
            RETURNING id
            """
            
            params = (
                feature_data['name'],
                feature_data['geometry_type'],
                json.dumps(feature_data['raw_geometry']),
                json.dumps(feature_data['properties']),
                json.dumps(feature_data['raw_geometry'])
            )
            
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(
                self.executor,
                self._execute_sql,
                insert_sql,
                params
            )
            
            feature_id = cursor.fetchone()[0]
            logger.info(f"Feature inserted successfully with ID: {feature_id}")
            return feature_id
            
        except Exception as e:
            logger.error(f"Failed to insert feature: {e}")
            raise
    
    async def _extract_feature_data(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from feature for database insertion"""
        geometry = feature['geometry']
        properties = feature.get('properties', {})
        
        # Extract name from properties
        name = properties.get('name', properties.get('NAME', properties.get('id', 'Unknown')))
        
        return {
            'name': name,
            'geometry_type': geometry['type'],
            'properties': properties,
            'raw_geometry': geometry
        }
    
    async def get_feature_count(self) -> int:
        """Get total count of features in database"""
        try:
            count_sql = "SELECT COUNT(*) FROM geo_features"
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(
                self.executor,
                self._execute_sql,
                count_sql
            )
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get feature count: {e}")
            return 0
    
    async def get_features_by_type(self, geometry_type: str, limit: int = 100) -> list:
        """Get features by geometry type"""
        try:
            query_sql = """
            SELECT id, name, geometry_type, ST_AsGeoJSON(geom) as geom, properties
            FROM geo_features 
            WHERE geometry_type = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(
                self.executor,
                self._execute_sql,
                query_sql,
                (geometry_type, limit)
            )
            
            features = []
            for row in cursor.fetchall():
                features.append({
                    'id': row[0],
                    'name': row[1],
                    'geometry_type': row[2],
                    'geometry': json.loads(row[3]),
                    'properties': row[4]
                })
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to get features by type: {e}")
            return []
