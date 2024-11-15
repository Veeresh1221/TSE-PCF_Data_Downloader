#file_processor.py
import zipfile
import os
import traceback
import logging
from include.operations.logger_file import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def unzip_file(zip_file_path, extract_to_folder):
    try:
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_folder)
            logger.info(f"Extracted '{zip_file_path}' to '{extract_to_folder}'")
    except zipfile.BadZipFile:
        logger.error(f"Error: '{zip_file_path}' is not a valid zip file.")
    except FileNotFoundError:
        logger.error(f"Error: File '{zip_file_path}' not found.")
    except PermissionError:
        logger.error(f"Error: Permission denied when accessing '{zip_file_path}' or '{extract_to_folder}'.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while extracting '{zip_file_path}': {e}")
        traceback.print_exc()

def unzip_all_files_in_directory(zip_directory, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
    
    # Loop through all files in the zip directory
    for file_name in os.listdir(zip_directory):
        if file_name.endswith('.zip'):
            zip_file_path = os.path.join(zip_directory, file_name)
            try:
                unzip_file(zip_file_path, output_directory)
            except Exception as e:
                logger.error(f"Failed to unzip '{zip_file_path}': {e}")
                traceback.print_exc()
