"""
SQL Agent module.

LangChain-based agent for natural language to SQL conversion.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import time
from langchain_groq import ChatGroq

from config.settings import settings
from agent.tools import SQLAgentTools
from agent.error_handler import SQLErrorHandler
from agent.query_cache import QueryCache
from agent.sql_validator import SQLValidator
from database.db_manager import DatabaseManager
from rag.vector_store import VectorStore
from rag.query_expander import QueryExpander
from utils.performance_tracker import PerformanceTracker


class SQLAgent:
    """Natural language to SQL agent using LangChain."""
    
    def __init__(self, engine=None, vectorstore=None):
        """Initialize the SQL agent with optional dynamic connection.
        
        Args:
            engine: SQLAlchemy engine for dynamic database connection
            vectorstore: ChromaDB vectorstore for dynamic schema
        """
        settings.validate()
        
        # Initialize components
        if engine is None:
            # Use default database manager
            self.db_manager = DatabaseManager()
            self.vector_store = VectorStore()
        else:
            # Use dynamic connection
            self.engine = engine
            self.vectorstore = vectorstore
            self.db_manager = None  # Will use engine directly
            self.vector_store = None  # Will use vectorstore directly
        
        self.error_handler = SQLErrorHandler(self.db_manager) if self.db_manager else None
        self.agent_tools = SQLAgentTools()
        
        # Initialize enhanced components
        self.cache = QueryCache(ttl_minutes=30)
        self.validator = SQLValidator()
        self.query_expander = QueryExpander()
        self.perf_tracker = PerformanceTracker()
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=settings.LLM_MODEL,  # type: ignore
            api_key=settings.GROQ_API_KEY,  # type: ignore
            temperature=settings.LLM_TEMPERATURE  # type: ignore
        )

    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for the agent.
        
        Returns:
            System prompt string
        """
        return """You are an expert SQL analyst assistant. Your job is to help users query a sales analytics database using natural language.

Your workflow:
1. When a user asks a question, first use the 'search_schema' tool to understand the database structure
2. If needed, use 'list_tables' or 'get_table_info' to get more details
3. Construct a valid SQL query based on the schema
4. Execute the query using the 'execute_sql' tool
5. If the query fails, analyze the error and try again with a corrected query

Important guidelines:
- Always search the schema first to understand what tables and columns are available
- Use proper SQLite syntax (e.g., strftime for date operations)
- When joining tables, ensure foreign key relationships are correct
- Use meaningful column aliases for readability
- For date grouping, use strftime('%Y-%m', column_name)
- Always include appropriate WHERE, GROUP BY, and ORDER BY clauses as needed
- If a query returns no results, explain why that might be

Be concise and focus on generating accurate SQL queries."""
    
    def query(self, user_question: str, conversation_memory: list = None, use_cache: bool = True) -> Dict[str, Any]:  # type: ignore
        """
        Enhanced query processing with caching, validation, and tracking.
        
        Args:
            user_question: User's question in natural language
            conversation_memory: Previous conversation context
            use_cache: Whether to use query caching
            
        Returns:
            Dictionary with results, SQL query, and metadata
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if use_cache:
                cached_result = self.cache.get(user_question)
                if cached_result:
                    print(f"⚡ Cache hit! Returning cached result")
                    cached_result['from_cache'] = True
                    cached_result['cache_hit'] = True
                    cached_result['execution_time'] = time.time() - start_time
                    return cached_result
            
            # Expand query for better RAG retrieval
            print(f"🔍 Expanding query for better context...")
            expanded_queries = self.query_expander.expand_query(user_question)
            
            # Get relevant schema context with expanded queries
            schema_context = ""
            for exp_query in expanded_queries[:2]:  # Use top 2 expansions
                if self.vector_store:
                    context = self.vector_store.get_relevant_context(exp_query)
                elif self.vectorstore:
                    # Use dynamic vectorstore
                    docs = self.vectorstore.similarity_search(exp_query, k=5)
                    context = "\n".join([doc.page_content for doc in docs])
                else:
                    context = ""
                schema_context += context + "\n"
            
            # Generate SQL using agent
            print(f"🤔 Processing query: {user_question}")
            
            sql_query = self._generate_sql_query(user_question, schema_context, conversation_memory)
            
            if not sql_query:
                result = {
                    "success": False,
                    "error": "Failed to generate SQL query",
                    "sql_query": None,
                    "data": None,
                    "execution_time": time.time() - start_time,
                    "from_cache": False
                }
                self.perf_tracker.track_query(user_question, "", time.time() - start_time, 0, False)
                return result
            
            print(f"📝 Generated SQL: {sql_query}")
            
            # Validate SQL before execution
            validation = self.validator.validate(sql_query)
            
            if not validation['valid']:
                error_msg = f"SQL Validation Failed: {'; '.join(validation['errors'])}"
                print(f"❌ {error_msg}")
                result = {
                    "success": False,
                    "error": error_msg,
                    "sql_query": sql_query,
                    "data": None,
                    "validation_errors": validation['errors'],
                    "execution_time": time.time() - start_time,
                    "from_cache": False
                }
                self.perf_tracker.track_query(user_question, sql_query, time.time() - start_time, 0, False)
                return result
            
            # Show warnings if any
            if validation['warnings']:
                print(f"⚠️ SQL Warnings: {'; '.join(validation['warnings'])}")
            
            # Execute with retry logic
            if self.error_handler:
                df, error, final_query = self.error_handler.execute_with_retry(
                    sql_query,
                    context=user_question
                )
            else:
                # Use dynamic engine directly
                try:
                    df = pd.read_sql(sql_query, self.engine)
                    error = None
                    final_query = sql_query
                except Exception as e:
                    df = None
                    error = str(e)
                    final_query = sql_query
            
            execution_time = time.time() - start_time
            
            if error:
                result = {
                    "success": False,
                    "error": error,
                    "sql_query": final_query,
                    "data": None,
                    "execution_time": execution_time,
                    "from_cache": False
                }
                self.perf_tracker.track_query(user_question, final_query, execution_time, 0, False)
                return result
            
            print(f"✅ Query executed successfully. Found {len(df)} rows.")
            
            result = {
                "success": True,
                "sql_query": final_query,
                "data": df,
                "row_count": len(df),
                "execution_time": execution_time,
                "from_cache": False,
                "validation_warnings": validation.get('warnings', [])
            }
            
            # Track performance
            self.perf_tracker.track_query(user_question, final_query, execution_time, len(df), True)
            
            # Cache successful results
            if use_cache:
                self.cache.set(user_question, result)
            
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sql_query": None,
                "data": None
            }
    
    def _generate_sql_query(self, question: str, schema_context: str, conversation_memory: list = None) -> str:  # type: ignore
        """
        Generate SQL query from natural language question with conversation context.
        
        Args:
            question: User's natural language question
            schema_context: Relevant database schema context
            conversation_memory: Previous conversation context
            
        Returns:
            Generated SQL query
        """
        # Build conversation context if available
        context_str = ""
        if conversation_memory and len(conversation_memory) > 0:
            context_str = "\n\nPrevious Conversation Context:\n"
            for i, conv in enumerate(conversation_memory[-3:]):  # Last 3 exchanges
                context_str += f"Q{i+1}: {conv.get('question', '')}\n"
                if conv.get('sql'):
                    context_str += f"SQL{i+1}: {conv.get('sql')}\n"
        
        prompt = f"""Given the following database schema and a user question, generate a SQL query.

