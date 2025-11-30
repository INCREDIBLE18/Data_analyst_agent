"""
Streamlit Application - SQL Data Analyst Agent

Main application entry point.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from agent.sql_agent import SQLAgent
from ui.components import (
    render_header,
    render_sidebar,
    render_query_input,
    render_results,
    render_loading,
    render_error_state,
    init_session_state,
    render_database_setup
)
from ui.visualizer import DataVisualizer
from rag.vector_store import initialize_vector_store
from database.db_setup import DatabaseSetup
from database.connection_manager import DatabaseConnectionManager
from rag.dynamic_vector_store import DynamicVectorStore


class SQLAnalystApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_page()
        init_session_state()
        self.connection_manager = DatabaseConnectionManager()
        self.dynamic_vector_store = DynamicVectorStore()
        self.initialize_components()
    
    def setup_page(self):
        """Set up the Streamlit page configuration."""
        render_header()
    
    def initialize_components(self):
        """Initialize application components with caching."""
        try:
            # Validate settings
            settings.validate()
            
            # Initialize visualizer (always available)
            if 'visualizer' not in st.session_state:
                st.session_state.visualizer = DataVisualizer()
            
            # Agent will be initialized after database connection
            
        except ValueError as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.info("📝 Please create a `.env` file based on `.env.example` and add your OpenAI API key.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Initialization Error: {str(e)}")
            st.stop()
    
    def run(self):
        """Run the main application."""
        # Check if database is connected
        if 'db_connected' not in st.session_state or not st.session_state.db_connected:
            # Show database setup screen
            render_database_setup(self.connection_manager, self.dynamic_vector_store)
            return
        
        # Database is connected, initialize agent if not already done
        if 'agent' not in st.session_state and 'db_info' in st.session_state:
            with st.spinner("🚀 Initializing AI agent..."):
                session_id = st.session_state.db_info['session_id']
                
                # Check if connection exists, if not recreate it
                conn_info = self.connection_manager.get_connection(session_id)
                if conn_info is None:
                    # Recreate connection from stored info
                    db_info = st.session_state.db_info
                    
                    if db_info['connection_method'] == 'file_upload' and 'file_path' in db_info:
                        # Reconnect to file
                        from sqlalchemy import create_engine
                        file_path = db_info['file_path']
                        engine = create_engine(f'sqlite:///{file_path}')
                        self.connection_manager.connections[session_id] = {
                            'engine': engine,
                            'db_type': db_info['db_type']
                        }
                        conn_info = self.connection_manager.connections[session_id]
                    elif db_info['connection_method'] == 'connection_string':
                        st.error("❌ Connection lost. Please reconnect to your database.")
                        st.session_state.db_connected = False
                        if 'db_info' in st.session_state:
                            del st.session_state.db_info
                        st.rerun()
                        return
                    else:
                        st.error("❌ Connection lost. Please reconnect to your database.")
                        st.session_state.db_connected = False
                        if 'db_info' in st.session_state:
                            del st.session_state.db_info
                        st.rerun()
                        return
                
                engine = conn_info['engine']
                
                # Get or create vector store
                vectorstore = self.dynamic_vector_store.get_store(session_id)
                if vectorstore is None:
                    vectorstore = self.dynamic_vector_store.initialize_for_session(
                        session_id=session_id,
                        engine=engine
                    )
                
                # Create agent with dynamic connection
                st.session_state.agent = SQLAgent(engine=engine, vectorstore=vectorstore)
                st.session_state.session_id = session_id
        
        # Database is connected, show main interface
        # Show connection info in header
        if 'db_info' in st.session_state:
            info = st.session_state.db_info
            st.markdown(f"""
            <div style='background: #e8f4f8; padding: 0.8rem 1.2rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #667eea;'>
                <span style='color: #1e3a8a; font-weight: 500; font-size: 0.95rem;'>
                    🔗 Connected: <b style='color: #667eea;'>{info.get('file_name', info.get('db_type_selected', 'Database'))}</b> 
                    <span style='color: #64748b;'>({info['db_type']})</span> | 
                    <span style='color: #64748b;'>{len(info['schema_info'])} tables</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Render sidebar and capture any returned queries
        sidebar_query = render_sidebar()
        
        # If sidebar returned a query, populate the main input and process
        if sidebar_query:
            st.session_state.query_text_input = sidebar_query
            self.process_query(sidebar_query)
            return
        
        # Always show query input
        main_query = render_query_input()
        
        # Process main query if provided
        if main_query:
            self.process_query(main_query)
        
        # Show previous results if they exist
        if 'last_result' in st.session_state and st.session_state.last_result:
            st.markdown("---")
            st.markdown("### 📊 Previous Results")
            visualizer = st.session_state.visualizer
            render_results(st.session_state.last_result, st.session_state.get('last_insights', ''), visualizer, key_prefix="prev_")
    
    def process_query(self, query: str):
        """
        Process user query and display results with conversation memory.
        
        Args:
            query: User's natural language question
        """
        # Display the query being executed
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <h4 style='margin: 0;'>🔍 Executing Query:</h4>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>{query}</p>
        </div>
        """, unsafe_allow_html=True)
        
        agent = st.session_state.agent
        visualizer = st.session_state.visualizer
        
        # Store last query and results for PDF generation and persistence
        st.session_state.last_query = query
        st.session_state.last_result = None
        st.session_state.last_insights = None
        
        # Show loading state
        with st.spinner("🤔 Analyzing your question..."):
            # Execute query with conversation memory
            result = agent.query(query, st.session_state.conversation_memory)
        
        # Store conversation context
        if result["success"]:
            st.session_state.conversation_memory.append({
                'question': query,
                'sql': result.get('sql_query'),
                'timestamp': datetime.now().isoformat()
            })
            # Keep only last 5 conversations
            if len(st.session_state.conversation_memory) > 5:
                st.session_state.conversation_memory = st.session_state.conversation_memory[-5:]
            
            # Store results for reference
            st.session_state.previous_results.append({
                'query': query,
                'data': result.get('data'),
                'sql': result.get('sql_query')
            })
            if len(st.session_state.previous_results) > 3:
                st.session_state.previous_results = st.session_state.previous_results[-3:]
        
        # If successful, generate insights
        insights = ""
        if result["success"] and result["data"] is not None:
            with st.spinner("💡 Generating insights..."):
                insights = agent.generate_insights(
                    query,
                    result["data"],
                    result["sql_query"]
                )
        
        # Store results in session state
        st.session_state.last_result = result
        st.session_state.last_insights = insights
        
        # Render results
        render_results(result, insights, visualizer)


def main():
    """Main entry point."""
    app = SQLAnalystApp()
    app.run()


if __name__ == "__main__":
    main()
