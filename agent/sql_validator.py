"""
SQL query validation before execution.
"""
import re
from typing import Dict, List, Any


class SQLValidator:
    """Validate SQL queries for safety and correctness."""
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        r'\bDROP\s+TABLE\b',
        r'\bDROP\s+DATABASE\b',
        r'\bDELETE\s+FROM\b',
        r'\bTRUNCATE\b',
        r'\bUPDATE\s+.*\s+SET\b',
        r'\bINSERT\s+INTO\b',
        r'\bALTER\s+TABLE\b',
        r'\bCREATE\s+TABLE\b',
        r';\s*DROP\b',  # SQL injection
        r'--',  # SQL comments (potential injection)
    ]
    
    def __init__(self):
        self.dangerous_regex = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in self.DANGEROUS_PATTERNS]
    
    def validate(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety and correctness.
        
        Args:
            sql: SQL query string
            
        Returns:
            Dict with 'valid', 'errors', 'warnings'
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # Check for dangerous operations
        for pattern in self.dangerous_regex:
            if pattern.search(sql):
                errors.append(f"Dangerous operation detected: {pattern.pattern}")
        
        # Check for basic SQL syntax
        if not sql.strip().upper().startswith(('SELECT', 'WITH')):
            errors.append("Query must be a SELECT statement")
        
        # Check for unbalanced parentheses
        if sql.count('(') != sql.count(')'):
            errors.append("Unbalanced parentheses")
        
        # Check for multiple statements
        if ';' in sql.rstrip(';'):
            warnings.append("Multiple statements detected - only first will execute")
        
        # Check for SELECT *
        if re.search(r'\bSELECT\s+\*\b', sql, re.IGNORECASE):
            warnings.append("Using SELECT * - consider specifying columns explicitly")
        
        # Check for missing WHERE in large tables
        if 'orders' in sql.lower() and 'where' not in sql.lower():
            warnings.append("Large table query without WHERE clause - may be slow")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
