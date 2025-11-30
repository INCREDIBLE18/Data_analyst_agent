"""
Query Template Library

Pre-built complex SQL queries for common analytics patterns.
"""

from typing import Dict, List


class QueryTemplates:
    """Library of pre-built SQL query templates."""
    
    def __init__(self):
        """Initialize query templates."""
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load all query templates."""
        return {
            "rfm_analysis": {
                "name": "RFM Analysis (Recency, Frequency, Monetary)",
                "description": "Segment customers based on purchase behavior",
                "category": "Customer Segmentation",
                "difficulty": "Advanced",
                "query": """
-- RFM Analysis: Recency, Frequency, Monetary Value
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        -- Recency: Days since last order
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) AS recency_days,
        -- Frequency: Number of orders
        COUNT(DISTINCT o.order_id) AS frequency,
        -- Monetary: Total spending
        SUM(oi.quantity * oi.unit_price) AS monetary_value
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.first_name, c.last_name
),
rfm_scores AS (
    SELECT 
        *,
        -- Assign RFM scores (1-5, 5 being best)
        CASE 
            WHEN recency_days <= 30 THEN 5
            WHEN recency_days <= 60 THEN 4
            WHEN recency_days <= 90 THEN 3
            WHEN recency_days <= 180 THEN 2
            ELSE 1
        END AS r_score,
        CASE 
            WHEN frequency >= 10 THEN 5
            WHEN frequency >= 7 THEN 4
            WHEN frequency >= 5 THEN 3
            WHEN frequency >= 3 THEN 2
            ELSE 1
        END AS f_score,
        CASE 
            WHEN monetary_value >= 1000 THEN 5
            WHEN monetary_value >= 500 THEN 4
            WHEN monetary_value >= 250 THEN 3
            WHEN monetary_value >= 100 THEN 2
            ELSE 1
        END AS m_score
    FROM customer_rfm
)
SELECT 
    customer_id,
    customer_name,
    recency_days,
    frequency,
    ROUND(monetary_value, 2) AS total_spending,
    r_score || f_score || m_score AS rfm_segment,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 4 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Potential Loyalists'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary_value DESC
LIMIT 50;
"""
            },
            "cohort_analysis": {
                "name": "Cohort Analysis by Month",
                "description": "Track customer retention over time by their first purchase month",
                "category": "Customer Retention",
                "difficulty": "Advanced",
                "query": """
-- Cohort Analysis: Track retention by first purchase month
WITH first_purchase AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
purchase_activity AS (
    SELECT 
        fp.customer_id,
        fp.cohort_month,
        strftime('%Y-%m', o.order_date) AS purchase_month,
        -- Calculate months since first purchase
        (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', fp.cohort_month) AS INTEGER)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', fp.cohort_month) AS INTEGER)) AS months_since_first
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id
)
SELECT 
    cohort_month,
    months_since_first,
    COUNT(DISTINCT customer_id) AS active_customers
FROM purchase_activity
GROUP BY cohort_month, months_since_first
ORDER BY cohort_month, months_since_first;
"""
            },
            "product_affinity": {
                "name": "Product Affinity Analysis",
                "description": "Find products frequently bought together",
                "category": "Product Analytics",
                "difficulty": "Advanced",
                "query": """
-- Product Affinity: Find products frequently bought together
WITH product_pairs AS (
    SELECT 
        oi1.product_id AS product_a_id,
        p1.name AS product_a,
        oi2.product_id AS product_b_id,
        p2.name AS product_b,
        COUNT(DISTINCT oi1.order_id) AS times_bought_together
    FROM order_items oi1
    JOIN order_items oi2 ON oi1.order_id = oi2.order_id 
        AND oi1.product_id < oi2.product_id
    JOIN products p1 ON oi1.product_id = p1.product_id
    JOIN products p2 ON oi2.product_id = p2.product_id
    GROUP BY oi1.product_id, p1.name, oi2.product_id, p2.name
    HAVING COUNT(DISTINCT oi1.order_id) >= 2
)
SELECT 
    product_a,
    product_b,
    times_bought_together,
    ROUND(times_bought_together * 100.0 / 
        (SELECT COUNT(DISTINCT order_id) FROM orders), 2) AS affinity_percentage
FROM product_pairs
ORDER BY times_bought_together DESC
LIMIT 20;
"""
            },
            "sales_trends": {
                "name": "Sales Trend Analysis with Growth",
                "description": "Monthly sales with month-over-month growth rates",
                "category": "Sales Analytics",
                "difficulty": "Intermediate",
                "query": """
