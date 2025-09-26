import os
import json
from supabase import create_client
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Test Supabase connection and table access"""
    # Load environment variables
    load_dotenv()
    
    # Print environment variables for debugging
    supabase_url = os.getenv("SUPABASE_URL")
    api_key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {api_key[:5]}..." if api_key else "API KEY NOT FOUND")
    
    if not supabase_url or not api_key:
        logger.error("Supabase credentials not found in environment variables")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, api_key)
        logger.info("Supabase client initialized successfully")
        
        # List tables in the database
        logger.info("Attempting to list tables...")
        try:
            # Try to query information_schema to list all tables
            tables_query = """
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
            """
            
            # Note: This might not work directly with the Supabase client
            # as it may not have permission to query information_schema
            response = supabase.rpc("exec_sql", {"sql": tables_query}).execute()
            print("Tables in database:", response)
        except Exception as e:
            logger.warning(f"Could not list tables using information_schema: {str(e)}")
            logger.info("This is normal if your API key doesn't have admin privileges")
        
        # Try to access specific tables
        schemas_to_check = ["public", "raw", "RAW"]
        tables_to_check = ["restaurants", "reviews", "restaurant_details"]
        
        for schema in schemas_to_check:
            logger.info(f"Checking schema: {schema}")
            for table in tables_to_check:
                table_path = f"{schema}.{table}"
                try:
                    # Try different ways to reference the table
                    try:
                        # Method 1: Using table() method
                        response = supabase.table(table_path).select("*").limit(1).execute()
                        logger.info(f"✅ Successfully accessed table using: supabase.table('{table_path}')")
                        print(f"Response data: {response.data}")
                    except Exception as e1:
                        logger.warning(f"Method 1 failed: {str(e1)}")
                        
                        # Method 2: Using from_() method
                        try:
                            response = supabase.from_(table_path).select("*").limit(1).execute()
                            logger.info(f"✅ Successfully accessed table using: supabase.from_('{table_path}')")
                            print(f"Response data: {response.data}")
                        except Exception as e2:
                            logger.warning(f"Method 2 failed: {str(e2)}")
                            
                            # Method 3: Using from_() with schema and table separately
                            try:
                                response = supabase.from_(schema).table(table).select("*").limit(1).execute()
                                logger.info(f"✅ Successfully accessed table using: supabase.from_('{schema}').table('{table}')")
                                print(f"Response data: {response.data}")
                            except Exception as e3:
                                logger.warning(f"Method 3 failed: {str(e3)}")
                                logger.error(f"❌ All methods failed for table {table_path}")
                except Exception as e:
                    logger.error(f"❌ Could not access table {table_path}: {str(e)}")
        
        # Try a simple insert to public.test_table (testing write access)
        try:
            logger.info("Testing write access with simple insert...")
            
            # First create a test table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS public.test_table (
                id SERIAL PRIMARY KEY,
                test_column TEXT
            );
            """
            
            try:
                supabase.rpc("exec_sql", {"sql": create_table_query}).execute()
                logger.info("Created test table")
            except Exception as e:
                logger.warning(f"Could not create test table: {str(e)}")
                logger.info("This is normal if your API key doesn't have admin privileges")
            
            # Try to insert data
            test_data = {"test_column": "test_value"}
            response = supabase.table("test_table").insert(test_data).execute()
            logger.info(f"✅ Successfully inserted data into test_table: {response.data}")
        except Exception as e:
            logger.error(f"❌ Could not insert data: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()