#database_manager.py
import mysql.connector
from configparser import ConfigParser
from datetime import datetime
import logging
from include.operations.logger_file import setup_logging
from .encryption import decrypt_password,load_key

setup_logging()
logger = logging.getLogger(__name__)
key = load_key()

from configparser import ConfigParser
import mysql.connector

def databaseConnect(file_path):
    config = ConfigParser()
    config.read(file_path)

    password = config['Database']['password']
    host = config['Database']['host']  # Removed the comma
    user = config['Database']['username']  # Removed the comma
    database = config['Database']['databasename']  # Ensure this matches the INI file key
    try:
        sender_password = decrypt_password(password, key)
    except Exception as e:
        logger.error(f"Failed to decrypt password: {e}")
        return

    try:
        # Use keyword arguments for connection
        db = mysql.connector.connect(host=host, user=user, password=sender_password, database=database)
        logger.info("Connection successful!")
        return db

    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        return None
    except KeyError as e:
        logger.error(f"Missing configuration parameter: {e}")
        return None

def create_Table(db_connection, sql_file):
    if db_connection is None:
        logger.error("No connection to execute SQL file.")
        return

    try:
        cursor = db_connection.cursor()

        # Read the SQL file
        with open(sql_file, 'r') as file:
            sql_script = file.read()

        # Execute each SQL statement
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    logger.info(f"{err}")
        
        db_connection.commit()
        cursor.close()

    except mysql.connector.Error as err:
        logger.error(f"Error executing SQL file: {err}")


def get_table_columns(cursor, table_name):
    """Retrieve column names for a given table."""
    query = f"SHOW COLUMNS FROM `{table_name}`"
    cursor.execute(query)
    columns = [row[0] for row in cursor.fetchall()]
    return columns


def insert_data(df, table_name, db_connection, date_str):
    if db_connection is None:
        logger.error("No connection to insert data.")
        return
    
    inserted_rows = 0
    updated_rows = 0
    skipped_rows = 0

    try:
        cursor = db_connection.cursor()

        # Convert 'date_str' to an integer in the format YYYYMMDD and add it as 'dt'
        dt_value = int(datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d'))
        df['dt'] = dt_value

        # Get all columns from the database table
        columns = get_table_columns(cursor, table_name)

        # Filter out columns with default values that are not in the DataFrame
        df_columns = df.columns.tolist()
        columns_to_insert = [col for col in columns if col in df_columns or col == 'dt']

        # Construct the SQL query for insertion with ON DUPLICATE KEY UPDATE
        columns_list = ', '.join([f"`{col}`" for col in columns_to_insert])
        placeholders = ', '.join(['%s'] * len(columns_to_insert))
        
        # Create the update clause for the ON DUPLICATE KEY UPDATE statement
        update_clause = ', '.join(
            [f"`{col}` = VALUES(`{col}`)" for col in columns_to_insert if col != 'dt']
        )

        # Explicitly set the update_source and update_time to new values on update
        update_clause += ", `update_source` = 'jpxwebetfpcfinfo', `update_time` = CURRENT_TIMESTAMP"

        sql = f"""
        INSERT INTO `{table_name}` ({columns_list}) 
        VALUES ({placeholders}) 
        ON DUPLICATE KEY UPDATE {update_clause}
        """

        # Prepare data for insertion
        data = df[columns_to_insert].fillna('').values.tolist()  # Convert NaN to None

        # Execute each row individually to track inserts and updates
        for row in data:
            try:
                cursor.execute(sql, row)
                if cursor.rowcount == 1:
                    inserted_rows += 1
                elif cursor.rowcount == 2:
                    updated_rows += 1
            except mysql.connector.Error as err:
                print(f"Skipping row due to error: {err}")
                skipped_rows += 1
                continue

        db_connection.commit()

        logger.info(f"Data inserted or updated in table '{table_name}' successfully!")
        logger.info(f"Number of rows inserted: {inserted_rows}")
        logger.info(f"Number of rows updated: {updated_rows}")
        logger.info(f"Number of rows skipped: {skipped_rows}")

    except mysql.connector.Error as err:
        logger.error(f"Error inserting or updating data in table '{table_name}': {err}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        cursor.close()