"""
Query caching system for improved performance.
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class QueryCache:
    """Cache for query results and SQL generation."""
    
    def __init__(self, ttl_minutes: int = 60):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _get_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        key = self._get_key(query)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                entry['hit_count'] = entry.get('hit_count', 0) + 1
                return entry['result']
            else:
                # Expired, remove it
                del self.cache[key]
        
        return None
    
    def set(self, query: str, result: Dict[str, Any]):
        """Cache a query result."""
        key = self._get_key(query)
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now(),
            'query': query,
            'hit_count': 0
        }
    
    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        total_hits = sum(entry.get('hit_count', 0) for entry in self.cache.values())
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'cache_size_mb': len(json.dumps(self.cache, default=str)) / (1024 * 1024)
        }
