"""
SQL Explainer Module

Breaks down SQL queries into understandable components.
"""

from typing import Dict, List
import re


class SQLExplainer:
    """Explains SQL queries in simple terms."""
    
    def __init__(self):
        """Initialize the SQL explainer."""
        pass
    
    def explain_query(self, sql_query: str) -> Dict[str, str]:
        """
        Break down SQL query into components and explain each.
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            Dictionary with query explanation
        """
        explanation = {
            "overview": self._get_overview(sql_query),
            "tables": self._explain_tables(sql_query),
            "joins": self._explain_joins(sql_query),
            "filters": self._explain_filters(sql_query),
            "aggregations": self._explain_aggregations(sql_query),
            "ordering": self._explain_ordering(sql_query),
            "complexity": self._assess_complexity(sql_query),
            "tips": self._get_tips(sql_query)
        }
        
        return explanation
    
    def _get_overview(self, sql_query: str) -> str:
        """Get high-level overview of what query does."""
        query_lower = sql_query.lower()
        
        if "group by" in query_lower and "sum" in query_lower:
            return "This query aggregates data to calculate totals grouped by categories"
        elif "join" in query_lower:
            return "This query combines data from multiple related tables"
        elif "where" in query_lower and "between" in query_lower:
            return "This query filters data within a specific range"
        elif "order by" in query_lower and "limit" in query_lower:
            return "This query ranks and returns top results"
        else:
            return "This query retrieves data from the database"
    
    def _explain_tables(self, sql_query: str) -> List[Dict[str, str]]:
        """Explain which tables are used and why."""
        tables = []
        
        # Extract FROM clause
        from_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
        if from_match:
            table_name = from_match.group(1)
            tables.append({
                "name": table_name,
                "purpose": f"Primary data source: {table_name}",
                "type": "Main table"
            })
        
        # Extract JOIN tables
        join_matches = re.finditer(r'JOIN\s+(\w+)', sql_query, re.IGNORECASE)
        for match in join_matches:
            table_name = match.group(1)
            tables.append({
                "name": table_name,
                "purpose": f"Connected data from {table_name}",
                "type": "Joined table"
            })
        
        return tables
    
    def _explain_joins(self, sql_query: str) -> List[Dict[str, str]]:
        """Explain how tables are connected."""
        joins = []
        
        join_patterns = [
            (r'(INNER\s+)?JOIN\s+(\w+)\s+ON\s+([^WHERE^GROUP^ORDER^;]+)', 'INNER JOIN'),
            (r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^WHERE^GROUP^ORDER^;]+)', 'LEFT JOIN'),
            (r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^WHERE^GROUP^ORDER^;]+)', 'RIGHT JOIN')
        ]
        
        for pattern, join_type in join_patterns:
            matches = re.finditer(pattern, sql_query, re.IGNORECASE)
            for match in matches:
                if join_type == 'INNER JOIN':
                    table = match.group(2)
                    condition = match.group(3).strip()
                else:
                    table = match.group(1)
                    condition = match.group(2).strip()
                
                joins.append({
                    "type": join_type,
                    "table": table,
                    "condition": condition,
                    "explanation": self._explain_join_type(join_type)
                })
        
        return joins
    
    def _explain_join_type(self, join_type: str) -> str:
        """Explain what a join type does."""
        explanations = {
            "INNER JOIN": "Returns only matching records from both tables",
            "LEFT JOIN": "Returns all records from left table, matching from right",
            "RIGHT JOIN": "Returns all records from right table, matching from left",
            "FULL JOIN": "Returns all records from both tables"
        }
        return explanations.get(join_type, "Combines tables based on a relationship")
    
    def _explain_filters(self, sql_query: str) -> List[Dict[str, str]]:
        """Explain WHERE clause filters."""
        filters = []
        
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP BY|ORDER BY|LIMIT|;|$)', sql_query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            
            # Split by AND/OR
            conditions = re.split(r'\s+(?:AND|OR)\s+', where_clause, flags=re.IGNORECASE)
            
            for condition in conditions:
                filters.append({
                    "condition": condition.strip(),
                    "purpose": self._explain_condition(condition.strip())
                })
        
        return filters
    
    def _explain_condition(self, condition: str) -> str:
        """Explain a filter condition."""
        if "=" in condition:
            return "Filters for exact matches"
        elif ">" in condition or "<" in condition:
            return "Filters for values in a range"
        elif "LIKE" in condition.upper():
            return "Filters for text patterns"
        elif "IN" in condition.upper():
            return "Filters for values in a list"
        elif "BETWEEN" in condition.upper():
            return "Filters for values between two points"
        else:
            return "Applies a filter condition"
    
    def _explain_aggregations(self, sql_query: str) -> List[Dict[str, str]]:
        """Explain aggregation functions."""
        aggregations = []
        
        agg_functions = {
            "SUM": "Adds up all values",
            "AVG": "Calculates average value",
            "COUNT": "Counts number of records",
            "MAX": "Finds maximum value",
            "MIN": "Finds minimum value"
        }
        
        for func, explanation in agg_functions.items():
            pattern = rf'{func}\s*\(([^)]+)\)'
            matches = re.finditer(pattern, sql_query, re.IGNORECASE)
            for match in matches:
                column = match.group(1).strip()
                aggregations.append({
                    "function": func,
                    "column": column,
                    "purpose": explanation
                })
        
        # Check for GROUP BY
        group_match = re.search(r'GROUP BY\s+(.+?)(?:HAVING|ORDER BY|LIMIT|;|$)', sql_query, re.IGNORECASE)
        if group_match:
            group_cols = group_match.group(1).strip()
            aggregations.append({
                "function": "GROUP BY",
                "column": group_cols,
                "purpose": f"Groups results by {group_cols}"
            })
        
        return aggregations
    
    def _explain_ordering(self, sql_query: str) -> Dict[str, str]:
        """Explain ORDER BY and LIMIT."""
        ordering = {}
        
        order_match = re.search(r'ORDER BY\s+(.+?)(?:LIMIT|;|$)', sql_query, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1).strip()
            direction = "descending" if "DESC" in order_clause.upper() else "ascending"
            column = re.sub(r'\s+(ASC|DESC)', '', order_clause, flags=re.IGNORECASE).strip()
            
            ordering["order_by"] = {
                "column": column,
                "direction": direction,
                "purpose": f"Sorts results by {column} in {direction} order"
            }
        
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_query, re.IGNORECASE)
        if limit_match:
            limit_value = limit_match.group(1)
            ordering["limit"] = {
                "value": limit_value,
                "purpose": f"Returns only the top {limit_value} results"
            }
        
        return ordering
    
    def _assess_complexity(self, sql_query: str) -> Dict[str, any]:  # type: ignore
        """Assess query complexity."""
        complexity_score = 0
        factors = []
        
        query_lower = sql_query.lower()
        
        # Count complexity factors
        if "join" in query_lower:
            join_count = query_lower.count("join")
            complexity_score += join_count * 2
            factors.append(f"{join_count} table join(s)")
        
        if "group by" in query_lower:
            complexity_score += 2
            factors.append("Aggregation with grouping")
        
        if "having" in query_lower:
            complexity_score += 1
            factors.append("Post-aggregation filtering")
        
        if "subquery" in query_lower or query_lower.count("select") > 1:
            complexity_score += 3
            factors.append("Subqueries")
        
        if "case" in query_lower:
            complexity_score += 2
            factors.append("Conditional logic")
        
        # Determine level
        if complexity_score <= 2:
            level = "Simple"
            description = "Straightforward query, easy to understand and optimize"
        elif complexity_score <= 5:
            level = "Moderate"
            description = "Moderately complex, requires some SQL knowledge"
        else:
            level = "Complex"
            description = "Advanced query, may benefit from optimization"
        
        return {
            "score": complexity_score,
            "level": level,
            "description": description,
            "factors": factors
        }
    
    def _get_tips(self, sql_query: str) -> List[str]:
        """Get tips for improving the query."""
        tips = []
        query_lower = sql_query.lower()
        
        if "select *" in query_lower:
            tips.append("💡 Specify only needed columns instead of SELECT * for better performance")
        
        if "join" in query_lower and "where" not in query_lower:
            tips.append("💡 Consider adding WHERE clauses to filter data before joining")
        
        if query_lower.count("join") > 2:
            tips.append("💡 Multiple joins can be slow - consider if all are necessary")
        
        if "group by" in query_lower and "having" not in query_lower:
            tips.append("💡 Use HAVING clause to filter aggregated results")
        
        if "order by" in query_lower and "limit" not in query_lower:
            tips.append("💡 Add LIMIT when sorting to improve performance")
        
        if not tips:
            tips.append("✅ Query looks well-optimized!")
        
        return tips
