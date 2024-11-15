# TSE-PCF Data Downloader  

This project automates the process of downloading and inserting Portfolio Composition File (PCF) data from the JPX website into a database. The script runs daily at 4:00 PM from Monday to Friday and sends an email notification upon task completion.  

## Features  
- Automated data download and insertion into the database.  
- Configurable email, database, log, and data storage settings.  
- Scheduled execution using `crontab`.  
- Detailed logs for task monitoring and troubleshooting.  

---

## Requirements  
### Operating System  
- Linux or Windows  

### Python  
- Version: **3.8 or higher**  
- Libraries:  
  - `requests`  
  - `mysql-connector-python`  
  - `sqlalchemy`  
  - `python-dotenv`  

### Additional Tools  
- `cron` for scheduling (Linux)  

---

## Setup Instructions  

### Step 1: Clone the Repository  
Clone the repository containing the necessary files and scripts.  
```bash  
git clone https://github.com/Veeresh1221/TSE-PCF_Data_Downloader.git  
cd TSE-PCF_Data_Downloader  
```  

### Step 2: Configure Settings  
Edit the necessary configuration files to set up email, database, logging, and data storage. These are typically located in `config.ini` or in the `src` folder.  

#### Email Configuration  
- Set up email credentials for notifications.  

#### Database Configuration  
- Update the database connection details:  
  - Username  
  - Password  
  - Database name  

#### Log Folder  
- Specify the directory path to store execution logs.  

#### Data Storage Folder  
- Define the directory path for downloaded data.  

---

### Step 3: Write the Bash Script  
Create a bash script to execute the Python script.  

1. Create a file named `auto_download.sh`:  
   ```bash  
   nano auto_download.sh  
   ```  
2. Add the following content:  
   ```bash  
   #!/bin/bash  
   cd <path_to_download_script>  
   python3 main.py  
   ```  

3. Make the script executable:  
   ```bash  
   chmod +x auto_download.sh  
   ```  

---

### Step 4: Schedule the Script with Crontab  
Use `cron` to schedule the script for automatic execution.  

1. Open the crontab editor:  
   ```bash  
   crontab -e  
   ```  

2. Add the following line to schedule the script to run at 4:00 PM (16:00) every weekday (Monday to Friday):  
   ```bash  
   0 16 * * 1-5 /path/to/auto_download.sh  
   ```  

---

### Step 5: Install Required Dependencies  
Install the necessary Python libraries using `pip`.  
```bash  
pip install -r requirements.txt  
```  

---

## File Structure  

```  
TSE-PCF_Data_Downloader/  
├── src/  
│   ├── main.py  
│   ├── config.ini  
│   └── ...  
├── auto_download.sh  
├── logs/  
├── data/  
├── requirements.txt  
└── README.md  
```  

---

## Running the Script Manually  
To execute the script manually, run:  
```bash  
./auto_download.sh  
```  

---

## Contact  
For further assistance, please contact the repository owner at [veereshvkanakalamath2@gmail.com](mailto:veereshvkanakalamath2@gmail.com).  

--- 

### `requirements.txt` File  

```plaintext  
requests==2.28.1  
mysql-connector-python==8.0.30  
sqlalchemy==2.0.1  
python-dotenv==0.21.0  
```  
