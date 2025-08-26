# GeoJSON Ingestion Microservice

A FastAPI-based microservice for ingesting, validating, and storing GeoJSON data in a PostgreSQL/PostGIS database.

## Features

- **GeoJSON Validation**: Comprehensive validation using Shapely and GeoJSON libraries
- **Spatial Database Storage**: Stores geometries in PostGIS with proper spatial indexing
- **FastAPI Framework**: Modern, async Python web framework with automatic API documentation
- **Docker Support**: Containerized application with all spatial dependencies
- **Health Checks**: Kubernetes-ready health check endpoints
- **Error Handling**: Robust error handling and logging

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  GeoJSON Service │───▶│  Database      │
│   (main.py)     │    │  (Validation)    │    │  Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────┐                            ┌─────────────────┐
│   Pydantic      │                            │   PostgreSQL    │
│   Models        │                            │   + PostGIS     │
└─────────────────┘                            └─────────────────┘
```

## API Endpoints

### GET /healthz
Health check endpoint for Kubernetes liveness/readiness probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "geojson-ingestion",
  "timestamp": "2024-01-01T00:00:00",
  "database_connected": true,
  "feature_count": 42
}
```

### POST /ingest
Ingest GeoJSON data from file upload or JSON body.

**Request:** Multipart form with GeoJSON file or JSON body

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 5 features",
  "total_features": 5,
  "processed_features": 5,
  "errors": [],
  "timestamp": "2024-01-01T00:00:00"
}
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL with PostGIS extension

## Quick Start

### 1. Clone and Navigate
```bash
cd applications/geojson-ingestion
```

### 2. Environment Setup
```bash
cp env.example .env
# Edit .env with your database credentials
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`

### 4. Test the API
```bash
# Health check
curl http://localhost:8000/healthz

# Ingest GeoJSON file
curl -X POST http://localhost:8000/ingest \
  -F "file=@test.geojson"
```

## Local Development

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=geospatial
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Build

### Build Image
```bash
docker build -t geojson-app .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DB_HOST=your-db-host \
  -e DB_NAME=your-db-name \
  -e DB_USER=your-db-user \
  -e DB_PASSWORD=your-db-password \
  geojson-app
```

## Database Schema

The service creates the following table structure:

```sql
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
```

**Indexes:**
- Spatial index on `geom` using GIST
- Index on `geometry_type` for filtering
- Index on `name` for text searches
- GIN index on `properties` for JSON queries

## Testing

### Sample GeoJSON Files
The project includes several test files:
- `test.geojson` - Basic test data
- `test2.geojson` - Additional test data
- `test-fixed.geojson` - Fixed version of test data
- `test-pipeline.geojson` - Pipeline test data

### Run Tests
```bash
# Test health endpoint
curl http://localhost:8000/healthz

# Test ingestion with sample file
curl -X POST http://localhost:8000/ingest \
  -F "file=@test.geojson"

# Check database
docker-compose exec db psql -U postgres -d geospatial -c "SELECT COUNT(*) FROM geo_features;"
```

## Deployment

### AWS ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Tag image
docker tag geojson-app:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/geojson-app:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/geojson-app:latest
```

### Kubernetes
The service is designed to work with Kubernetes:
- Health check endpoint for liveness/readiness probes
- Environment variable configuration
- Non-root user for security
- Resource limits and requests configurable

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `geospatial` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `` |
| `DB_SSLMODE` | SSL mode | `prefer` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Troubleshooting

### Common Issues

1. **GDAL Installation Errors**
   - Ensure Docker image has proper GDAL dependencies
   - Check GDAL environment variables

2. **Database Connection Issues**
   - Verify database credentials
   - Check network connectivity
   - Ensure PostGIS extension is enabled

3. **GeoJSON Validation Errors**
   - Check GeoJSON format compliance
   - Verify geometry validity
   - Review coordinate system (should be WGS84/4326)

### Logs
```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Terraform infrastructure setup for geospatial data processing.
