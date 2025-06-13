"""
Materialised-view layer: summarised IRR/PME results per fund_id
to serve as L-3 cache when Redis misses.
"""

import duckdb
import os
import json
import pathlib
import pandas as pd
import tempfile
from typing import Optional, Dict, Any, List
from logger import get_logger

logger = get_logger(__name__)

# **FIX: Use writable directory instead of read-only /data**
# Try multiple writable locations in order of preference
def get_writable_db_path():
    """Get a writable path for DuckDB database."""
    possible_paths = [
        os.getenv("DUCKDB_PATH"),  # Environment variable override
        "./pme_cache.duckdb",      # Current directory
        os.path.expanduser("~/pme_cache.duckdb"),  # Home directory
        os.path.join(tempfile.gettempdir(), "pme_cache.duckdb")  # Temp directory
    ]
    
    for path in possible_paths:
        if path is None:
            continue
        try:
            # Test if we can write to this location
            test_path = pathlib.Path(path)
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to create/open the database
            with duckdb.connect(str(test_path)) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
                conn.execute("DROP TABLE IF EXISTS test_table")
            
            logger.info(f"✅ Using writable DuckDB path: {path}")
            return test_path
        except Exception as e:
            logger.warning(f"⚠️  Cannot use DuckDB path {path}: {e}")
            continue
    
    # Fallback to in-memory database
    logger.warning("⚠️  No writable path found, using in-memory DuckDB")
    return ":memory:"

DB_PATH = get_writable_db_path()

# Global connection
_conn: Optional[duckdb.DuckDBPyConnection] = None

def get_connection() -> duckdb.DuckDBPyConnection:
    """Get or create DuckDB connection."""
    global _conn
    if not _conn:
        try:
            # Ensure directory exists
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            _conn = duckdb.connect(DB_PATH.as_posix())
            logger.info(f"✅ DuckDB connected: {DB_PATH}")
            
            # Initialize tables if they don't exist
            _initialize_tables()
            
        except Exception as e:
            logger.error(f"❌ DuckDB connection failed: {e}")
            raise
    return _conn

def _initialize_tables():
    """Initialize DuckDB tables and materialized views."""
    conn = get_connection()
    
    # Create fund_metric_cache table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fund_metric_cache (
            fund_id VARCHAR PRIMARY KEY,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            json VARCHAR  -- JSON metric payload
        )
    """)
    
    # Create materialized view
    refresh()

VIEW_SQL = """
CREATE OR REPLACE VIEW irr_pme_mv AS
SELECT fund_id,
       MAX(updated_at) AS as_of,
       ANY_VALUE(json) AS json  -- JSON metric payload
FROM   fund_metric_cache
GROUP  BY fund_id;
"""

def refresh():
    """Refresh the view (recreate it)."""
    try:
        conn = get_connection()
        conn.execute(VIEW_SQL)
        logger.debug("🔄 DuckDB view refreshed")
    except Exception as e:
        logger.error(f"❌ Failed to refresh view: {e}")
        raise

def get(fund_id: str) -> Optional[Dict[str, Any]]:
    """
    Get cached IRR/PME data for a fund from materialized view.
    
    Args:
        fund_id: Fund identifier
        
    Returns:
        Cached metric data or None if not found
    """
    try:
        conn = get_connection()
        cur = conn.execute(
            "SELECT json FROM irr_pme_mv WHERE fund_id = ?",
            [fund_id]
        )
        row = cur.fetchone()
        
        if row and row[0]:
            logger.debug(f"🎯 DuckDB L3 HIT for fund: {fund_id}")
            return json.loads(row[0])
        else:
            logger.debug(f"❌ DuckDB L3 MISS for fund: {fund_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ DuckDB get error for fund {fund_id}: {e}")
        return None

def set(fund_id: str, data: Dict[str, Any]) -> bool:
    """
    Store IRR/PME data for a fund in the cache table.
    
    Args:
        fund_id: Fund identifier
        data: Metric data to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_connection()
        json_data = json.dumps(data, default=str)
        
        # Upsert the data
        conn.execute("""
            INSERT OR REPLACE INTO fund_metric_cache (fund_id, updated_at, json)
            VALUES (?, CURRENT_TIMESTAMP, ?)
        """, [fund_id, json_data])
        
        logger.debug(f"💾 DuckDB L3 SET for fund: {fund_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ DuckDB set error for fund {fund_id}: {e}")
        return False

def clear(fund_id: Optional[str] = None) -> int:
    """
    Clear cached data for a specific fund or all funds.
    
    Args:
        fund_id: Fund to clear, or None to clear all
        
    Returns:
        Number of records cleared
    """
    try:
        conn = get_connection()
        
        if fund_id:
            result = conn.execute(
                "DELETE FROM fund_metric_cache WHERE fund_id = ?",
                [fund_id]
            )
            count = result.rowcount if hasattr(result, 'rowcount') else 1
            logger.info(f"🧹 DuckDB cleared fund: {fund_id}")
        else:
            result = conn.execute("DELETE FROM fund_metric_cache")
            count = result.rowcount if hasattr(result, 'rowcount') else 0
            logger.info("🧹 DuckDB cleared all funds")
            
        # Refresh materialized view after clearing
        refresh()
        return count
        
    except Exception as e:
        logger.error(f"❌ DuckDB clear error: {e}")
        return 0

def stats() -> Dict[str, Any]:
    """Get DuckDB cache statistics."""
    try:
        conn = get_connection()
        
        # Get table stats
        table_stats = conn.execute(
            "SELECT COUNT(*) as total_funds FROM fund_metric_cache"
        ).fetchone()
        
        mv_stats = conn.execute(
            "SELECT COUNT(*) as mv_funds FROM irr_pme_mv"
        ).fetchone()
        
        return {
            "connected": True,
            "db_path": str(DB_PATH),
            "total_funds_cached": table_stats[0] if table_stats else 0,
            "materialized_view_funds": mv_stats[0] if mv_stats else 0,
        }
        
    except Exception as e:
        logger.error(f"❌ DuckDB stats error: {e}")
        return {"connected": False, "error": str(e)}

def close():
    """Close DuckDB connection."""
    global _conn
    if _conn:
        try:
            _conn.close()
            _conn = None
            logger.info("🔌 DuckDB connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing DuckDB: {e}") 