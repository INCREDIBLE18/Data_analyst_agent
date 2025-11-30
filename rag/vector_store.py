"""
Vector store module.

Manages Chroma vector database for semantic search over database schema.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions

from config.settings import settings
from rag.schema_loader import SchemaLoader


class VectorStore:
    """Manages vector store for database schema and documentation."""
    
    def __init__(self):
        """Initialize vector store with Chroma."""
        settings.ensure_directories()
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_PERSIST_DIR)
        )
        
        # Use Chroma's default embedding function (ONNX-based, no API key needed)
        # This is lightweight and works without external dependencies
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection with default embeddings
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"description": "Database schema and documentation"}
        )
        
        self.schema_loader = SchemaLoader()
    
    def initialize_schema_embeddings(self, force_refresh: bool = False) -> None:
        """
        Initialize vector store with database schema embeddings.
        
        Args:
            force_refresh: If True, delete existing embeddings and recreate
        """
        # Check if collection already has documents
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_refresh:
            print(f"✅ Vector store already initialized with {existing_count} documents")
            return
        
        if force_refresh and existing_count > 0:
            print("🔄 Refreshing vector store...")
            # Delete existing collection and recreate
            self.client.delete_collection(settings.CHROMA_COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Database schema and documentation"}
            )
        
        print("📚 Loading database schema...")
        documents = self.schema_loader.get_schema_documents()
        
        print(f"🔢 Creating embeddings for {len(documents)} documents...")
        
        # Prepare data for Chroma
        ids = [f"doc_{i}" for i in range(len(documents))]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not create embeddings: {e}")
            print("📝 Vector store will use default embeddings")
        
        print(f"✅ Vector store initialized with {len(documents)} documents")
    
    def search_schema(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant schema information using semantic search.
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with content and metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        documents = []
        if results.get("documents") and results["documents"] and len(results["documents"]) > 0:  # type: ignore
            for i in range(len(results["documents"][0])):  # type: ignore
                documents.append({
                    "content": results["documents"][0][i],  # type: ignore
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},  # type: ignore
                    "distance": results["distances"][0][i] if results.get("distances") else None  # type: ignore
                })
        
        return documents
    
    def get_relevant_context(self, query: str) -> str:
        """
        Get relevant schema context as formatted string.
        
        Args:
            query: Natural language query
            
        Returns:
            Formatted context string
        """
        documents = self.search_schema(query, n_results=3)
        
        context_parts = ["# Relevant Database Schema Information\n"]
        
        for doc in documents:
            context_parts.append(doc["content"])
            context_parts.append("\n---\n")
        
        return "\n".join(context_parts)
    
    def get_all_tables_summary(self) -> str:
        """
        Get a summary of all tables in the database.
        
        Returns:
            Summary string
        """
        from database.db_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        summary = db_manager.get_database_summary()
        
        lines = ["# Database Summary\n"]
        lines.append(f"Total tables: {summary['table_count']}\n")
        
        for table_name, info in summary["tables"].items():
            lines.append(f"\n## {table_name}")
            lines.append(f"- Rows: {info['row_count']}")
            lines.append(f"- Columns: {', '.join(info['columns'])}")
        
        return "\n".join(lines)


def initialize_vector_store(force_refresh: bool = False) -> VectorStore:
    """
    Helper function to initialize vector store.
    
    Args:
        force_refresh: If True, recreate all embeddings
        
    Returns:
        Initialized VectorStore instance
    """
    vector_store = VectorStore()
    vector_store.initialize_schema_embeddings(force_refresh=force_refresh)
    return vector_store
