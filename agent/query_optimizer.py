"""
Query Optimizer Module

Analyzes SQL queries and provides optimization suggestions.
"""

from typing import Dict, List
import re


class QueryOptimizer:
    """Analyzes and suggests optimizations for SQL queries."""
    
    def __init__(self):
        """Initialize the query optimizer."""
        pass
    
    def analyze(self, sql_query: str, execution_time: float = None) -> Dict[str, any]:  # type: ignore
        """
        Analyze query and provide optimization suggestions.
        
        Args:
            sql_query: SQL query to analyze
            execution_time: Optional execution time in seconds
            
        Returns:
            Dictionary with analysis and suggestions
        """
        analysis = {
            "performance_score": self._calculate_performance_score(sql_query),
            "issues": self._identify_issues(sql_query),
            "suggestions": self._get_suggestions(sql_query),
            "best_practices": self._check_best_practices(sql_query),
            "index_recommendations": self._recommend_indexes(sql_query),
            "execution_plan": self._explain_execution(sql_query)
        }
        
        if execution_time:
            analysis["execution_time"] = execution_time
            analysis["speed_rating"] = self._rate_speed(execution_time)
        
        return analysis
    
    def _calculate_performance_score(self, sql_query: str) -> float:
        """Calculate overall performance score (0-10)."""
        score = 10
        query_lower = sql_query.lower()
        
        # Deduct points for potential issues
        if "select *" in query_lower:
            score -= 2
        
        if query_lower.count("join") > 3:
            score -= 1.5
        
        if "or" in query_lower:
            score -= 1
        
        if "not in" in query_lower:
            score -= 1.5
        
        if query_lower.count("select") > 1:  # Subqueries
            score -= 1
        
        if "function" in query_lower or "cast" in query_lower:
            score -= 0.5
        
        # Add points for good practices
        if "where" in query_lower:
            score += 0.5
        
        if "limit" in query_lower:
            score += 0.5
        
        return max(0, min(10, round(score, 1)))
    
    def _identify_issues(self, sql_query: str) -> List[Dict[str, str]]:
        """Identify potential performance issues."""
        issues = []
        query_lower = sql_query.lower()
        
        # SELECT * issue
        if "select *" in query_lower:
            issues.append({
                "severity": "medium",
                "issue": "Using SELECT *",
                "impact": "Retrieves unnecessary columns, increases I/O",
                "solution": "Specify only needed columns"
            })
        
        # Multiple JOINs
        join_count = query_lower.count("join")
        if join_count > 3:
            issues.append({
                "severity": "high",
                "issue": f"{join_count} table joins",
                "impact": "Can significantly slow down query execution",
                "solution": "Consider denormalizing or using materialized views"
            })
        
        # OR conditions
        if " or " in query_lower:
            issues.append({
                "severity": "medium",
                "issue": "OR conditions in WHERE clause",
                "impact": "Prevents efficient index usage",
                "solution": "Use UNION or IN clause instead"
            })
        
        # NOT IN
        if "not in" in query_lower:
            issues.append({
                "severity": "medium",
                "issue": "NOT IN clause",
                "impact": "Less efficient than NOT EXISTS",
                "solution": "Use NOT EXISTS or LEFT JOIN with NULL check"
            })
        
        # Missing WHERE on JOIN
        if "join" in query_lower and "where" not in query_lower:
            issues.append({
                "severity": "low",
                "issue": "No WHERE clause with JOIN",
                "impact": "May return more data than needed",
                "solution": "Add WHERE clause to filter results"
            })
        
        # Cartesian product risk
        from_matches = re.findall(r'from\s+\w+\s*,\s*\w+', query_lower)
        if from_matches:
            issues.append({
                "severity": "high",
                "issue": "Comma-separated FROM (potential cartesian product)",
                "impact": "Can cause exponential data explosion",
                "solution": "Use explicit JOIN syntax with ON conditions"
            })
        
        return issues
    
    def _get_suggestions(self, sql_query: str) -> List[str]:
        """Get optimization suggestions."""
        suggestions = []
        query_lower = sql_query.lower()
        
        # Index suggestions
        if "where" in query_lower:
            where_match = re.search(r'where\s+(\w+)\s*=', query_lower)
            if where_match:
                column = where_match.group(1)
                suggestions.append(f"🎯 Consider adding an index on '{column}' for faster filtering")
        
        # JOIN optimization
        if "join" in query_lower:
            suggestions.append("🔗 Ensure JOIN columns have indexes for better performance")
            suggestions.append("📊 Filter data with WHERE before joining when possible")
        
        # Aggregation optimization
        if "group by" in query_lower:
            suggestions.append("📈 Consider creating a summary table for frequently used aggregations")
        
        # LIMIT suggestion
        if "order by" in query_lower and "limit" not in query_lower:
            suggestions.append("🎚️ Add LIMIT clause when ordering to reduce result set")
        
        # DISTINCT optimization
        if "distinct" in query_lower:
            suggestions.append("🔍 DISTINCT can be expensive - ensure it's necessary")
        
        # Subquery optimization
        if query_lower.count("select") > 1:
            suggestions.append("🔄 Consider using JOIN instead of subqueries for better performance")
        
        if not suggestions:
            suggestions.append("✅ Query appears well-optimized!")
        
        return suggestions
    
    def _check_best_practices(self, sql_query: str) -> Dict[str, bool]:
        """Check if query follows SQL best practices."""
        query_lower = sql_query.lower()
        
        practices = {
            "specific_columns": "select *" not in query_lower,
            "explicit_joins": "," not in query_lower.split("from")[1].split("where")[0] if "where" in query_lower else True,
            "uses_aliases": " as " in query_lower,
            "filters_early": self._has_where_before_group(query_lower),
            "limits_results": "limit" in query_lower or query_lower.count("select") == 1,
            "proper_indentation": "\n" in sql_query,
            "uppercase_keywords": any(kw.isupper() for kw in ["SELECT", "FROM", "WHERE", "JOIN"] if kw in sql_query)
        }
        
        return practices
    
    def _has_where_before_group(self, query_lower: str) -> bool:
        """Check if WHERE comes before GROUP BY."""
        if "group by" not in query_lower:
            return True
        
        if "where" not in query_lower:
            return False
        
        where_pos = query_lower.index("where")
        group_pos = query_lower.index("group by")
        
        return where_pos < group_pos
    
    def _recommend_indexes(self, sql_query: str) -> List[Dict[str, str]]:
        """Recommend indexes based on query patterns."""
        indexes = []
        query_lower = sql_query.lower()
        
        # WHERE clause columns
        where_matches = re.finditer(r'where\s+(\w+)\s*[=<>]', query_lower)
        for match in where_matches:
            column = match.group(1)
            indexes.append({
                "table": "auto-detected",
                "column": column,
                "type": "B-tree",
                "reason": "Used in WHERE clause for filtering"
            })
        
        # JOIN columns
        join_matches = re.finditer(r'on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', query_lower)
        for match in join_matches:
            indexes.append({
                "table": match.group(1),
                "column": match.group(2),
                "type": "B-tree",
                "reason": "Used in JOIN condition"
            })
            indexes.append({
                "table": match.group(3),
                "column": match.group(4),
                "type": "B-tree",
                "reason": "Used in JOIN condition"
            })
        
        # ORDER BY columns
        order_matches = re.finditer(r'order by\s+(\w+)', query_lower)
        for match in order_matches:
            column = match.group(1)
            indexes.append({
                "table": "auto-detected",
                "column": column,
                "type": "B-tree",
                "reason": "Used in ORDER BY clause for sorting"
            })
        
        # Remove duplicates
        unique_indexes = []
        seen = set()
        for idx in indexes:
            key = (idx['column'], idx['type'])
            if key not in seen:
                seen.add(key)
                unique_indexes.append(idx)
        
        return unique_indexes[:5]  # Limit to top 5 recommendations
    
    def _explain_execution(self, sql_query: str) -> List[str]:
        """Explain likely execution plan."""
        plan = []
        query_lower = sql_query.lower()
        
        # FROM clause
        from_match = re.search(r'from\s+(\w+)', query_lower)
        if from_match:
            table = from_match.group(1)
            plan.append(f"1️⃣ Scan {table} table")
        
        # WHERE clause
        if "where" in query_lower:
            plan.append("2️⃣ Apply WHERE filters (index seek if available)")
        
        # JOINs
        join_count = query_lower.count("join")
        if join_count > 0:
            plan.append(f"3️⃣ Perform {join_count} table join(s)")
        
        # GROUP BY
        if "group by" in query_lower:
            plan.append("4️⃣ Group results and calculate aggregations")
        
        # HAVING
        if "having" in query_lower:
            plan.append("5️⃣ Filter grouped results with HAVING")
        
        # ORDER BY
        if "order by" in query_lower:
            plan.append("6️⃣ Sort results (memory-intensive)")
        
        # LIMIT
        if "limit" in query_lower:
            plan.append("7️⃣ Return top N results")
        
        plan.append("✅ Return final result set to client")
        
        return plan
    
    def _rate_speed(self, execution_time: float) -> str:
        """Rate execution speed."""
        if execution_time < 0.1:
            return "⚡ Blazing Fast"
        elif execution_time < 0.5:
            return "🚀 Fast"
        elif execution_time < 1.0:
            return "✅ Good"
        elif execution_time < 3.0:
            return "⚠️ Acceptable"
        else:
            return "🐌 Slow - Optimization Needed"
