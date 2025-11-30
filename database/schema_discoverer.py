"""
Automatic schema discovery and analysis.
"""
import sqlalchemy
from sqlalchemy import inspect, text
import pandas as pd
from typing import Dict, List, Any


class SchemaDiscoverer:
    """Discover and analyze database schemas dynamically."""
    
    def discover_full_schema(self, engine: sqlalchemy.Engine) -> Dict[str, Any]:
        """Discover complete database schema with metadata."""
        
        inspector = inspect(engine)
        schema = {}
        
        # Get all tables
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            # Get columns
            columns = inspector.get_columns(table_name)
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            
            # Get row count
            row_count = self._get_row_count(engine, table_name)
            
            # Sample data for better understanding
            sample_data = self._get_sample_data(engine, table_name)
            
            # Analyze columns
            column_stats = self._analyze_columns(engine, table_name, columns)
            
            schema[table_name] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'row_count': row_count,
                'sample_data': sample_data,
                'column_stats': column_stats,
                'column_names': [col['name'] for col in columns]
            }
        
        return schema
    
    def _get_row_count(self, engine: sqlalchemy.Engine, table_name: str) -> int:
        """Get total row count for table."""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                return int(count) if count is not None else 0
        except:
            return 0
    
    def _get_sample_data(self, engine: sqlalchemy.Engine, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample rows from table."""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = pd.read_sql(query, engine)
            return df.to_dict('records')
        except:
            return []
    
    def _analyze_columns(self, engine: sqlalchemy.Engine, table_name: str, columns: List[Any]) -> Dict:  # type: ignore
        """Analyze column statistics."""
        stats = {}
        
        for column in columns:
            col_name = column['name']
            col_type = str(column['type']).upper()
            
            try:
                # Check if numeric
                if any(t in col_type for t in ['INT', 'FLOAT', 'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE']):
                    # Numeric column stats
                    query = f"""
                    SELECT 
                        COUNT(*) as count,
                        COUNT(DISTINCT {col_name}) as unique_count,
                        MIN({col_name}) as min_value,
                        MAX({col_name}) as max_value,
                        AVG({col_name}) as avg_value
                    FROM {table_name}
                    WHERE {col_name} IS NOT NULL
                    """
                else:
                    # Text/Date column stats
                    query = f"""
                    SELECT 
                        COUNT(*) as count,
                        COUNT(DISTINCT {col_name}) as unique_count,
                        COUNT(*) - COUNT({col_name}) as null_count
                    FROM {table_name}
                    """
                
                result = pd.read_sql(query, engine).iloc[0].to_dict()
                stats[col_name] = result
                
            except Exception as e:
                stats[col_name] = {'error': f'Analysis failed: {str(e)[:50]}'}
        
        return stats
    
    def generate_schema_description(self, schema: Dict) -> str:
        """Generate natural language description of schema."""
        descriptions = []
        
        for table_name, table_info in schema.items():
            columns = [f"{col['name']} ({col['type']})" for col in table_info['columns']]
            row_count = table_info.get('row_count', 0)
            
            # Foreign key relationships
            fk_desc = ""
            if table_info.get('foreign_keys'):
                fk_list = []
                for fk in table_info['foreign_keys']:
                    fk_list.append(f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                if fk_list:
                    fk_desc = f"\n  Relationships: {', '.join(fk_list)}"
            
            desc = f"""
Table: {table_name}
  Columns: {', '.join(columns)}
  Rows: {row_count:,}{fk_desc}
"""
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def generate_schema_documents(self, schema: Dict) -> List[str]:
        """Generate documents for vector store."""
        documents = []
        
        for table_name, table_info in schema.items():
            # Main table description
            columns_desc = ", ".join([f"{col['name']} ({col['type']})" for col in table_info['columns']])
            doc = f"Table {table_name} contains: {columns_desc}. Total rows: {table_info.get('row_count', 0):,}"
            documents.append(doc)
            
            # Foreign key relationships
            if table_info.get('foreign_keys'):
                for fk in table_info['foreign_keys']:
                    fk_doc = f"Table {table_name} has foreign key {fk['constrained_columns']} referencing {fk['referred_table']}.{fk['referred_columns']}"
                    documents.append(fk_doc)
            
            # Sample data context
            if table_info.get('sample_data'):
                for idx, sample in enumerate(table_info['sample_data'][:2]):
                    sample_doc = f"Sample data from {table_name}: {sample}"
                    documents.append(sample_doc)
            
            # Column statistics
            for col_name, stats in table_info.get('column_stats', {}).items():
                if isinstance(stats, dict) and 'error' not in stats:
                    if 'min_value' in stats:
                        stats_doc = f"Column {table_name}.{col_name}: min={stats.get('min_value')}, max={stats.get('max_value')}, avg={stats.get('avg_value', 0):.2f}"
                    else:
                        stats_doc = f"Column {table_name}.{col_name}: {stats.get('unique_count', 0)} unique values out of {stats.get('count', 0)}"
                    documents.append(stats_doc)
        
        return documents
