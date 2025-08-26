from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from typing import Optional, Union, Dict, Any
import logging
import json

from .services.geojson_service import GeoJSONService
from .services.database_service import DatabaseService
from .models.geojson_models import GeoJSONFeatureCollection, IngestResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GeoJSON Ingestion Microservice",
    description="A microservice for ingesting and validating GeoJSON data",
    version="1.0.0"
)

# Initialize services
geojson_service = GeoJSONService()
db_service = DatabaseService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting GeoJSON Ingestion Microservice...")
        await db_service.connect()
        await db_service.create_tables_if_not_exist()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to establish database connection: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_service.disconnect()

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "geojson-ingestion"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_geojson(
    file: Optional[UploadFile] = File(None),
    request: Request = None
):
    """Ingest GeoJSON data from file upload or JSON body"""
    try:
        if file:
            # Handle file upload
            content = await file.read()
            geojson_content = content.decode('utf-8')
            geojson_dict = json.loads(geojson_content)
        elif request:
            # Handle JSON body
            body = await request.body()
            geojson_content = body.decode('utf-8')
            geojson_dict = json.loads(geojson_content)
        else:
            raise HTTPException(status_code=400, detail="Either file or request body must be provided")
        
        # Validate and parse GeoJSON
        feature_collection = geojson_service.parse_geojson(geojson_dict)
        
        # Check if parsing was successful
        if not feature_collection or 'features' not in feature_collection:
            raise HTTPException(status_code=400, detail="Invalid GeoJSON format")
        
        # Process features
        processed_features = 0
        errors = []
        
        for i, feature in enumerate(feature_collection['features'], 1):
            try:
                await db_service.insert_feature(feature)
                processed_features += 1
                logger.info(f"Successfully processed feature {i}")
            except Exception as e:
                error_msg = f"Failed to process feature {i}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        total_features = len(feature_collection['features'])
        
        return IngestResponse(
            success=True,
            message=f"Successfully processed {processed_features} features",
            total_features=total_features,
            processed_features=processed_features,
            errors=errors
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
