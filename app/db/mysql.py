from typing import Optional, List, Dict, Any, Tuple
import mysql.connector
from mysql.connector import Error
import json
import os

class MySQLConnector:
    def __init__(self):
        self.connection = None
        self.config = self._load_config()

    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'database.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'host': 'localhost',
                'user': 'root',
                'password': 'sharad1234',
                'database': 'schools'
            }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def get_table_structure(self, table_name: str) -> Dict:
        """Get detailed structure of a specific table"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get column information
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample = cursor.fetchone()
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
            total = cursor.fetchone()['total']
            
            return {
                "name": table_name,
                "columns": columns,
                "sample_data": sample if sample else {},
                "total_records": total
            }
        except Error as e:
            print(f"Error getting table structure: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_all_tables(self) -> Dict[str, Dict]:
        """Get structure of all tables in the database"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get all table names
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            result = {}
            for table in tables:
                table_name = list(table.values())[0]
                table_info = self.get_table_structure(table_name)
                result[table_name] = {
                    "column_name": [col['Field'] for col in table_info['columns']],
                    "sample_data": table_info['sample_data'],
                    "total_records": table_info['total_records']
                }
            
            return result
        except Error as e:
            print(f"Error fetching tables: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query: str) -> Tuple[List[Dict], int]:
        """Execute a query and return results with total count"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Execute the main query
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get total count based on query type
            query_lower = query.lower()
            
            if "group by" in query_lower:
                # For GROUP BY queries, count the number of groups
                total_count = len(results)
            elif "count(*)" in query_lower:
                # If query already has COUNT(*), use that result
                total_count = results[0]['COUNT(*)'] if results else 0
            else:
                # For regular queries, count the results
                total_count = len(results)
            
            return results, total_count
        except Error as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close() 