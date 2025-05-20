import google.generativeai as genai
from typing import Dict, Any, Tuple, List
import json
import os
import re

class GeminiService:
    def __init__(self):
        # Initialize Gemini with your API key
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDSHeQahfIPuEVBCmQCZxopN6oOVLqxVAk")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.db_structure = None

    def _clean_sql_query(self, query: str) -> str:
        # Remove markdown formatting if present
        query = re.sub(r'```sql\s*', '', query)
        query = re.sub(r'```\s*$', '', query)
        return query.strip()

    def set_database_structure(self, tables_info: Dict[str, Dict]):
        """Set the database structure for query generation"""
        self.db_structure = tables_info

    def _format_table_info(self) -> str:
        """Format table information for the prompt"""
        if not self.db_structure:
            return "No database structure available"
            
        tables_description = []
        for table_name, table_info in self.db_structure.items():
            columns = table_info.get("column_name", [])
            sample = table_info.get("sample_data", {})
            total_records = table_info.get("total_records", 0)
            
            tables_description.append(f"Table: {table_name}")
            tables_description.append(f"Total Records: {total_records}")
            tables_description.append(f"Columns: {', '.join(columns)}")
            if sample:
                tables_description.append("Sample Data:")
                for col, val in sample.items():
                    tables_description.append(f"  {col}: {val}")
            tables_description.append("---")
            
        return "\n".join(tables_description)

    def convert_to_sql(self, natural_query: str) -> str:
        if not self.db_structure:
            raise ValueError("Database structure not set. Call set_database_structure first.")

        prompt = f"""
        You are a SQL expert. Convert the following natural language query to a valid MySQL query.
        
        Database Structure:
        {self._format_table_info()}
        
        Natural Language Query: {natural_query}
        
        Requirements:
        1. Return ONLY the SQL query without any markdown formatting or explanations
        2. Use ONLY the tables and columns that exist in the database structure above
        3. Make sure the query is valid MySQL syntax
        4. Include appropriate JOINs if needed
        5. Use proper column names as shown in the database structure
        6. Consider the sample data to understand the data types and relationships
        7. If aggregating data, use appropriate GROUP BY clauses
        8. If filtering, use appropriate WHERE clauses
        9. Keep the query simple and avoid complex subqueries
        10. Use COUNT(*) for counting records
        11. Use appropriate aggregate functions (SUM, AVG, etc.) when needed
        12. For counting records, use: SELECT COUNT(*) FROM table_name
        13. For grouping, use: SELECT column, COUNT(*) FROM table_name GROUP BY column
        14. For filtering, use: SELECT column FROM table_name WHERE condition
        
        Example response format:
        SELECT column1, column2 FROM table_name WHERE condition;
        """
        
        response = self.model.generate_content(prompt)
        sql_query = self._clean_sql_query(response.text)
        return sql_query

    def format_visualization(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.db_structure:
            raise ValueError("Database structure not set. Call set_database_structure first.")

        # Analyze the data to create meaningful distributions
        results = data.get("results", [])
        if not results:
            return {
                "success": True,
                "message": "No data found",
                "metadata": {
                    "total_records": 0,
                    "charts": {
                        "distribution_1": {
                            "title": "No Data Available",
                            "type": "bar",
                            "values": [],
                            "labels": [],
                        },
                        "distribution_2": {
                            "title": "No Data Available",
                            "type": "pie",
                            "values": [],
                            "labels": [],
                        },
                        "distribution_3": {
                            "title": "No Data Available",
                            "type": "line chart",
                            "values": [],
                            "labels": [],
                            
                        }
                    }
                }
            }

        # Get all possible column names from the first result
        columns = list(results[0].keys()) if results else []
        
        # Create distributions based on available columns
        distributions = {}
        
        # First distribution: Main category (e.g., class, department)
        category_cols = [col for col in columns if any(x in col.lower() for x in ['class', 'department', 'category', 'type'])]
        if category_cols:
            col = category_cols[0]
            values = {}
            for row in results:
                val = str(row.get(col, 'Unknown'))
                if val and val != 'None':
                    values[val] = values.get(val, 0) + 1
            if values:
                distributions['distribution_1'] = {
                    "title": f"Distribution by {col.title()}",
                    "type": "bar",
                    "labels": list(values.values()),
                    "values": list(values.keys())
                }
        
        # Second distribution: Demographic (e.g., gender, age)
        demo_cols = [col for col in columns if any(x in col.lower() for x in ['gender', 'age', 'status'])]
        if demo_cols:
            col = demo_cols[0]
            values = {}
            for row in results:
                val = str(row.get(col, 'Unknown'))
                if val and val != 'None':
                    values[val] = values.get(val, 0) + 1
            if values:
                distributions['distribution_2'] = {
                    "title": f"Distribution by {col.title()}",
                    "type": "pie",
                    "labels": list(values.values()),
                    "values": list(values.keys())
                }
        
        # Third distribution: Location (e.g., village, taluka, city)
        location_cols = [col for col in columns if any(x in col.lower() for x in ['village', 'taluka', 'city', 'location'])]
        if location_cols:
            col = location_cols[0]
            values = {}
            for row in results:
                val = str(row.get(col, 'Unknown'))
                if val and val != 'None':
                    values[val] = values.get(val, 0) + 1
            if values:
                distributions['distribution_3'] = {
                    "title": f"Distribution by {col.title()}",
                    "type": "line chart",
                   "labels": list(values.values()),
                    "values": list(values.keys())
                }
        
        # If we don't have enough columns for all distributions, use remaining columns
        remaining_cols = [col for col in columns if col not in category_cols + demo_cols + location_cols]
        for i in range(1, 4):
            if f'distribution_{i}' not in distributions and remaining_cols:
                col = remaining_cols.pop(0)
                values = {}
                for row in results:
                    val = str(row.get(col, 'Unknown'))
                    if val and val != 'None':
                        values[val] = values.get(val, 0) + 1
                if values:
                    distributions[f'distribution_{i}'] = {
                        "title": f"Distribution by {col.title()}",
                        "type": "bar" if i != 2 else "pie",
                        "labels": list(values.keys()),
                        "values": list(values.values())
                    }

        # Ensure we have all three distributions with meaningful data
        for i in range(1, 4):
            if f'distribution_{i}' not in distributions:
                # Try to find any column with meaningful data
                for col in columns:
                    values = {}
                    for row in results:
                        val = str(row.get(col, 'Unknown'))
                        if val and val != 'None':
                            values[val] = values.get(val, 0) + 1
                    if len(values) > 1:  # Only use if we have at least 2 different values
                        distributions[f'distribution_{i}'] = {
                            "title": f"Distribution by {col.title()}",
                            "type": "bar" if i != 2 else "pie",
                            "labels": list(values.keys()),
                            "values": list(values.values())
                        }
                        break
                else:
                    # If no meaningful data found, use a default distribution
                    distributions[f'distribution_{i}'] = {
                        "title": "No Data Available",
                        "type": "bar" if i != 2 else "pie",
                        "labels": ["No Data"],
                        "values": [0]
                    }

        return {
            "success": True,
            "message": f"Fetched {len(results)} records from database",
            "metadata": {
                "total_records": len(results),
                "charts": distributions
            }
        } 