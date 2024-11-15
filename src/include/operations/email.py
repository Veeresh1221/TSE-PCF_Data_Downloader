from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import os
import configparser
import logging
from include.operations.logger_file import setup_logging
from .encryption import decrypt_password,load_key

setup_logging()
logger = logging.getLogger(__name__)

# Load or generate encryption key
key = load_key()
def send_email(subject, body, ini_file_path):
    # Read the email configuration from the ini file
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    
    # Email details
    sender_email = config['Email']['sender_email']
    encrypted_password = config['Email']['sender_password']
    smtp_server = config['Email']['smtp_server']
    smtp_port = config['Email'].getint('smtp_port')
    recipients = config['Recipients']['recipients'].split(',')

    # Decrypt the password
    try:
        sender_password = decrypt_password(encrypted_password, key)
    except Exception as e:
        logger.error(f"Failed to decrypt password: {e}")
        return

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach the log file if available
   

    try:
        # Try to establish the connection and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
    