-- Sales Trends with MoM Growth
WITH monthly_sales AS (
    SELECT 
        strftime('%Y-%m', o.order_date) AS month,
        COUNT(DISTINCT o.order_id) AS order_count,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        AVG(oi.quantity * oi.unit_price) AS avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY strftime('%Y-%m', o.order_date)
),
with_previous AS (
    SELECT 
        month,
        order_count,
        unique_customers,
        ROUND(total_revenue, 2) AS total_revenue,
        ROUND(avg_order_value, 2) AS avg_order_value,
        LAG(total_revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly_sales
)
SELECT 
    month,
    order_count,
    unique_customers,
    total_revenue,
    avg_order_value,
    ROUND(((total_revenue - prev_revenue) / prev_revenue * 100), 2) AS revenue_growth_pct
FROM with_previous
ORDER BY month DESC;
"""
            },
            "customer_lifetime_value": {
                "name": "Customer Lifetime Value (CLV)",
                "description": "Calculate total value and metrics per customer",
                "category": "Customer Analytics",
                "difficulty": "Intermediate",
                "query": """
-- Customer Lifetime Value Analysis
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS lifetime_value,
    AVG(oi.quantity * oi.unit_price) AS avg_order_value,
    MIN(o.order_date) AS first_purchase,
    MAX(o.order_date) AS last_purchase,
    JULIANDAY(MAX(o.order_date)) - JULIANDAY(MIN(o.order_date)) AS customer_lifespan_days,
    ROUND(SUM(oi.quantity * oi.unit_price) / 
        NULLIF((JULIANDAY(MAX(o.order_date)) - JULIANDAY(MIN(o.order_date))) / 30, 0), 2) AS avg_monthly_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
HAVING total_orders > 0
ORDER BY lifetime_value DESC
LIMIT 25;
"""
            },
            "abc_analysis": {
                "name": "ABC Analysis (Product Classification)",
                "description": "Classify products by revenue contribution (Pareto principle)",
                "category": "Product Analytics",
                "difficulty": "Advanced",
                "query": """
-- ABC Analysis: Classify products by revenue contribution
WITH product_revenue AS (
    SELECT 
        p.product_id,
        p.name AS product_name,
        p.category,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        SUM(oi.quantity) AS total_quantity_sold
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.name, p.category
),
with_cumulative AS (
    SELECT 
        *,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative_revenue,
        SUM(total_revenue) OVER () AS total_revenue_all,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank
    FROM product_revenue
)
SELECT 
    product_id,
    product_name,
    category,
    ROUND(total_revenue, 2) AS revenue,
    total_quantity_sold,
    revenue_rank,
    ROUND(cumulative_revenue * 100.0 / total_revenue_all, 2) AS cumulative_pct,
    CASE 
        WHEN cumulative_revenue * 100.0 / total_revenue_all <= 80 THEN 'A - High Value'
        WHEN cumulative_revenue * 100.0 / total_revenue_all <= 95 THEN 'B - Medium Value'
        ELSE 'C - Low Value'
    END AS abc_classification
FROM with_cumulative
ORDER BY revenue_rank;
"""
            },
            "sales_funnel": {
                "name": "Sales Conversion Funnel",
                "description": "Track conversion through the sales process",
                "category": "Sales Analytics",
                "difficulty": "Intermediate",
                "query": """
-- Sales Funnel Analysis
WITH funnel_stages AS (
    SELECT 
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN customer_id IN (SELECT customer_id FROM orders) THEN customer_id END) AS customers_with_orders,
        COUNT(DISTINCT CASE WHEN customer_id IN (
            SELECT o.customer_id FROM orders o 
            JOIN order_items oi ON o.order_id = oi.order_id 
            GROUP BY o.customer_id 
            HAVING COUNT(DISTINCT o.order_id) > 1
        ) THEN customer_id END) AS repeat_customers,
        COUNT(DISTINCT CASE WHEN customer_id IN (
            SELECT o.customer_id FROM orders o 
            JOIN order_items oi ON o.order_id = oi.order_id 
            GROUP BY o.customer_id 
            HAVING COUNT(DISTINCT o.order_id) >= 5
        ) THEN customer_id END) AS loyal_customers
    FROM customers
)
SELECT 
    'Total Customers' AS stage,
    total_customers AS count,
    100.0 AS conversion_rate,
    NULL AS dropoff_rate
FROM funnel_stages
UNION ALL
SELECT 
    'Purchased Once',
    customers_with_orders,
    ROUND(customers_with_orders * 100.0 / total_customers, 2),
    ROUND((total_customers - customers_with_orders) * 100.0 / total_customers, 2)
FROM funnel_stages
UNION ALL
SELECT 
    'Repeat Customers',
    repeat_customers,
    ROUND(repeat_customers * 100.0 / total_customers, 2),
    ROUND((customers_with_orders - repeat_customers) * 100.0 / customers_with_orders, 2)
FROM funnel_stages
UNION ALL
SELECT 
    'Loyal Customers (5+ orders)',
    loyal_customers,
    ROUND(loyal_customers * 100.0 / total_customers, 2),
    ROUND((repeat_customers - loyal_customers) * 100.0 / repeat_customers, 2)
FROM funnel_stages;
"""
            },
            "category_performance": {
                "name": "Product Category Performance",
                "description": "Compare performance across product categories",
                "category": "Product Analytics",
                "difficulty": "Intermediate",
                "query": """
-- Category Performance Dashboard
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) AS total_products,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    ROUND(AVG(oi.quantity * oi.unit_price), 2) AS avg_order_value,
    ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS revenue_per_order,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY total_revenue DESC;
"""
            }
        }
    
    def get_all_templates(self) -> Dict[str, Dict[str, str]]:
        """Get all available templates."""
        return self.templates
    
    def get_template(self, template_id: str) -> Dict[str, str]:  # type: ignore
        """Get a specific template by ID."""
        return self.templates.get(template_id)  # type: ignore
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict[str, str]]:
        """Get templates filtered by category."""
        return {
            tid: template 
            for tid, template in self.templates.items() 
            if template["category"] == category
        }
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set(template["category"] for template in self.templates.values())
        return sorted(list(categories))
