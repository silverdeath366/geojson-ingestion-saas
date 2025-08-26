import json
import logging
from typing import Dict, Any, List
from shapely.geometry import shape, Point, Polygon, LineString
from shapely.validation import explain_validity
import geojson

logger = logging.getLogger(__name__)

class GeoJSONService:
    """Service for handling GeoJSON validation and parsing"""
    
    def __init__(self):
        self.supported_geometry_types = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']
    
    def parse_geojson(self, geojson_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate GeoJSON data
        
        Args:
            geojson_dict: Raw GeoJSON dictionary
            
        Returns:
            Validated and parsed GeoJSON dictionary
            
        Raises:
            ValueError: If GeoJSON is invalid
        """
        try:
            # Validate basic GeoJSON structure
            if not isinstance(geojson_dict, dict):
                raise ValueError("GeoJSON must be a dictionary")
            
            if 'type' not in geojson_dict:
                raise ValueError("GeoJSON must have a 'type' field")
            
            if geojson_dict['type'] != 'FeatureCollection':
                raise ValueError("Only FeatureCollection type is supported")
            
            if 'features' not in geojson_dict:
                raise ValueError("FeatureCollection must have 'features' array")
            
            if not isinstance(geojson_dict['features'], list):
                raise ValueError("Features must be an array")
            
            # Validate each feature
            validated_features = []
            for i, feature in enumerate(geojson_dict['features']):
                try:
                    validated_feature = self._validate_feature(feature, i)
                    validated_features.append(validated_feature)
                except Exception as e:
                    logger.warning(f"Feature {i} validation failed: {e}")
                    continue
            
            # Return validated feature collection
            return {
                'type': 'FeatureCollection',
                'features': validated_features
            }
            
        except Exception as e:
            logger.error(f"GeoJSON parsing failed: {e}")
            raise ValueError(f"Invalid GeoJSON: {str(e)}")
    
    def _validate_feature(self, feature: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Validate individual GeoJSON feature
        
        Args:
            feature: Individual feature dictionary
            index: Feature index for error reporting
            
        Returns:
            Validated feature dictionary
        """
        if not isinstance(feature, dict):
            raise ValueError(f"Feature {index}: Feature must be a dictionary")
        
        if 'type' not in feature:
            raise ValueError(f"Feature {index}: Feature must have a 'type' field")
        
        if feature['type'] != 'Feature':
            raise ValueError(f"Feature {index}: Feature type must be 'Feature'")
        
        if 'geometry' not in feature:
            raise ValueError(f"Feature {index}: Feature must have a 'geometry' field")
        
        # Validate geometry
        geometry = feature['geometry']
        if not isinstance(geometry, dict):
            raise ValueError(f"Feature {index}: Geometry must be a dictionary")
        
        if 'type' not in geometry:
            raise ValueError(f"Feature {index}: Geometry must have a 'type' field")
        
        if 'coordinates' not in geometry:
            raise ValueError(f"Feature {index}: Geometry must have 'coordinates' field")
        
        # Validate geometry type
        geom_type = geometry['type']
        if geom_type not in self.supported_geometry_types:
            raise ValueError(f"Feature {index}: Unsupported geometry type: {geom_type}")
        
        # Validate coordinates using shapely
        try:
            shapely_geom = shape(geometry)
            if not shapely_geom.is_valid:
                validity_explanation = explain_validity(shapely_geom)
                raise ValueError(f"Feature {index}: Invalid geometry: {validity_explanation}")
        except Exception as e:
            raise ValueError(f"Feature {index}: Geometry validation failed: {str(e)}")
        
        # Validate properties (optional)
        if 'properties' in feature and not isinstance(feature['properties'], dict):
            raise ValueError(f"Feature {index}: Properties must be a dictionary")
        
        return feature
    
    def extract_feature_data(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant data from a validated feature
        
        Args:
            feature: Validated GeoJSON feature
            
        Returns:
            Dictionary with extracted data
        """
        geometry = feature['geometry']
        properties = feature.get('properties', {})
        
        # Extract name from properties (common field)
        name = properties.get('name', properties.get('NAME', properties.get('id', 'Unknown')))
        
        # Convert geometry to WKT format for database storage
        shapely_geom = shape(geometry)
        wkt_geometry = shapely_geom.wkt
        
        return {
            'name': name,
            'geometry_type': geometry['type'],
            'properties': properties,
            'wkt_geometry': wkt_geometry,
            'raw_geometry': geometry
        }
