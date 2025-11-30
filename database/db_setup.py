"""
Database setup and initialization module.

This module creates the SQLite database schema for sales analytics
and populates it with sample data.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import random

from config.settings import settings


class DatabaseSetup:
    """Handles database schema creation and data population."""
    
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        """
        Initialize database setup.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def create_schema(self) -> None:
        """Create the database schema with all tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                country TEXT NOT NULL,
                segment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT NOT NULL,
                total_amount REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database schema created successfully")
    
    def populate_sample_data(self) -> None:
        """Populate the database with sample sales data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sample data
        customers_data = [
            ("John Smith", "john.smith@email.com", "USA", "Enterprise"),
            ("Emma Johnson", "emma.j@email.com", "UK", "SMB"),
            ("Michael Chen", "m.chen@email.com", "Canada", "Enterprise"),
            ("Sarah Williams", "s.williams@email.com", "Australia", "Mid-Market"),
            ("David Brown", "d.brown@email.com", "USA", "SMB"),
            ("Lisa Anderson", "l.anderson@email.com", "Germany", "Enterprise"),
            ("James Wilson", "j.wilson@email.com", "France", "Mid-Market"),
            ("Maria Garcia", "m.garcia@email.com", "Spain", "SMB"),
            ("Robert Taylor", "r.taylor@email.com", "USA", "Enterprise"),
            ("Jennifer Lee", "j.lee@email.com", "Singapore", "Mid-Market"),
        ]
        
        created_at = datetime.now().isoformat()
        cursor.executemany(
            "INSERT INTO customers (name, email, country, segment, created_at) VALUES (?, ?, ?, ?, ?)",
            [(name, email, country, segment, created_at) for name, email, country, segment in customers_data]
        )
        
        # Products data
        products_data = [
            ("Laptop Pro 15", "Electronics", 1299.99),
            ("Wireless Mouse", "Electronics", 29.99),
            ("Office Chair Deluxe", "Furniture", 399.99),
            ("Standing Desk", "Furniture", 599.99),
            ("Mechanical Keyboard", "Electronics", 149.99),
            ("Monitor 27-inch", "Electronics", 349.99),
            ("Desk Lamp LED", "Furniture", 49.99),
            ("Webcam HD", "Electronics", 89.99),
            ("Headphones Premium", "Electronics", 199.99),
            ("Notebook Set", "Office Supplies", 19.99),
            ("Pen Collection", "Office Supplies", 12.99),
            ("Whiteboard", "Office Supplies", 79.99),
            ("Ergonomic Footrest", "Furniture", 69.99),
            ("Cable Organizer", "Office Supplies", 24.99),
            ("USB Hub 7-Port", "Electronics", 39.99),
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, price, created_at) VALUES (?, ?, ?, ?)",
            [(name, category, price, created_at) for name, category, price in products_data]
        )
        
        # Generate orders (last 6 months)
        customer_ids = list(range(1, 11))
        product_ids = list(range(1, 16))
        statuses = ["completed", "completed", "completed", "pending", "shipped"]
        
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(100):  # 100 orders
            customer_id = random.choice(customer_ids)
            order_date = start_date + timedelta(days=random.randint(0, 180))
            status = random.choice(statuses)
            
            # Insert order
            cursor.execute(
                "INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (?, ?, ?, ?)",
                (customer_id, order_date.isoformat(), status, 0.0)  # Total will be updated
            )
            order_id = cursor.lastrowid
            
            # Add 1-4 items per order
            num_items = random.randint(1, 4)
            total_amount = 0.0
            
            for _ in range(num_items):
                product_id = random.choice(product_ids)
                quantity = random.randint(1, 5)
                
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                unit_price = cursor.fetchone()[0]
                
                total_amount += unit_price * quantity
                
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, quantity, unit_price)
                )
            
            # Update order total
            cursor.execute(
                "UPDATE orders SET total_amount = ? WHERE id = ?",
                (total_amount, order_id)
            )
        
        conn.commit()
        conn.close()
        print("✅ Sample data populated successfully")
    
    def get_schema_description(self) -> str:
        """
        Get a human-readable description of the database schema.
        
        Returns:
            String description of the schema for RAG indexing
        """
        return """
# Sales Analytics Database Schema

This database contains sales and customer data for analytics purposes.

## Tables Overview

### customers
Stores customer information and segmentation data.
- id (INTEGER PRIMARY KEY): Unique customer identifier
- name (TEXT): Customer full name
- email (TEXT UNIQUE): Customer email address
- country (TEXT): Customer's country
- segment (TEXT): Customer segment (Enterprise, Mid-Market, SMB)
- created_at (TEXT): Account creation timestamp

### products
Product catalog with pricing information.
- id (INTEGER PRIMARY KEY): Unique product identifier
- name (TEXT): Product name
- category (TEXT): Product category (Electronics, Furniture, Office Supplies)
- price (REAL): Product price in USD
- created_at (TEXT): Product creation timestamp

### orders
Customer order transactions.
- id (INTEGER PRIMARY KEY): Unique order identifier
- customer_id (INTEGER): Foreign key to customers table
- order_date (TEXT): Order placement date
- status (TEXT): Order status (completed, pending, shipped)
- total_amount (REAL): Total order value in USD

### order_items
Individual line items for each order.
- id (INTEGER PRIMARY KEY): Unique item identifier
- order_id (INTEGER): Foreign key to orders table
- product_id (INTEGER): Foreign key to products table
- quantity (INTEGER): Number of units ordered
- unit_price (REAL): Price per unit at time of order

## Relationships
- customers (1) → (many) orders
- orders (1) → (many) order_items
- products (1) → (many) order_items

## Common Analytics Queries
- Total sales by product category
- Customer lifetime value by segment
- Monthly sales trends
- Top selling products
- Customer purchase frequency
- Average order value
- Revenue by country
"""
    
    def setup_complete(self) -> None:
        """Run complete database setup process."""
        print("🚀 Starting database setup...")
        self.create_schema()
        self.populate_sample_data()
        print("✅ Database setup complete!")
        print(f"📁 Database location: {self.db_path}")


def main():
    """Main entry point for database setup."""
    setup = DatabaseSetup()
    setup.setup_complete()


if __name__ == "__main__":
    main()
