#file_downloader.py
import os
import requests
import configparser
from datetime import datetime
import logging
from include.operations.logger_file import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
# Function to format date as ddmmyyyy
def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d%m%Y')
        except ValueError:
            logger.error(f"Error: Invalid date format '{date_str}'. Expected format: YYYY-MM-DD.")
            raise

    # Function to create a new filename based on a fixed pattern
def create_filename(index, date_str):
        formatted_date = format_date(date_str)
        return f"link{index}-{formatted_date}.zip"

 # Function to download and save files
def download_file(url, save_dir, index, date_str):
    local_filename = create_filename(index, date_str)
    file_path = os.path.join(save_dir, local_filename)
    
    # Proceed with downloading the file if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Headers to mimic a browser request (optional)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        # Add other headers if required by the server
    }
    
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            
            # Check if the response is HTML (content-type or response body check)
            if "text/html" in r.headers.get('Content-Type', '') or b"<html>" in r.content[:100].lower():
                logger.error(f"Received HTML content instead of a file. Skipping file: {local_filename}")
                logger.debug(f"Response content: {r.text}")  # Log or print the response for analysis
                return
            
            # Save the file if it's not an HTML page
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info(f"Downloaded: {local_filename}")
    
    except requests.RequestException as e:
        logger.error(f"Failed to download: {e}")
    except OSError as e:
        logger.error(f"Failed to save the file {file_path}: {e}")

        
    # Read URLs and date from INI file
def read_urls_and_date_from_ini(file_path):
        config = configparser.ConfigParser()
        try:
            config.read(file_path)
        except configparser.Error as e:
            logger.error(f"Error reading INI file '{file_path}': {e}")
            raise

        try:
            date = config.get('Date', 'date')
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
                logger.warn(f"Section 'Date' found empty in the INI file. Using System's Date {date}")
        except configparser.NoSectionError:
            logger.error("Error: No section 'Date' found in the INI file.")
            raise
        except configparser.NoOptionError:
            logger.error("Error: No 'date' option found in the 'Date' section of the INI file.")
            raise

        urls = []

        if 'Download' in config:
            for index, key in enumerate(config['Download'], start=1):
                url = config['Download'][key]
                url = url.replace('YYYYMMDD', date.replace('-', ''))
                url = url.replace('YYYY-MM-DD', date)
                urls.append((url, index))
        else:
            logger.error("Error: No 'download' section found in the INI file.")
            raise configparser.NoSectionError('download')

        return urls, date

    

