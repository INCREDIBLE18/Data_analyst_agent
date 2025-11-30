"""
Multi-database connection manager.
"""
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any
import sqlalchemy
from sqlalchemy import create_engine, inspect
from urllib.parse import urlparse
import os
import shutil
from pathlib import Path


class DatabaseConnectionManager:
    """Manage connections to multiple databases."""
    
    SUPPORTED_TYPES = {
        'sqlite': 'SQLite',
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL', 
        'mssql': 'SQL Server',
        'oracle': 'Oracle'
    }
    
    def __init__(self):
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, Dict] = {}
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_db_type(self, connection_string: str) -> str:
        """Auto-detect database type from connection string."""
        if connection_string.endswith(('.db', '.sqlite', '.sqlite3')):
            return 'sqlite'
        
        parsed = urlparse(connection_string)
        db_type = parsed.scheme.split('+')[0] if parsed.scheme else 'unknown'
        return db_type
    
    def connect_database(self, 
                        session_id: str,
                        connection_string: Optional[str] = None,
                        uploaded_file = None) -> Dict[str, Any]:
        """Connect to a database (upload or connection string)."""
        
        try:
            if uploaded_file:
                # Handle file upload
                return self._handle_file_upload(session_id, uploaded_file)
            elif connection_string:
                # Handle connection string
                return self._handle_connection_string(session_id, connection_string)
            else:
                return {
                    'success': False,
                    'error': 'No database source provided'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Connection failed: {str(e)}"
            }
    
    def _handle_file_upload(self, session_id: str, uploaded_file) -> Dict[str, Any]:
        """Handle uploaded database files."""
        
        # Create session directory
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = session_dir / uploaded_file.name
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Detect file type and connect
        actual_db_path = file_path  # Track the actual database file path
        
        if uploaded_file.name.endswith(('.db', '.sqlite', '.sqlite3')):
            engine = create_engine(f'sqlite:///{file_path}')
            db_type = 'sqlite'
            actual_db_path = file_path
            
        elif uploaded_file.name.endswith('.csv'):
            # Convert CSV to SQLite
            df = pd.read_csv(file_path)
            sqlite_path = file_path.with_suffix('.db')
            engine = create_engine(f'sqlite:///{sqlite_path}')
            
            # Infer table name from filename - sanitize for SQL
            import re
            table_name = file_path.stem.lower()
            table_name = re.sub(r'[^a-z0-9_]', '_', table_name)  # Replace invalid chars with underscore
            table_name = re.sub(r'_+', '_', table_name)  # Remove consecutive underscores
            table_name = table_name.strip('_')  # Remove leading/trailing underscores
            if not table_name or table_name[0].isdigit():  # Ensure valid start
                table_name = 'table_' + table_name
            
            df.to_sql(table_name, engine, index=False, if_exists='replace')
            db_type = 'sqlite'
            actual_db_path = sqlite_path  # Use the converted DB path
            
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            # Convert Excel to SQLite
            excel_file = pd.ExcelFile(file_path)
            sqlite_path = file_path.with_suffix('.db')
            engine = create_engine(f'sqlite:///{sqlite_path}')
            
            # Each sheet becomes a table
            import re
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Sanitize sheet name for SQL
                table_name = str(sheet_name).lower()
                table_name = re.sub(r'[^a-z0-9_]', '_', table_name)  # Replace invalid chars
                table_name = re.sub(r'_+', '_', table_name)  # Remove consecutive underscores
                table_name = table_name.strip('_')  # Remove leading/trailing underscores
                if not table_name or table_name[0].isdigit():  # Ensure valid start
                    table_name = 'sheet_' + table_name
                
                df.to_sql(table_name, engine, index=False, if_exists='replace')
            db_type = 'sqlite'
            actual_db_path = sqlite_path  # Use the converted DB path
            
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.name}")
        
        # Store connection
        self.connections[session_id] = {'engine': engine, 'db_type': db_type}
        
        # Discover schema
        schema = self._discover_schema(engine)
        self.schemas[session_id] = schema
        
        return {
            'success': True,
            'db_type': db_type,
            'schema_info': schema,
            'tables': list(schema.keys()),
            'total_tables': len(schema),
            'file_name': uploaded_file.name,
            'file_path': str(actual_db_path)  # Use actual database path
        }
    
    def _handle_connection_string(self, session_id: str, connection_string: str) -> Dict[str, Any]:
        """Handle database connection via connection string."""
        
        # Create engine
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        
        db_type = self.detect_db_type(connection_string)
        
        # Store connection
        self.connections[session_id] = {'engine': engine, 'db_type': db_type}
        
        # Discover schema
        schema = self._discover_schema(engine)
        self.schemas[session_id] = schema
        
        return {
            'success': True,
            'db_type': db_type,
            'schema_info': schema,
            'tables': list(schema.keys()),
            'total_tables': len(schema),
            'connection_type': 'remote'
        }
    
    def _discover_schema(self, engine: sqlalchemy.Engine) -> Dict:
        """Discover basic schema information."""
        inspector = inspect(engine)
        schema = {}
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get row count
            try:
                with engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = result.scalar() or 0
            except:
                row_count = 0
            
            schema[table_name] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'column_names': [col['name'] for col in columns],
                'row_count': row_count
            }
        
        return schema
    
    def get_connection(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get database connection for session."""
        return self.connections.get(session_id)
    
    def get_schema(self, session_id: str) -> Optional[Dict]:
        """Get schema for session."""
        return self.schemas.get(session_id)
    
    def execute_query(self, session_id: str, query: str) -> pd.DataFrame:
        """Execute query on session database."""
        conn_info = self.get_connection(session_id)
        if not conn_info:
            raise ValueError(f"No connection found for session {session_id}")
        
        return pd.read_sql(query, conn_info['engine'])
    
    def disconnect(self, session_id: str):
        """Disconnect and cleanup session."""
        if session_id in self.connections:
            self.connections[session_id]['engine'].dispose()
            del self.connections[session_id]
        
        if session_id in self.schemas:
            del self.schemas[session_id]
        
        # Cleanup uploaded files
        session_dir = self.upload_dir / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
    
    def list_active_sessions(self) -> List[str]:
        """List all active database sessions."""
        return list(self.connections.keys())
