"""
Reusable UI components for Streamlit app.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from datetime import datetime
import json


def init_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'conversation_memory' not in st.session_state:
        st.session_state.conversation_memory = []
    if 'previous_results' not in st.session_state:
        st.session_state.previous_results = []
    if 'previous_sql' not in st.session_state:
        st.session_state.previous_sql = None


def render_header():
    """Render application header with enhanced styling."""
    st.set_page_config(
        page_title="SQL Data Analyst Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling and web compatibility
    st.markdown("""
    <style>
    /* Responsive header */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Card styling */
    .query-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .main-header p {
            font-size: 0.9rem;
        }
        .main-header {
            padding: 1.5rem;
        }
    }
    
    /* Sidebar improvements */
    [data-testid="stSidebar"] {
        min-width: 280px;
    }
    
    /* Make expanders more visible */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Tab improvements for mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        font-size: 0.9rem;
    }
    
    /* Metrics spacing */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    
    /* Code block improvements */
    .stCodeBlock {
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Text area improvements */
    textarea {
        font-size: 1rem !important;
    }
    
    /* Mobile specific adjustments */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 100%;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem;
            padding: 6px 8px;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI SQL Data Analyst</h1>
        <p>Transform natural language into powerful SQL queries • Powered by Groq AI</p>
    </div>
    """, unsafe_allow_html=True)


def generate_dynamic_examples(schema_info):
    """Generate example questions based on actual database schema.
    
    Args:
        schema_info: Dict containing table and column information
        
    Returns:
        Dict of categorized example questions
    """
    if not schema_info:
        # Default examples if no schema available
        return {
            "🚀 Quick Start": [
                "Show me all data",
                "List all tables",
                "Count total rows",
                "Show first 10 records"
            ],
            "📊 Analytics": [
                "Show summary statistics",
                "Group data by category",
                "Calculate totals",
                "Show trends over time"
            ],
            "🔍 Advanced": [
                "Find duplicates",
                "Show unique values",
                "Calculate percentages",
                "Compare groups"
            ]
        }
    
    # Get table names and columns
    tables = list(schema_info.keys())
    first_table = tables[0] if tables else "data"
    
    # Get columns for the first table
    columns = []
    numeric_cols = []
    text_cols = []
    date_cols = []
    id_cols = []
    percentage_cols = []
    score_cols = []
    
    if first_table in schema_info:
        for col_info in schema_info[first_table].get('columns', []):
            col_name = col_info.get('name', '')
            col_type = str(col_info.get('type', '')).upper()
            col_lower = col_name.lower()
            columns.append(col_name)
            
            # Identify ID columns (exclude from metrics)
            if 'id' in col_lower or col_name.upper().endswith('_ID'):
                id_cols.append(col_name)
                text_cols.append(col_name)  # Treat IDs as categorical
            # Identify percentage columns
            elif '%' in col_name or 'percent' in col_lower or 'rate' in col_lower:
                percentage_cols.append(col_name)
                numeric_cols.append(col_name)
            # Identify score/test columns
            elif any(word in col_lower for word in ['score', 'marks', 'test', 'grade', 'result']):
                score_cols.append(col_name)
                numeric_cols.append(col_name)
            # Regular numeric columns
            elif any(t in col_type for t in ['INT', 'FLOAT', 'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE']):
                numeric_cols.append(col_name)
            # Date columns
            elif any(t in col_type for t in ['DATE', 'TIME']):
                date_cols.append(col_name)
            # Text columns
            else:
                text_cols.append(col_name)
    
    # Filter numeric columns to exclude IDs
    numeric_cols_no_id = [col for col in numeric_cols if col not in id_cols]
    
    # Generate dynamic examples
    quick_start = [
        f"Show me the first 10 rows",
        f"How many records are in {first_table}?",
    ]
    
    # Add meaningful quick start based on available columns
    if id_cols and numeric_cols_no_id:
        quick_start.append(f"Show {id_cols[0]} and {numeric_cols_no_id[0]}")
    elif len(columns) > 1:
        quick_start.append(f"List {columns[0]} and {columns[1]}")
    
    if percentage_cols:
        quick_start.append(f"What is the average {percentage_cols[0]}?")
    elif score_cols:
        quick_start.append(f"What is the average {score_cols[0]}?")
    elif numeric_cols_no_id:
        quick_start.append(f"What is the total {numeric_cols_no_id[0]}?")
    else:
        quick_start.append(f"Show all unique values")
    
    # Analytics examples
    analytics = []
    
    # Use non-ID columns for grouping
    non_id_text = [col for col in text_cols if col not in id_cols]
    
    if id_cols and numeric_cols_no_id:
        analytics.append(f"Top 5 {id_cols[0]} by {numeric_cols_no_id[0]}")
        analytics.append(f"Show {id_cols[0]} with highest {numeric_cols_no_id[0]}")
    
    if score_cols and len(score_cols) > 1:
        analytics.append(f"Compare {score_cols[0]} and {score_cols[1]}")
    elif numeric_cols_no_id and len(numeric_cols_no_id) > 1:
        analytics.append(f"Correlation between {numeric_cols_no_id[0]} and {numeric_cols_no_id[1]}")
    
    if percentage_cols:
        analytics.append(f"What is the average {percentage_cols[0]}?")
    elif numeric_cols_no_id:
        analytics.append(f"Show statistics for {numeric_cols_no_id[0]}")
    
    if date_cols and numeric_cols_no_id:
        analytics.append(f"Show {numeric_cols_no_id[0]} trends by {date_cols[0]}")
    elif non_id_text and numeric_cols_no_id:
        analytics.append(f"Group {numeric_cols_no_id[0]} by {non_id_text[0]}")
    
    # Pad analytics if needed
    while len(analytics) < 4:
        if numeric_cols_no_id:
            analytics.append(f"Summary statistics for all metrics")
        else:
            analytics.append(f"Analyze {first_table} data")
    
    # Advanced examples
    advanced = []
    
    if id_cols and numeric_cols_no_id:
        advanced.append(f"Which {id_cols[0]} has the highest {numeric_cols_no_id[0]}?")
        if len(numeric_cols_no_id) > 1:
            advanced.append(f"Find {id_cols[0]} where {numeric_cols_no_id[0]} > average")
    
    if numeric_cols_no_id and len(numeric_cols_no_id) > 1:
        advanced.append(f"Show correlation: {numeric_cols_no_id[0]} vs {numeric_cols_no_id[1]}")
    
    if percentage_cols and score_cols:
        advanced.append(f"How does {percentage_cols[0]} affect {score_cols[0]}?")
    elif len(numeric_cols_no_id) >= 2:
        advanced.append(f"Relationship between {numeric_cols_no_id[0]} and {numeric_cols_no_id[1]}")
    
    if id_cols and numeric_cols_no_id:
        advanced.append(f"Ranking of {id_cols[0]} by performance")
    elif non_id_text:
        advanced.append(f"Distribution analysis by {non_id_text[0]}")
    
    # Pad advanced if needed
    while len(advanced) < 4:
        if numeric_cols_no_id and len(numeric_cols_no_id) >= 2:
            advanced.append(f"Multi-factor analysis of key metrics")
        elif non_id_text:
            advanced.append(f"Show patterns in {non_id_text[0]}")
        else:
            advanced.append(f"Advanced insights from {first_table}")
    
    return {
        "🚀 Quick Start": quick_start[:4],
        "📊 Analytics": analytics[:4],
        "🔍 Advanced": advanced[:4]
    }


def render_sidebar():
    """Render enhanced sidebar with features and examples."""
    with st.sidebar:
        # About section with icon
        st.markdown("### 🎯 About This Tool")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 8px; color: white; margin-bottom: 1rem;
                    font-size: 0.95rem; line-height: 1.5;'>
            <strong style='font-size: 1.1rem;'>AI-Powered SQL Assistant</strong><br/>
            Ask questions in plain English and get instant insights from your sales database.
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("##### ✨ Key Features")
        features = {
            "🧠": "Smart SQL Generation",
            "🔧": "Auto Error Correction",
            "📊": "Beautiful Visualizations",
            "💡": "AI-Powered Insights",
            "📈": "Real-time Analytics"
        }
        for icon, feature in features.items():
            st.markdown(f"{icon} **{feature}**")
        
        st.divider()
        
        # Performance statistics
        if 'agent' in st.session_state:
            with st.expander("📊 Performance Stats"):
                try:
                    stats = st.session_state.agent.get_performance_stats()
                    cache_stats = st.session_state.agent.get_cache_stats()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Queries", stats.get('total_queries', 0))
                        st.metric("Cache Hits", cache_stats.get('total_hits', 0))
                    with col2:
                        st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
                        st.metric("Avg Time", f"{stats.get('avg_execution_time', 0):.2f}s")
                    
                    # Recommendations
                    recommendations = st.session_state.agent.get_performance_recommendations()
                    if recommendations:
                        st.markdown("**💡 Recommendations:**")
                        for rec in recommendations:
                            st.markdown(f"- {rec}")
                    
                    # Clear buttons
                    col_clear1, col_clear2 = st.columns(2)
                    with col_clear1:
                        if st.button("🗑️ Clear Cache", key="clear_cache_btn"):
                            st.session_state.agent.clear_cache()
                            st.success("Cache cleared!")
                    with col_clear2:
                        if st.button("📊 Reset Stats", key="reset_stats_btn"):
                            st.session_state.agent.clear_performance_history()
                            st.success("Stats reset!")
                except Exception as e:
                    st.warning(f"Stats unavailable: {str(e)}")
        
        st.divider()
        
        # Dynamic examples based on actual schema
        st.markdown("### 💡 Try These Examples")
        
        # Get schema info if available
        schema_info = None
        if 'db_info' in st.session_state:
            schema_info = st.session_state.db_info.get('schema_info', {})
        
        # Generate dynamic examples
        examples = generate_dynamic_examples(schema_info)
        
        # Category tabs
        example_category = st.selectbox(
            "Choose category:",
            list(examples.keys()),
            label_visibility="collapsed"
        )
        
        for idx, example in enumerate(examples[example_category]):
            # Create a small copyable text input with click to use
            col1, col2 = st.columns([4, 1])
            with col1:
                st.code(example, language="text")
            with col2:
                if st.button("📋 Use", key=f"use_ex_{idx}_{example_category}", help="Use this query"):
                    return example
        
        st.divider()
        
        # Query history
        if st.session_state.query_history:
            st.markdown("### 📜 Recent Queries")
            for i, hist in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"🕐 {hist['time'][:5]} - {hist['query'][:30]}..."):
                    st.markdown(f"**Query:** {hist['query']}")
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        if st.button(f"🔄 Rerun", key=f"hist_{i}"):
                            return hist['query']
                    with col_h2:
                        st.code(hist['query'], language="text")
        
        st.divider()
        
        # Database schema with toggle - Show actual schema
        with st.expander("📊 Database Schema", expanded=False):
            if 'db_info' in st.session_state and 'schema_info' in st.session_state.db_info:
                schema_info = st.session_state.db_info['schema_info']
                st.markdown("**📋 Tables in Your Database:**")
                st.markdown("")
                
                for table_name, table_info in schema_info.items():
                    row_count = table_info.get('row_count', 0)
                    st.markdown(f"**📄 {table_name}** ({row_count:,} rows)")
                    
                    # Show columns
                    columns = table_info.get('column_names', [])
                    if columns:
                        st.markdown(f"*Columns:* {', '.join(columns)}")
                    
                    st.markdown("")
            else:
                st.markdown("""
                **📋 Default Schema:**
                
                **👥 customers**
                - id, name, email, country, segment
                
                **📦 products**
                - id, name, category, price
                
                **🛒 orders**
                - id, customer_id, order_date, status, total_amount
            
            **📝 order_items**
            - id, order_id, product_id, quantity, unit_price
            
            *All tables are connected via foreign keys*
            """)
        
        # Footer with stats
        st.divider()
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.85rem;'>
            <p>⚡ Powered by <strong>Groq AI</strong></p>
            <p>🚀 llama-3.3-70b Model</p>
        </div>
        """, unsafe_allow_html=True)


