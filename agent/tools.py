"""
Agent tools module.

Defines tools for the SQL agent to use.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from langchain_core.tools import Tool

from database.db_manager import DatabaseManager
from rag.vector_store import VectorStore
from agent.error_handler import SQLErrorHandler


class SQLAgentTools:
    """Collection of tools for the SQL agent."""
    
    def __init__(self):
        """Initialize agent tools."""
        self.db_manager = DatabaseManager()
        self.vector_store = VectorStore()
        self.error_handler = SQLErrorHandler(self.db_manager)
    
    def search_schema_tool(self, query: str) -> str:
        """
        Search database schema using semantic search.
        
        Args:
            query: Natural language description of what to search for
            
        Returns:
            Relevant schema context
        """
        context = self.vector_store.get_relevant_context(query)
        return context
    
    def execute_sql_tool(self, sql_query: str) -> str:
        """
        Execute SQL query and return results or error.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Query results as string or error message
        """
        df, error = self.db_manager.execute_query(sql_query)
        
        if error:
            return f"Error executing query: {error}"
        
        if df.empty:
            return "Query executed successfully but returned no results."
        
        # Format results as string
        result = f"Query executed successfully. Found {len(df)} rows.\n\n"
        result += df.to_string(index=False)
        
        return result
    
    def get_table_info_tool(self, table_name: str) -> str:
        """
        Get detailed information about a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table schema and sample data
        """
        try:
            schema = self.db_manager.get_table_schema(table_name)
            sample_df = self.db_manager.get_sample_data(table_name, limit=3)
            
            result = f"Table: {table_name}\n"
            result += "=" * 50 + "\n\n"
            result += "Columns:\n"
            for col in schema:
                result += f"  - {col['name']} ({col['type']})\n"
            result += f"\nSample data:\n{sample_df.to_string(index=False)}\n"
            
            return result
        except Exception as e:
            return f"Error getting table info: {str(e)}"
    
    def list_tables_tool(self, _: str = "") -> str:
        """
        List all tables in the database.
        
        Args:
            _: Unused parameter (for tool interface compatibility)
            
        Returns:
            List of table names with row counts
        """
        summary = self.db_manager.get_database_summary()
        
        result = "Available tables:\n\n"
        for table_name, info in summary["tables"].items():
            result += f"- {table_name} ({info['row_count']} rows)\n"
            result += f"  Columns: {', '.join(info['columns'])}\n\n"
        
        return result
    
    def get_langchain_tools(self) -> list:
        """
        Get tools formatted for LangChain agent.
        
        Returns:
            List of LangChain Tool objects
        """
        tools = [
            Tool(
                name="search_schema",
                func=self.search_schema_tool,
                description=(
                    "Search database schema and documentation using natural language. "
                    "Use this to understand what tables and columns are available, "
                    "and how they relate to each other. "
                    "Input: natural language description of what you're looking for."
                )
            ),
            Tool(
                name="execute_sql",
                func=self.execute_sql_tool,
                description=(
                    "Execute a SQL query on the database. "
                    "Use this after you've constructed a valid SQL query. "
                    "Input: valid SQL query string."
                )
            ),
            Tool(
                name="get_table_info",
                func=self.get_table_info_tool,
                description=(
                    "Get detailed information about a specific table including "
                    "its schema and sample data. "
                    "Input: table name."
                )
            ),
            Tool(
                name="list_tables",
                func=self.list_tables_tool,
                description=(
                    "List all available tables in the database with their columns. "
                    "Use this to see what tables exist. "
                    "Input: empty string or any text (ignored)."
                )
            )
        ]
        
        return tools
