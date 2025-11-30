"""
Schema loader module.

Extracts database schema information and formats it for RAG indexing.
"""

from typing import List, Dict, Any
from database.db_manager import DatabaseManager
from database.db_setup import DatabaseSetup


class SchemaLoader:
    """Loads and formats database schema information for RAG."""
    
    def __init__(self):
        """Initialize schema loader."""
        self.db_manager = DatabaseManager()
        self.db_setup = DatabaseSetup()
    
    def get_schema_documents(self) -> List[Dict[str, str]]:
        """
        Extract schema information as documents for vector store.
        
        Returns:
            List of document dictionaries with content and metadata
        """
        documents = []
        
        # Add overall schema description
        documents.append({
            "content": self.db_setup.get_schema_description(),
            "metadata": {
                "type": "schema_overview",
                "source": "database_documentation"
            }
        })
        
        # Add detailed information for each table
        tables = self.db_manager.get_table_names()
        
        for table in tables:
            # Table schema document
            schema = self.db_manager.get_table_schema(table)
            schema_text = self._format_table_schema(table, schema)
            
            documents.append({
                "content": schema_text,
                "metadata": {
                    "type": "table_schema",
                    "table_name": table,
                    "source": "database_schema"
                }
            })
            
            # Sample data document
            sample_df = self.db_manager.get_sample_data(table, limit=3)
            sample_text = self._format_sample_data(table, sample_df)
            
            documents.append({
                "content": sample_text,
                "metadata": {
                    "type": "sample_data",
                    "table_name": table,
                    "source": "database_samples"
                }
            })
        
        # Add common query patterns
        query_patterns = self._get_query_patterns()
        documents.append({
            "content": query_patterns,
            "metadata": {
                "type": "query_patterns",
                "source": "documentation"
            }
        })
        
        return documents
    
    def _format_table_schema(self, table_name: str, schema: List[Dict[str, Any]]) -> str:
        """
        Format table schema as readable text.
        
        Args:
            table_name: Name of the table
            schema: List of column information
            
        Returns:
            Formatted schema text
        """
        lines = [f"Table: {table_name}", "=" * 50, ""]
        
        for col in schema:
            pk_marker = " (PRIMARY KEY)" if col["primary_key"] else ""
            null_marker = " NOT NULL" if col["not_null"] else ""
            
            lines.append(
                f"- {col['name']}: {col['type']}{pk_marker}{null_marker}"
            )
        
        lines.append("")
        return "\n".join(lines)
    
    def _format_sample_data(self, table_name: str, sample_df) -> str:
        """
        Format sample data as readable text.
        
        Args:
            table_name: Name of the table
            sample_df: DataFrame with sample rows
            
        Returns:
            Formatted sample data text
        """
        lines = [
            f"Sample data from {table_name}:",
            "=" * 50,
            "",
            sample_df.to_string(index=False),
            ""
        ]
        return "\n".join(lines)
    
    def _get_query_patterns(self) -> str:
        """
        Get common SQL query patterns and examples.
        
        Returns:
            Query patterns documentation
        """
        return """
# Common SQL Query Patterns

## Aggregation Queries
- Total sales: SELECT SUM(total_amount) FROM orders
- Average order value: SELECT AVG(total_amount) FROM orders
- Count by category: SELECT category, COUNT(*) FROM products GROUP BY category

## Time-based Queries
- Monthly sales: SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) FROM orders GROUP BY month
- Sales by date: SELECT order_date, SUM(total_amount) FROM orders GROUP BY order_date

## Join Queries
- Customer orders: SELECT c.name, COUNT(o.id) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id
- Product sales: SELECT p.name, SUM(oi.quantity) FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id

## Filtering Queries
- By status: SELECT * FROM orders WHERE status = 'completed'
- By date range: SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
- By customer segment: SELECT * FROM customers WHERE segment = 'Enterprise'

## Top N Queries
- Top customers: SELECT customer_id, SUM(total_amount) as revenue FROM orders GROUP BY customer_id ORDER BY revenue DESC LIMIT 10
- Best selling products: SELECT product_id, SUM(quantity) as total_qty FROM order_items GROUP BY product_id ORDER BY total_qty DESC LIMIT 5

## Important Notes
- Use strftime() for date formatting in SQLite
- Always use meaningful aliases for readability
- Include appropriate GROUP BY when using aggregation functions
- Use JOIN to combine data from multiple tables
- Use ORDER BY with LIMIT for top N queries
"""
