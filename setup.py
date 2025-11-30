"""
Setup script for initializing the SQL Data Analyst Agent.

Run this script once to:
1. Create the database
2. Initialize the vector store
3. Verify configuration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from database.db_setup import DatabaseSetup
from rag.vector_store import initialize_vector_store


def main():
    """Main setup function."""
    print("=" * 60)
    print("SQL Data Analyst Agent - Initial Setup")
    print("=" * 60)
    print()
    
    # Check configuration
    print("1️⃣  Checking configuration...")
    try:
        settings.validate()
        print("✅ Configuration valid")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Please:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Groq API key to .env (get it from https://console.groq.com/keys)")
        return
    
    # Ensure directories exist
    settings.ensure_directories()
    
    # Setup database
    print("\n2️⃣  Setting up database...")
    if settings.DATABASE_PATH.exists():
        print(f"⚠️  Database already exists at {settings.DATABASE_PATH}")
        response = input("Do you want to recreate it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping database setup...")
        else:
            settings.DATABASE_PATH.unlink()
            db_setup = DatabaseSetup()
            db_setup.setup_complete()
    else:
        db_setup = DatabaseSetup()
        db_setup.setup_complete()
    
    # Initialize vector store
    print("\n3️⃣  Initializing vector store...")
    try:
        initialize_vector_store(force_refresh=False)
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"❌ Error initializing vector store: {e}")
        return
    
    # Success
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\n🚀 You can now run the application:")
    print("   streamlit run ui/app.py")
    print()


if __name__ == "__main__":
    main()
