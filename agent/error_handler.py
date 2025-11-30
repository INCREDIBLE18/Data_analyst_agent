"""
SQL error handler module.

Handles SQL query errors and attempts to repair them using LLM.
"""

from typing import Tuple, Optional
import pandas as pd
from langchain_groq import ChatGroq

from config.settings import settings
from database.db_manager import DatabaseManager


class SQLErrorHandler:
    """Handles SQL errors and attempts automatic repair."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize error handler.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.llm = ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,  # type: ignore
            temperature=0.0
        )
    
    def execute_with_retry(
        self,
        query: str,
        context: str = ""
    ) -> Tuple[pd.DataFrame, Optional[str], str]:
        """
        Execute SQL query with automatic error repair.
        
        Args:
            query: SQL query to execute
            context: Additional context about the query intent
            
        Returns:
            Tuple of (result DataFrame, error message, final query used)
        """
        attempts = 0
        current_query = query
        last_error = None
        
        while attempts < settings.MAX_REPAIR_ATTEMPTS:
            # Try to execute the query
            df, error = self.db_manager.execute_query(current_query)
            
            if error is None:
                # Success!
                return df, None, current_query
            
            # Query failed, try to repair
            attempts += 1
            last_error = error
            
            if attempts >= settings.MAX_REPAIR_ATTEMPTS:
                break
            
            print(f"⚠️  Query error (attempt {attempts}/{settings.MAX_REPAIR_ATTEMPTS}): {error}")
            print("🔧 Attempting to repair query...")
            
            # Get schema context for repair
            schema_context = self._get_schema_context()
            
            # Attempt repair using LLM
            current_query = self._repair_query(
                current_query,
                error,
                schema_context,
                context
            )
            
            if current_query is None:
                break
        
        # All attempts failed
        return pd.DataFrame(), last_error, query
    
    def _repair_query(
        self,
        query: str,
        error: str,
        schema_context: str,
        intent_context: str
    ) -> Optional[str]:
        """
        Attempt to repair a SQL query using LLM.
        
        Args:
            query: The failed SQL query
            error: The error message
            schema_context: Database schema information
            intent_context: User's original intent
            
        Returns:
            Repaired query or None if repair failed
        """
        prompt = f"""You are a SQL expert. A SQL query has failed with an error. Your task is to fix the query.

Database Schema:
{schema_context}

Failed Query:
{query}

Error Message:
{error}

User Intent:
{intent_context}

Please provide a corrected SQL query that will execute successfully. Consider:
1. Column names and table names must match the schema exactly
2. Use proper SQLite syntax (e.g., strftime for dates)
3. Ensure proper JOIN syntax if joining tables
4. Check for proper GROUP BY usage with aggregations
5. Verify WHERE clause conditions

Provide ONLY the corrected SQL query, nothing else. Do not include any explanations or markdown formatting.
"""
        
        try:
            response = self.llm.invoke(prompt)
            # Handle both string and AIMessage responses
            content = response.content if hasattr(response, 'content') else str(response)
            repaired_query = content.strip() if isinstance(content, str) else str(content).strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if repaired_query.startswith("```"):
                lines = repaired_query.split("\n")
                repaired_query = "\n".join(lines[1:-1])
            
            repaired_query = repaired_query.strip()
            
            print(f"🔧 Repaired query: {repaired_query}")
            return repaired_query
            
        except Exception as e:
            print(f"❌ Error during query repair: {e}")
            return None
    
    def _get_schema_context(self) -> str:
        """
        Get database schema context for error repair.
        
        Returns:
            Schema information string
        """
        tables = self.db_manager.get_table_names()
        context_parts = []
        
        for table in tables:
            schema = self.db_manager.get_table_schema(table)
            context_parts.append(f"\nTable: {table}")
            context_parts.append("Columns:")
            for col in schema:
                context_parts.append(f"  - {col['name']} ({col['type']})")
        
        return "\n".join(context_parts)
