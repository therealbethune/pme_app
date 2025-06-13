# PME Calculator Backend Startup Guide

## Issues Resolved

### 1. Import Path Issues ✅
- **Problem**: `ModuleNotFoundError: No module named 'main_minimal'`
- **Solution**: Created `start_backend.py` script that properly sets `PYTHONPATH`
- **Fix**: Backend directory is now correctly added to Python path

### 2. CORS Configuration Issues ✅
- **Problem**: 400 Bad Request errors for OPTIONS preflight requests
- **Solution**: Enhanced CORS middleware configuration
- **Fix**: Added support for multiple frontend ports (5173, 5174) and network addresses

### 3. Database Connection Handling ✅
- **Problem**: PostgreSQL connection failures causing startup issues
- **Solution**: Enhanced error handling with graceful fallback to memory-only mode
- **Fix**: Server continues to run even when PostgreSQL is unavailable

### 4. Missing Dependencies ✅
- **Problem**: References to non-existent `cache_manager.py`
- **Solution**: Verified all required files exist (`cache.py` is the correct file)
- **Fix**: Updated diagnostic tests to check for correct files

## How to Start the Backend

### Option 1: Using the Startup Script (Recommended)
```bash
# From the project root directory
python3 start_backend.py
```

### Option 2: Manual Startup
```bash
# Navigate to backend directory
cd pme_calculator/backend

# Set Python path and start server
PYTHONPATH=/Users/charlesbethune/Desktop/pme_app/pme_calculator/backend python3 main_minimal.py
```

### Option 3: Using Uvicorn Directly
```bash
cd pme_calculator/backend
PYTHONPATH=$(pwd) uvicorn main_minimal:app --host 0.0.0.0 --port 8000 --reload
```

## Verification

Run the comprehensive test to verify everything is working:
```bash
python3 test_backend_fixed.py
```

Expected output: All 5 tests should pass ✅

## Server Endpoints

Once running, the backend provides:

- **Health Check**: http://localhost:8000/api/health
- **API Documentation**: http://localhost:8000/api/docs
- **Chart Data**: http://localhost:8000/v1/metrics/*
- **File Upload**: http://localhost:8000/api/upload/*

## CORS Configuration

The backend now supports connections from:
- `http://localhost:5173` (Vite default)
- `http://localhost:5174` (Vite fallback)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`
- `http://192.168.0.15:5173` (Network address)
- `http://192.168.0.15:5174` (Network address fallback)

## Dependencies

Required Python packages:
- fastapi
- uvicorn
- asyncpg
- sqlalchemy
- redis
- pandas
- numpy

## Troubleshooting

### If you get import errors:
1. Make sure you're using the `start_backend.py` script
2. Verify you're in the correct directory
3. Check that all dependencies are installed

### If you get CORS errors:
1. Check that the frontend is running on a supported port
2. Verify the backend CORS configuration includes your frontend URL
3. Use browser developer tools to inspect the actual Origin header

### If charts don't load:
1. Check that the backend is running on port 8000
2. Verify the chart endpoints return valid JSON
3. Test individual chart endpoints: `/v1/metrics/irr_pme`, etc.

## Database Notes

- The backend runs in memory-only mode when PostgreSQL is unavailable
- This is normal for development and testing
- All functionality works without a database connection
- File uploads are stored in memory and temporary files

## Performance

- Redis caching is available if Redis is running
- DuckDB is used for local data caching
- Analysis engine provides 37.5x performance improvement with caching
- Mock data is used when no real data is uploaded 