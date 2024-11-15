from include.operations.downloader import download_file
from include.operations.extractor import unzip_all_files_in_directory
from include.operations.categorizer import categorize
from include.operations.database import create_Table,insert_data,databaseConnect
import os
import logging
from include.operations.logger_file import setup_logging

setup_logging
logger = logging.getLogger(__name__)

def download_and_extract(urls,date_str, base_directory):
    logger.info("Downloading and Extracting")
    zip_directory = os.path.join(base_directory, 'raw', date_str)
    output_directory = os.path.join(base_directory, 'extracted', date_str)
    os.makedirs(zip_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    for url, index in urls:
        download_file(url, zip_directory, index, date_str)
    unzip_all_files_in_directory(zip_directory, output_directory)


def catagarize_and_insert(date_str,ini_file_path,sql_file ,table_names,output_directory):
    logger.info("Connecting To Database Started")
    db_connection = databaseConnect(ini_file_path)
    if db_connection is None:
        logger.info("Database connection failed. Exiting.")
        return

    # Execute SQL file to create tables
    logger.info("Creating Tables Started")
    create_Table(db_connection, sql_file)
        
    # Process and categorize data
    logger.info(f"Categorizing Started for {date_str}")
    summary_df, detail_df = categorize(output_directory)

    if summary_df.empty:
        logger.info(f"No data to insert into table '{table_names[0]}'")
    else:
        logger.info(f"Inserting Into Table '{table_names[0]}' for date {date_str}")
        insert_data(summary_df, table_names[0], db_connection, date_str)
        
    if detail_df.empty:
        logger.info(f"No data to insert into table '{table_names[1]}'")
    else:
        logger.info(f"Inserting Into Table '{table_names[1]}' for date {date_str}")
        insert_data(detail_df, table_names[1], db_connection, date_str)


