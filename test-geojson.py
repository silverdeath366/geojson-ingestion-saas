#!/usr/bin/env python3
"""
GeoJSON Validation Test Script
Tests GeoJSON files for validity and basic structure
"""

import json
import sys
import os
from pathlib import Path
from shapely.geometry import shape
from shapely.validation import explain_validity

def validate_geojson(file_path):
    """Validate a GeoJSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ File: {file_path}")
        
        # Check basic structure
        if not isinstance(data, dict):
            print("❌ Error: File must contain a JSON object")
            return False
        
        if 'type' not in data:
            print("❌ Error: Missing 'type' field")
            return False
        
        if data['type'] != 'FeatureCollection':
            print("❌ Error: Only FeatureCollection type is supported")
            return False
        
        if 'features' not in data:
            print("❌ Error: Missing 'features' array")
            return False
        
        if not isinstance(data['features'], list):
            print("❌ Error: 'features' must be an array")
            return False
        
        print(f"   📊 Type: {data['type']}")
        print(f"   🔢 Features: {len(data['features'])}")
        
        # Validate each feature
        valid_features = 0
        for i, feature in enumerate(data['features']):
            if validate_feature(feature, i):
                valid_features += 1
        
        print(f"   ✅ Valid features: {valid_features}/{len(data['features'])}")
        
        if valid_features == len(data['features']):
            print("   🎉 All features are valid!")
            return True
        else:
            print("   ⚠️  Some features have issues")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def validate_feature(feature, index):
    """Validate individual GeoJSON feature"""
    try:
        if not isinstance(feature, dict):
            print(f"     ❌ Feature {index}: Must be a dictionary")
            return False
        
        if 'type' not in feature:
            print(f"     ❌ Feature {index}: Missing 'type' field")
            return False
        
        if feature['type'] != 'Feature':
            print(f"     ❌ Feature {index}: Type must be 'Feature'")
            return False
        
        if 'geometry' not in feature:
            print(f"     ❌ Feature {index}: Missing 'geometry' field")
            return False
        
        geometry = feature['geometry']
        if not isinstance(geometry, dict):
            print(f"     ❌ Feature {index}: Geometry must be a dictionary")
            return False
        
        if 'type' not in geometry:
            print(f"     ❌ Feature {index}: Geometry missing 'type' field")
            return False
        
        if 'coordinates' not in geometry:
            print(f"     ❌ Feature {index}: Geometry missing 'coordinates' field")
            return False
        
        # Validate geometry using Shapely
        try:
            shapely_geom = shape(geometry)
            if not shapely_geom.is_valid:
                validity_explanation = explain_validity(shapely_geom)
                print(f"     ❌ Feature {index}: Invalid geometry - {validity_explanation}")
                return False
        except Exception as e:
            print(f"     ❌ Feature {index}: Geometry validation failed - {e}")
            return False
        
        # Check properties
        if 'properties' in feature and not isinstance(feature['properties'], dict):
            print(f"     ❌ Feature {index}: Properties must be a dictionary")
            return False
        
        # Extract name for display
        name = "Unknown"
        if 'properties' in feature and feature['properties']:
            name = feature['properties'].get('name', 
                   feature['properties'].get('NAME', 
                   feature['properties'].get('id', 'Unknown')))
        
        print(f"     ✅ Feature {index}: {name} ({geometry['type']})")
        return True
        
    except Exception as e:
        print(f"     ❌ Feature {index}: Validation error - {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test-geojson.py <geojson_file> [geojson_file2] ...")
        print("Or: python test-geojson.py --all (tests all .geojson files in parent directory)")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        # Test all GeoJSON files in parent directory
        parent_dir = Path(__file__).parent.parent
        geojson_files = list(parent_dir.glob('*.geojson'))
        
        if not geojson_files:
            print("No .geojson files found in parent directory")
            sys.exit(1)
        
        print(f"Found {len(geojson_files)} GeoJSON files to test:")
        print()
        
        all_valid = True
        for file_path in geojson_files:
            if not validate_geojson(file_path):
                all_valid = False
            print()
        
        if all_valid:
            print("🎉 All GeoJSON files are valid!")
            sys.exit(0)
        else:
            print("⚠️  Some GeoJSON files have issues")
            sys.exit(1)
    
    else:
        # Test specific files
        all_valid = True
        for file_path in sys.argv[1:]:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                all_valid = False
                continue
            
            if not validate_geojson(file_path):
                all_valid = False
            print()
        
        if all_valid:
            print("🎉 All specified GeoJSON files are valid!")
            sys.exit(0)
        else:
            print("⚠️  Some GeoJSON files have issues")
            sys.exit(1)

if __name__ == "__main__":
    main()
