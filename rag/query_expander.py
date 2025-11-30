"""
Query expansion for better RAG retrieval.
"""
from typing import List
from langchain_groq import ChatGroq
from config.settings import settings


class QueryExpander:
    """Expand user queries for better semantic search."""
    
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.LLM_MODEL,  # type: ignore
            api_key=settings.GROQ_API_KEY,  # type: ignore
            temperature=0.3  # type: ignore
        )
    
    def expand_query(self, user_query: str) -> List[str]:
        """
        Generate alternative phrasings of the query.
        
        Args:
            user_query: Original user query
            
        Returns:
            List of expanded queries including original
        """
        prompt = f"""Given this data analysis question, generate 3 alternative ways to phrase it that mean the same thing. Focus on different SQL-related terms.

Original Question: {user_query}

Generate 3 alternative phrasings (one per line):
"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            content_str = str(content) if not isinstance(content, str) else content
            
            # Parse alternatives
            alternatives = [line.strip() for line in content_str.split('\n') if line.strip()]
            alternatives = [alt.lstrip('123456789.-) ') for alt in alternatives]
            
            # Return original + alternatives (max 4 total)
            return [user_query] + alternatives[:3]
            
        except Exception as e:
            print(f"Query expansion failed: {e}")
            return [user_query]
