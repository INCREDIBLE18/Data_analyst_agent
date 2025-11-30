"""
Dynamic vector store management for multi-database support.
"""
import os
import shutil
from typing import Optional, Dict
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from database.schema_discoverer import SchemaDiscoverer
import sqlalchemy


class SimpleEmbeddings(Embeddings):
    """Simple hash-based embeddings as fallback."""
    
    def embed_documents(self, texts):
        """Embed documents using simple hashing."""
        import hashlib
        embeddings = []
        for text in texts:
            # Create a simple 384-dimensional embedding from hash
            hash_obj = hashlib.sha384(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to floats between -1 and 1
            embedding = [((b - 128) / 128.0) for b in hash_bytes]
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Embed query using simple hashing."""
        return self.embed_documents([text])[0]


class DynamicVectorStore:
    """Manage session-based vector stores for different databases."""
    
    def __init__(self, base_persist_dir: str = "session_vector_stores"):
        self.base_persist_dir = base_persist_dir
        self.stores: Dict[str, Chroma] = {}
        
        # Use simple embeddings (no TensorFlow dependencies)
        self.embeddings = SimpleEmbeddings()
        
        # Create base directory if not exists
        os.makedirs(base_persist_dir, exist_ok=True)
    
    def initialize_for_session(
        self,
        session_id: str,
        engine: sqlalchemy.Engine,
        force_rebuild: bool = False
    ) -> Chroma:
        """Initialize vector store for a session from database schema."""
        
        # Check if already initialized
        if session_id in self.stores and not force_rebuild:
            return self.stores[session_id]
        
        # Set up persist directory for this session
        persist_dir = os.path.join(self.base_persist_dir, session_id)
        
        # If force rebuild, clear existing
        if force_rebuild and os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            os.makedirs(persist_dir, exist_ok=True)
        
        # Discover schema
        discoverer = SchemaDiscoverer()
        schema = discoverer.discover_full_schema(engine)
        
        # Generate schema documents
        documents = discoverer.generate_schema_documents(schema)
        
        # Create vector store
        vectorstore = Chroma.from_texts(
            texts=documents,
            embedding=self.embeddings,
            persist_directory=persist_dir
        )
        
        # Cache the store
        self.stores[session_id] = vectorstore
        
        return vectorstore
    
    def get_store(self, session_id: str) -> Optional[Chroma]:
        """Get existing vector store for session."""
        
        # Return from cache if available
        if session_id in self.stores:
            return self.stores[session_id]
        
        # Try to load from disk
        persist_dir = os.path.join(self.base_persist_dir, session_id)
        if os.path.exists(persist_dir):
            vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=persist_dir
            )
            self.stores[session_id] = vectorstore
            return vectorstore
        
        return None
    
    def cleanup_session(self, session_id: str):
        """Clean up vector store for session."""
        
        # Remove from cache
        if session_id in self.stores:
            del self.stores[session_id]
        
        # Remove from disk
        persist_dir = os.path.join(self.base_persist_dir, session_id)
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
    
    def rebuild_store(self, session_id: str, engine: sqlalchemy.Engine) -> Chroma:
        """Rebuild vector store from scratch."""
        return self.initialize_for_session(session_id, engine, force_rebuild=True)
