from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry model"""
    type: str = Field(..., description="Geometry type (Point, LineString, Polygon, etc.)")
    coordinates: List[Any] = Field(..., description="Geometry coordinates")

class GeoJSONProperties(BaseModel):
    """GeoJSON feature properties"""
    name: Optional[str] = Field(None, description="Feature name")
    description: Optional[str] = Field(None, description="Feature description")
    id: Optional[str] = Field(None, description="Feature ID")
    
    class Config:
        extra = "allow"  # Allow additional properties

class GeoJSONFeature(BaseModel):
    """GeoJSON feature model"""
    type: str = Field("Feature", description="Feature type")
    geometry: GeoJSONGeometry = Field(..., description="Feature geometry")
    properties: Optional[GeoJSONProperties] = Field(None, description="Feature properties")
    id: Optional[str] = Field(None, description="Feature ID")

class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON feature collection model"""
    type: str = Field("FeatureCollection", description="Feature collection type")
    features: List[GeoJSONFeature] = Field(..., description="List of features")

class IngestResponse(BaseModel):
    """Response model for ingest endpoint"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    total_features: int = Field(..., description="Total number of features in the input")
    processed_features: int = Field(..., description="Number of features successfully processed")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    database_connected: bool = Field(..., description="Database connection status")
    feature_count: Optional[int] = Field(None, description="Total features in database")

class FeatureQueryResponse(BaseModel):
    """Response model for feature queries"""
    features: List[Dict[str, Any]] = Field(..., description="List of features")
    total_count: int = Field(..., description="Total number of features")
    geometry_type: Optional[str] = Field(None, description="Filtered geometry type")
    limit: int = Field(..., description="Query limit applied")
