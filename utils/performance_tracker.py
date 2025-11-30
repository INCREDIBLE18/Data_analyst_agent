"""
Track and analyze query performance metrics.
"""
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class PerformanceTracker:
    """Track query execution performance."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.stats_by_pattern: Dict[str, List[float]] = defaultdict(list)
    
    def track_query(self, query: str, sql: str, execution_time: float, 
                    row_count: int, success: bool):
        """Record query execution metrics."""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'sql': sql,
            'execution_time': execution_time,
            'row_count': row_count,
            'success': success,
            'query_length': len(sql),
            'has_join': 'join' in sql.lower(),
            'has_aggregation': any(agg in sql.lower() for agg in ['sum', 'avg', 'count', 'max', 'min']),
            'has_subquery': '(' in sql and 'select' in sql.lower().split('from')[0] if 'from' in sql.lower() else False
        }
        
        self.metrics.append(metric)
        
        # Categorize by complexity
        complexity = self._get_complexity(metric)
        self.stats_by_pattern[complexity].append(execution_time)
    
    def _get_complexity(self, metric: Dict[str, Any]) -> str:
        """Determine query complexity."""
        if metric['has_subquery']:
            return 'complex'
        elif metric['has_join'] and metric['has_aggregation']:
            return 'medium'
        else:
            return 'simple'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.metrics:
            return {
                'total_queries': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0
            }
        
        total = len(self.metrics)
        successful = sum(1 for m in self.metrics if m['success'])
        avg_time = sum(m['execution_time'] for m in self.metrics) / total
        
        # Stats by complexity
        complexity_stats = {}
        for complexity, times in self.stats_by_pattern.items():
            complexity_stats[complexity] = {
                'count': len(times),
                'avg_time': sum(times) / len(times) if times else 0.0,
                'max_time': max(times) if times else 0.0
            }
        
        return {
            'total_queries': total,
            'successful_queries': successful,
            'failed_queries': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0.0,
            'avg_execution_time': avg_time,
            'total_rows_returned': sum(m['row_count'] for m in self.metrics),
            'complexity_breakdown': complexity_stats,
            'slowest_query': max(self.metrics, key=lambda m: m['execution_time']) if self.metrics else None
        }
    
    def get_recommendations(self) -> List[str]:
        """Get performance recommendations based on metrics."""
        stats = self.get_statistics()
        recommendations = []
        
        if stats['avg_execution_time'] > 2.0:
            recommendations.append("⚠️ Average query time is high - consider adding indexes")
        
        if stats['success_rate'] < 80:
            recommendations.append("⚠️ Success rate is low - review error patterns")
        
        complexity_stats = stats.get('complexity_breakdown', {})
        if 'complex' in complexity_stats and complexity_stats['complex']['avg_time'] > 3.0:
            recommendations.append("💡 Complex queries are slow - consider materialized views")
        
        return recommendations
    
    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        self.stats_by_pattern.clear()
