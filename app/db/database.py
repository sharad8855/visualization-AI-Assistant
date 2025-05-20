import mysql.connector
from mysql.connector import Error
from .models import DatabaseConfig

def get_database_connection(config: DatabaseConfig):
    try:
        connection = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=config.database
        )
        return connection
    except Error as e:
        raise Exception(f"Error connecting to MySQL database: {str(e)}")

def save_database_config(config: DatabaseConfig):
    try:
        connection = get_database_connection(config)
        cursor = connection.cursor()
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            host VARCHAR(255) NOT NULL,
            user VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            database_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        
        # Insert the configuration
        insert_query = """
        INSERT INTO data (host, user, password, database_name)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            config.host,
            config.user,
            config.password,
            config.database
        ))
        
        connection.commit()
        return True
    except Error as e:
        raise Exception(f"Error saving database configuration: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close() 