Database Schema:
{schema_context}
{context_str}

User Question: {question}

Generate a valid SQLite SQL query that answers the question. Important:
- Use proper SQLite syntax
- For date operations, use strftime() function
- Use appropriate JOINs when accessing multiple tables
- Include proper GROUP BY for aggregations
- Add ORDER BY and LIMIT when appropriate
- Use meaningful aliases
- If this is a follow-up question (like "show more", "break it down"), reference the previous SQL context

Provide ONLY the SQL query, no explanations or markdown formatting.
"""
        
        try:
            response = self.llm.invoke(prompt)
            # Handle both string and AIMessage responses
            content = response.content if hasattr(response, 'content') else str(response)
            sql_query = content.strip() if isinstance(content, str) else str(content).strip()
            
            # Clean up markdown if present
            if sql_query.startswith("```"):
                lines = sql_query.split("\n")
                sql_query = "\n".join(lines[1:-1]) if len(lines) > 2 else sql_query
            
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            return sql_query
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            return ""
    
    def generate_insights(self, question: str, data: pd.DataFrame, sql_query: str) -> str:
        """
        Generate natural language insights from query results.
        
        Args:
            question: Original user question
            data: Query result DataFrame
            sql_query: SQL query that was executed
            
        Returns:
            Natural language insights
        """
        import pandas as pd
        
        # Handle different data types
        if isinstance(data, tuple):
            # Convert tuple to DataFrame
            if len(data) > 1 and data[1] is not None and len(data[1]) > 0:
                df = pd.DataFrame(data[1], columns=[desc[0] for desc in data[0]])
            else:
                return "No results found for this query."
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return "No results found for this query."
            
        if df.empty:
            return "No results found for this query."
        
        # Prepare data summary
        data_summary = f"Found {len(df)} rows.\n"
        data_summary += f"Columns: {', '.join(df.columns)}\n"
        data_summary += f"\nFirst few rows:\n{df.head(10).to_string(index=False)}"
        
        prompt = f"""Analyze the following SQL query results and provide insights.

Original Question: {question}

SQL Query: {sql_query}

Results:
{data_summary}

Provide a clear, concise summary of the insights. Include:
1. Direct answer to the user's question
2. Key findings and trends
3. Notable patterns or anomalies
4. Any actionable insights

Keep it brief and focused (3-5 sentences).
"""
        
        try:
            response = self.llm.invoke(prompt)
            # Handle both string and AIMessage responses
            content = response.content if hasattr(response, 'content') else str(response)
            return content.strip() if isinstance(content, str) else str(content).strip()
        except Exception as e:
            return f"Unable to generate insights: {str(e)}"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.perf_tracker.get_statistics()
    
    def get_performance_recommendations(self) -> list:
        """Get performance recommendations."""
        return self.perf_tracker.get_recommendations()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Clear query cache."""
        self.cache.clear()
        print("✅ Cache cleared")
    
    def clear_performance_history(self):
        """Clear performance tracking history."""
        self.perf_tracker.clear()
        print("✅ Performance history cleared")