def render_query_input() -> Optional[str]:
    """
    Render enhanced query input area with suggestions.
    
    Returns:
        User query string or None
    """
    # Initialize session state for query input
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""
    
    # Check if we need to clear (from previous interaction)
    if 'clear_requested' in st.session_state and st.session_state.clear_requested:
        if 'query_text_input' in st.session_state:
            del st.session_state.query_text_input
        if 'last_result' in st.session_state:
            del st.session_state.last_result
        if 'last_insights' in st.session_state:
            del st.session_state.last_insights
        if 'query_history' in st.session_state:
            st.session_state.query_history = []
        st.session_state.clear_requested = False
    
    # Query input section with styling
    st.markdown("### 💬 Ask Your Question")
    
    # Text area takes full width
    query = st.text_area(
        "Type your question here:",
        placeholder="e.g., Show me the top 10 customers by total revenue with their order counts...",
        height=100,
        key="query_text_input",
        label_visibility="collapsed",
        value=st.session_state.get('query_text_input', '')
    )
    
    # Buttons below the text area
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        submit = st.button("🚀 Analyze", type="primary")
    with col_btn2:
        clear = st.button("🗑️ Clear")
    
    if clear:
        # Set flag to clear on next run
        st.session_state.clear_requested = True
        st.rerun()
        return None
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    quick_cols = st.columns(4)
    quick_actions = [
        ("📊 Show Stats", "Show database statistics and table row counts"),
        ("🏆 Top Sales", "What are the top 5 products by total revenue?"),
        ("📈 Trends", "Show monthly sales trends for 2024"),
        ("👥 Customers", "List top 10 customers by spending")
    ]
    
    for idx, (label, query_text) in enumerate(quick_actions):
        with quick_cols[idx]:
            if st.button(label, key=f"quick_{idx}"):
                # Add to history and return the query directly
                st.session_state.query_history.append({
                    'query': query_text,
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'timestamp': datetime.now().isoformat()
                })
                return query_text
    
    # Add to history and return query
    if submit and query:
        # Add to history
        st.session_state.query_history.append({
            'query': query,
            'time': datetime.now().strftime('%H:%M:%S'),
            'timestamp': datetime.now().isoformat()
        })
        return query
    
    return None


