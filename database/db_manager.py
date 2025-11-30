"""
Database manager module.

Handles database connections, query execution, and error handling.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from config.settings import settings


class DatabaseManager:
    """Manages database connections and query execution."""
    
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Execute a SQL query and return results as a pandas DataFrame.
        
        Args:
            query: SQL query string to execute
            
        Returns:
            Tuple of (DataFrame with results, error message if any)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, None
        except Exception as e:
            return pd.DataFrame(), str(e)
    
    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database.
        
        Returns:
            List of table names
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "column_id": row[0],
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default_value": row[4],
                "primary_key": bool(row[5])
            })
        conn.close()
        return columns
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """
        Get sample rows from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to fetch
            
        Returns:
            DataFrame with sample rows
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df, _ = self.execute_query(query)
        return df
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a SQL query without executing it.
        
        Args:
            query: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Use EXPLAIN to validate without executing
            cursor.execute(f"EXPLAIN {query}")
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_database_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the database.
        
        Returns:
            Dictionary with database statistics
        """
        tables = self.get_table_names()
        summary = {
            "table_count": len(tables),
            "tables": {}
        }
        
        for table in tables:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            conn.close()
            
            schema = self.get_table_schema(table)
            summary["tables"][table] = {
                "row_count": row_count,
                "column_count": len(schema),
                "columns": [col["name"] for col in schema]
            }
        
        return summary
