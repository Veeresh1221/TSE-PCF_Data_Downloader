from cryptography.fernet import Fernet
import configparser
import os

def generate_key():
    """Generate a new key and return it."""
    return Fernet.generate_key()

def encrypt_password(password, key):
    """Encrypt the password using the provided key."""
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, key):
    """Decrypt the password using the provided key."""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

KEY_FILE_PATH = 'key.key'

def load_key():
    """Load the key from a file, generate and save it if not present."""
    if not os.path.exists(KEY_FILE_PATH):
        key = generate_key()
        with open(KEY_FILE_PATH, 'wb') as key_file:
            key_file.write(key)
        os.chmod(KEY_FILE_PATH, 0o600)
    with open(KEY_FILE_PATH, 'rb') as key_file:
        return key_file.read()

def is_encrypted(value):
    """Check if the given value is already encrypted."""
    return value.startswith('gAAAA')

def save_encrypted_password_to_ini(ini_file_path, section, key, password):
    """Encrypt the password and save it to the specified section and key in the ini file."""
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    # Check if the section exists and the key already has a value
    if config.has_section(section) and config.has_option(section, key):
        current_value = config.get(section, key)
        if is_encrypted(current_value):
            print("Password is already encrypted, no further encryption needed.")
            return  # Exit the function without re-encrypting

    # Encrypt the password if it’s not already encrypted
    encrypted_password = encrypt_password(password, load_key())

    if not config.has_section(section):
        config.add_section(section)  # Add section if it doesn't exist
    
    config.set(section, key, encrypted_password)
    
    with open(ini_file_path, 'w') as configfile:
        config.write(configfile)
