import include.servies as service
import include.operations.downloader as file_downloader
import os
from include.operations.email import send_email
from include.operations.logger_file import get_log_output
import configparser
import include.operations.encryption as encryption
from time import gmtime, strftime
import include.operations.database as database
from include.operations.logger_file import setup_logging,logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    ini_file_path = 'config.ini'
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    log_file_dir = config['Folders']['Log']
    base_directory = config['Folders']['Data']
    sql_file = os.path.join(os.path.dirname(__file__), '..', 'sql', 'create_table_schema.sql')
    table_names = ['tsepcfsummary', 'tsepcfdetail']

    # Encrypt sensitive data in the ini file
    encryption.save_encrypted_password_to_ini(ini_file_path, 'Email', 'sender_password', config['Email']['sender_password'])
    encryption.save_encrypted_password_to_ini(ini_file_path, 'Database', 'password', config['Database']['password'])
    
    # Initialize variables
    script_success = True
    subject = ""
    message = ""

    try:
        # Read URLs and date from the ini file
        urls, date_str = file_downloader.read_urls_and_date_from_ini(ini_file_path)
        service.download_and_extract(urls, date_str, base_directory)
        service.catagarize_and_insert(date_str, ini_file_path, sql_file, table_names, os.path.join(base_directory, 'extracted', date_str))

        # If everything succeeded, set success message
        subject = 'Jpx web pcf download : successful'
        message = f"The data processing and insertion for {date_str} were completed successfully:\nLogs:\n{get_log_output()}"
        
    except Exception as e:
        script_success = False
        subject = 'Jpx web pcf download : Failed'
        logger.error(e)
        message = f"An error occurred:\n{str(e)}\nLogs:\n{get_log_output()}"


    finally:
        # ?send_email(subject, message, ini_file_path)
        # Format the current time and construct the log filename
        now = strftime("%Y-%m-%d_%H-%M-%S", gmtime())  
        log_filename = os.path.join(log_file_dir, f"tsepcf_log_{now}.log")
        
        # Write the log output to the file
        with open(log_filename, "w") as f:
            f.write(get_log_output())
        
if __name__ == "__main__":
    main()