def render_results(result: dict, insights: str, visualizer, key_prefix: str = ""):
    """
    Render enhanced query results with data, visualization, and insights.
    
    Args:
        result: Query result dictionary
        insights: Generated insights text
        visualizer: DataVisualizer instance
        key_prefix: Prefix for unique widget keys (e.g., 'prev_' for previous results)
    """
    if not result["success"]:
        st.markdown("""
        <div style='background: #fee; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #f44;'>
            <h3 style='color: #f44; margin: 0;'>❌ Query Failed</h3>
            <p style='margin: 0.5rem 0 0 0;'>{}</p>
        </div>
        """.format(result['error']), unsafe_allow_html=True)
        
        if result["sql_query"]:
            with st.expander("🔍 View SQL Query"):
                st.code(result["sql_query"], language="sql")
                st.markdown("**💡 Tip:** Try rephrasing your question or check the example queries in the sidebar.")
        return
    
    # Success notification with cache indicator
    cache_badge = "⚡ <strong>CACHED</strong>" if result.get('from_cache', False) else ""
    execution_time = result.get("execution_time", 0)
    warnings = result.get("validation_warnings", [])
    warnings_html = ""
    if warnings:
        warnings_html = "<br><small>⚠️ " + " | ".join(warnings) + "</small>"
    
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;
                animation: slideIn 0.5s ease-out;'>
        <h4 style='margin: 0;'>✅ Query Executed Successfully! {cache_badge}</h4>
        <p style='margin: 0.3rem 0 0 0;'>Found {result['row_count']} rows in {execution_time:.3f} seconds</p>
        {warnings_html}
    </div>
    <style>
        @keyframes slideIn {{
            from {{ transform: translateY(-20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs for organized results
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Visualization", "💡 AI Insights", "📋 Data Table", "🔧 SQL Query", "🎓 SQL Explainer", "⚡ Optimizer"])
    
    df = result["data"]
    
    with tab1:
        if not df.empty:
            # Show metrics first if applicable
            metrics = visualizer.create_metric_cards(df)
            if metrics and len(metrics) <= 4:
                st.markdown("#### 📈 Key Metrics")
                metric_cols = st.columns(len(metrics))
                for idx, (col_name, values) in enumerate(metrics.items()):
                    with metric_cols[idx]:
                        # Show average with min/max as delta context
                        avg_val = values['mean']
                        delta_info = f"Range: {values['min']:.1f} - {values['max']:.1f}"
                        st.metric(
                            label=col_name.replace('_', ' ').title(),
                            value=f"{avg_val:,.2f}" if avg_val < 1000 else f"{avg_val:,.0f}",
                            delta=delta_info
                        )
                st.divider()
            
            # Show chart
            fig = visualizer.create_visualization(df)
            if fig:
                st.plotly_chart(fig, key=f"{key_prefix}main_chart")
            else:
                st.info("📊 Data is best viewed in table format")
        else:
            st.warning("No data to visualize")
    
    with tab2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 10px; color: white;'>
            <h4 style='margin: 0 0 1rem 0;'>🤖 AI Analysis</h4>
            <p style='font-size: 1.1rem; line-height: 1.6; margin: 0;'>{insights}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        if not df.empty:
            st.markdown(f"**Showing {len(df)} rows × {len(df.columns)} columns**")
            
            # Download buttons row
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                # CSV download
                csv = df.to_csv(index=False).encode('utf-8')
                result_id = hash(str(result.get("sql_query", "")))
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"{key_prefix}download_csv_{result_id}"
                )
            
            with col2:
                # PDF download
                try:
                    from utils.pdf_generator import PDFReportGenerator
                    
                    # Only generate PDF when button is clicked to avoid rerun issues
                    if 'pdf_data' not in st.session_state:
                        st.session_state.pdf_data = None
                    
                    # Generate PDF on first render or when results change
                    result_hash = hash(str(result.get("sql_query", "")))
                    if st.session_state.pdf_data is None or st.session_state.get('last_result_hash') != result_hash:
                        try:
                            pdf_gen = PDFReportGenerator()
                            
                            # Get chart as base64 if available
                            chart_b64 = None
                            fig = visualizer.create_visualization(df)
                            if fig:
                                chart_b64 = pdf_gen.get_chart_as_base64(fig)
                            
                            # Generate PDF
                            pdf_bytes = pdf_gen.generate_report(
                                query=st.session_state.get('last_query', 'N/A'),
                                sql=result["sql_query"],
                                data=df,
                                insights=insights,
                                chart_base64=chart_b64
                            )
                            
                            st.session_state.pdf_data = pdf_bytes
                            st.session_state.last_result_hash = result_hash
                        except Exception as pdf_err:
                            st.error(f"PDF generation failed: {str(pdf_err)}")
                            st.session_state.pdf_data = None
                    
                    # Show download button
                    if st.session_state.pdf_data:
                        # Check if it's PDF or HTML based on content
                        is_pdf = st.session_state.pdf_data[:4] == b'%PDF'
                        file_ext = "pdf" if is_pdf else "html"
                        mime_type = "application/pdf" if is_pdf else "text/html"
                        label = "📄 Download PDF" if is_pdf else "📄 Download HTML Report"
                        
                        result_id = hash(str(result.get("sql_query", "")))
                        st.download_button(
                            label=label,
                            data=st.session_state.pdf_data,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                            mime=mime_type,
                            key=f"{key_prefix}download_pdf_{result_id}"
                        )
                    else:
                        st.caption("⚠️ Report unavailable")
                        
                except ImportError:
                    st.caption("📦 Install reportlab for PDF export")
                except Exception as e:
                    st.caption(f"⚠️ Report error: {str(e)[:30]}...")
            
            with col3:
                st.caption("💡 Export your results for further analysis")
            
            # Display dataframe with custom styling
            st.dataframe(
                df,
                height=400,
                hide_index=True
            )
        else:
            st.info("No data returned")
    
    with tab4:
        st.markdown("**Generated SQL Query (Select to Copy):**")
        
        # Copyable text area with copy button
        col_sql1, col_sql2 = st.columns([5, 1])
        with col_sql1:
            st.text_area(
                "SQL Query",
                value=result["sql_query"],
                height=200,
                label_visibility="collapsed",
                key=f"{key_prefix}sql_copy_area",
                help="Select all text (Ctrl+A) and copy (Ctrl+C)"
            )
        with col_sql2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            # Copy button using st.components
            import html
            sql_escaped = result["sql_query"].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            copy_button_html = f"""
                <button id="copy-sql-btn" 
                    style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    color: white; border: none; padding: 0.6rem 1.2rem; 
                    border-radius: 5px; cursor: pointer; font-weight: 500;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    📋 Copy SQL
                </button>
                <script>
                    document.getElementById('copy-sql-btn').addEventListener('click', function() {{
                        const sqlText = `{sql_escaped}`;
                        navigator.clipboard.writeText(sqlText).then(function() {{
                            alert('✅ SQL copied to clipboard!');
                        }}).catch(function(err) {{
                            console.error('Failed to copy: ', err);
                        }});
                    }});
                </script>
            """
            st.components.v1.html(copy_button_html, height=50)
        
        # SQL explanation
        with st.expander("ℹ️ Understanding the SQL"):
            st.markdown("""
            **What this query does:**
            - Retrieves data from the database
            - Uses appropriate JOINs for related tables
            - Includes WHERE clauses for filtering
            - Groups and sorts results as needed
            
            **💡 Tip:** You can modify this SQL and run it directly in your database client!
            """)
    
    with tab5:
        # Import explainer and optimizer
        from agent.sql_explainer import SQLExplainer
        from agent.query_optimizer import QueryOptimizer
        
        explainer = SQLExplainer()
        optimizer = QueryOptimizer()
        
        # Explain the query
        explanation = explainer.explain_query(result["sql_query"])
        
        # Overview
        st.markdown("### 📖 Query Overview")
        st.info(explanation["overview"])
        
        # Complexity
        complexity = explanation["complexity"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Complexity Level", complexity["level"])  # type: ignore
        with col2:
            st.metric("Complexity Score", f"{complexity['score']}/10")  # type: ignore
        
        if complexity["factors"]:  # type: ignore
            st.markdown("**Complexity Factors:**")
            for factor in complexity["factors"]:  # type: ignore
                st.markdown(f"- {factor}")
        
        st.divider()
        
        # Tables
        if explanation["tables"]:
            st.markdown("### 📊 Tables Used")
            for table in explanation["tables"]:
                with st.expander(f"{table['type']}: **{table['name']}**"):  # type: ignore
                    st.markdown(f"**Purpose:** {table['purpose']}")  # type: ignore
        
        # Joins
        if explanation["joins"]:
            st.markdown("### 🔗 Table Joins")
            for join in explanation["joins"]:
                with st.expander(f"{join['type']} on **{join['table']}**"):  # type: ignore
                    st.markdown(f"**Condition:** `{join['condition']}`")  # type: ignore
                    st.markdown(f"**What it does:** {join['explanation']}")  # type: ignore
        
        # Filters
        if explanation["filters"]:
            st.markdown("### 🔍 Filters (WHERE Clause)")
            for filt in explanation["filters"]:
                st.markdown(f"- `{filt['condition']}` - {filt['purpose']}")  # type: ignore
        
        # Aggregations
        if explanation["aggregations"]:
            st.markdown("### 📈 Aggregations")
            for agg in explanation["aggregations"]:
                st.markdown(f"- **{agg['function']}({agg['column']})** - {agg['purpose']}")  # type: ignore
        
        # Ordering
        if explanation["ordering"]:
            st.markdown("### 📋 Ordering & Limiting")
            if "order_by" in explanation["ordering"]:
                order = explanation["ordering"]["order_by"]  # type: ignore
                st.markdown(f"- **Order by:** {order['column']} ({order['direction']}")  # type: ignore
                st.markdown(f"  - {order['purpose']}")  # type: ignore
            if "limit" in explanation["ordering"]:
                limit = explanation["ordering"]["limit"]  # type: ignore
                st.markdown(f"- **Limit:** {limit['value']} rows")  # type: ignore
                st.markdown(f"  - {limit['purpose']}")  # type: ignore
        
        # Tips
        st.divider()
        st.markdown("### 💡 Tips & Best Practices")
        for tip in explanation["tips"]:
            st.markdown(tip)
    
    with tab6:
        # Optimize the query
        optimizer = QueryOptimizer()
        analysis = optimizer.analyze(result["sql_query"])
        
        # Performance score
        score = analysis["performance_score"]
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Color-code the score
            if score >= 8:
                score_color = "🟢"
            elif score >= 6:
                score_color = "🟡"
            else:
                score_color = "🔴"
            
            st.metric("Performance Score", f"{score_color} {score}/10")
        
        with col2:
            # Count issues
            issue_count = len(analysis["issues"])
            st.metric("Issues Found", issue_count)
        
        with col3:
            # Best practices check
            practices = analysis["best_practices"]
            passed = sum(1 for v in practices.values() if v)
            total = len(practices)
            st.metric("Best Practices", f"{passed}/{total} Passed")
        
        st.divider()
        
        # Issues
        if analysis["issues"]:
            st.markdown("### ⚠️ Performance Issues")
            for issue in analysis["issues"]:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[issue["severity"]]
                with st.expander(f"{severity_icon} {issue['severity'].upper()}: {issue['issue']}"):
                    st.markdown(f"**Impact:** {issue['impact']}")
                    st.success(f"**Solution:** {issue['solution']}")
        else:
            st.success("✅ No performance issues detected!")
        
        # Suggestions
        st.markdown("### 💡 Optimization Suggestions")
        for suggestion in analysis["suggestions"]:
            st.markdown(suggestion)
        
        st.divider()
        
        # Index recommendations
        if analysis["index_recommendations"]:
            st.markdown("### 📇 Index Recommendations")
            st.info("Creating indexes can significantly improve query performance:")
            for idx in analysis["index_recommendations"]:
                st.code(f"CREATE INDEX idx_{idx['column']} ON {idx['table']}({idx['column']});", language="sql")
                st.caption(f"Reason: {idx['reason']}")
        
        # Execution plan
        st.divider()
        st.markdown("### 🔄 Estimated Execution Plan")
        for step in analysis["execution_plan"]:
            st.markdown(step)


def render_loading():
    """Render loading state."""
    with st.spinner("🤔 Analyzing your question and generating SQL..."):
        st.write("This may take a few moments...")


def render_error_state(error_message: str):
    """
    Render error state.
    
    Args:
        error_message: Error message to display
    """
    st.error(f"❌ An error occurred: {error_message}")
    st.info("💡 Try rephrasing your question or check the example questions in the sidebar.")


def render_database_setup(connection_manager, dynamic_vector_store):
    """
    Render database setup screen for connecting to a database.
    
    Args:
        connection_manager: DatabaseConnectionManager instance
        dynamic_vector_store: DynamicVectorStore instance
    
    Returns:
        Connection info dict if successful, None otherwise
    """
    # Check if we have a pending connection ready to activate
    if 'pending_connection' in st.session_state:
        st.markdown("""
        <div class='main-header'>
            <h1>🤖 SQL Data Analyst Agent</h1>
            <p>Database Connected! Ready to analyze your data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pending = st.session_state.pending_connection
        
        st.success("✅ Successfully connected to database!")
        
        # Show schema info
        st.markdown("### 📋 Database Schema")
        schema_info = pending['schema_info']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tables", len(schema_info))
        with col2:
            total_columns = sum(len(info['column_names']) for info in schema_info.values())
            st.metric("Total Columns", total_columns)
        with col3:
            total_rows = sum(info.get('row_count', 0) for info in schema_info.values())
            st.metric("Total Rows", f"{total_rows:,}")
        
        with st.expander("📊 View Tables"):
            for table_name, info in schema_info.items():
                st.markdown(f"**{table_name}** ({info.get('row_count', 0):,} rows)")
                st.caption(f"Columns: {', '.join(info['column_names'])}")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"🔗 Connected to: **{pending.get('file_name', pending.get('db_type_selected', 'Database'))}** ({pending['db_type']})")
        with col2:
            if st.button("✅ Start Analyzing", type="primary", key="start_analyzing_main", use_container_width=True):
                st.session_state.db_connected = True
                st.session_state.db_info = st.session_state.pending_connection
                del st.session_state.pending_connection  # Clear pending
                st.rerun()
        
        return
    
    st.markdown("## 📊 Database Setup")
    st.markdown("Connect your database to start analyzing with natural language queries.")
    st.markdown("Choose how you'd like to connect to your database:")
    
    # Connection method tabs
    tab1, tab2 = st.tabs(["📁 Upload Database File", "🔗 Connection String"])
    
    with tab1:
        st.markdown("### Upload SQLite Database or CSV File")
        st.info("💡 Supported formats: .db, .sqlite, .sqlite3, .csv")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['db', 'sqlite', 'sqlite3', 'csv'],
            help="Upload your database file or CSV data"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
            
            with col2:
                if st.button("🚀 Connect", key="upload_connect", type="primary"):
                    with st.spinner("🔄 Connecting to database..."):
                        try:
                            import uuid
                            
                            session_id = str(uuid.uuid4())
                            
                            # Connect via connection manager (pass the uploaded file directly)
                            result = connection_manager.connect_database(
                                session_id=session_id,
                                uploaded_file=uploaded_file
                            )
                            
                            if result['success']:
                                # Initialize vector store
                                with st.spinner("🔍 Analyzing database schema..."):
                                    vectorstore = dynamic_vector_store.initialize_for_session(
                                        session_id=session_id,
                                        engine=connection_manager.get_connection(session_id)['engine']
                                    )
                                
                                # Show schema info
                                st.markdown("### 📋 Database Schema")
                                schema_info = result['schema_info']
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Tables", len(schema_info))
                                with col2:
                                    total_columns = sum(len(info['column_names']) for info in schema_info.values())
                                    st.metric("Total Columns", total_columns)
                                with col3:
                                    total_rows = sum(info.get('row_count', 0) for info in schema_info.values())
                                    st.metric("Total Rows", f"{total_rows:,}")
                                
                                with st.expander("📊 View Tables"):
                                    for table_name, info in schema_info.items():
                                        st.markdown(f"**{table_name}** ({info.get('row_count', 0):,} rows)")
                                        st.caption(f"Columns: {', '.join(info['column_names'])}")
                                
                                # Store connection info in session state and trigger rerun
                                pending_conn = {
                                    'session_id': session_id,
                                    'db_type': result['db_type'],
                                    'schema_info': schema_info,
                                    'connection_method': 'file_upload',
                                    'file_name': uploaded_file.name,
                                    'file_path': result.get('file_path', '')
                                }
                                st.session_state.pending_connection = pending_conn
                                print(f"[DEBUG] Stored pending_connection: {list(pending_conn.keys())}")
                                print("[DEBUG] Triggering rerun to show Start Analyzing button")
                                st.rerun()
                            else:
                                st.error(f"❌ Connection failed: {result['message']}")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("### Enter Database Connection String")
        st.info("💡 Supported databases: MySQL, PostgreSQL, SQL Server, Oracle, SQLite")
        
        # Database type selector
        db_type = st.selectbox(
            "Database Type",
            ["MySQL", "PostgreSQL", "SQL Server", "Oracle", "SQLite"],
            help="Select your database type"
        )
        
        # Connection string examples
        examples = {
            "MySQL": "mysql+pymysql://user:password@localhost:3306/database",
            "PostgreSQL": "postgresql://user:password@localhost:5432/database",
            "SQL Server": "mssql+pyodbc://user:password@localhost/database?driver=ODBC+Driver+17+for+SQL+Server",
            "Oracle": "oracle+cx_oracle://user:password@localhost:1521/database",
            "SQLite": "sqlite:///path/to/database.db"
        }
        
        st.caption(f"Example: `{examples[db_type]}`")
        
        conn_string = st.text_input(
            "Connection String",
            type="password",
            help="Enter your database connection string"
        )
        
        if conn_string:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success("✅ Connection string entered")
            
            with col2:
                if st.button("🚀 Connect", key="string_connect", type="primary"):
                    with st.spinner("🔄 Connecting to database..."):
                        try:
                            import uuid
                            session_id = str(uuid.uuid4())
                            
                            # Connect via connection manager
                            result = connection_manager.connect_database(
                                session_id=session_id,
                                connection_string=conn_string
                            )
                            print(f"[DEBUG] Connection result: {result.get('success', False)}")
                            print(f"[DEBUG] Result keys: {list(result.keys())}")
                            
                            if result['success']:
                                # Initialize vector store
                                with st.spinner("🔍 Analyzing database schema..."):
                                    vectorstore = dynamic_vector_store.initialize_for_session(
                                        session_id=session_id,
                                        engine=connection_manager.get_connection(session_id)['engine']
                                    )
                                
                                # Show schema info
                                st.markdown("### 📋 Database Schema")
                                schema_info = result['schema_info']
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Tables", len(schema_info))
                                with col2:
                                    total_columns = sum(len(info['column_names']) for info in schema_info.values())
                                    st.metric("Total Columns", total_columns)
                                with col3:
                                    total_rows = sum(info.get('row_count', 0) for info in schema_info.values())
                                    st.metric("Total Rows", f"{total_rows:,}")
                                
                                with st.expander("📊 View Tables"):
                                    for table_name, info in schema_info.items():
                                        st.markdown(f"**{table_name}** ({info.get('row_count', 0):,} rows)")
                                        st.caption(f"Columns: {', '.join(info['column_names'])}")
                                
                                # Store connection info in session state and trigger rerun
                                pending_conn = {
                                    'session_id': session_id,
                                    'db_type': result['db_type'],
                                    'schema_info': schema_info,
                                    'connection_method': 'connection_string',
                                    'db_type_selected': db_type
                                }
                                st.session_state.pending_connection = pending_conn
                                print(f"[DEBUG] Stored pending_connection: {list(pending_conn.keys())}")
                                print("[DEBUG] Triggering rerun to show Start Analyzing button")
                                st.rerun()
                            else:
                                st.error(f"❌ Connection failed: {result['message']}")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    return None
