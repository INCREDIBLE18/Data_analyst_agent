### Visual Aid: Show Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Streamlit)                │
│  • Query Input  • Results Display  • Visualizations          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    AGENT LAYER (LangChain)                   │
│  • SQL Generation  • Error Handling  • Query Optimization    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    RAG LAYER (Chroma)                        │
│  • Schema Indexing  • Semantic Search  • Context Retrieval   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              DATABASE LAYER (SQLAlchemy)                     │
│  • Multi-DB Connections  • Query Execution  • Schema Discovery│
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              CONFIGURATION LAYER                             │
│  • Environment Variables  • Settings  • API Keys             │
└─────────────────────────────────────────────────────────────┘
```
