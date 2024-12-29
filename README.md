# Team 13 - Metaflix
### Team members: 
**Aimee Chen, Zhizhi Wang, Samy Dushimimana Shyaka, Jason Evans**
## Target Company: Netflix 
 
The application demo is built with **Streamlit**. The application includes features such as user authentication, homepage, a friend system, and watch-together sessions. It uses **MongoDB Atlas** for storing movie data, friend data, and watch history, and supports additional integration with **AWS RDS** for relational data like user data, etc., and live comments data is stored in **HBase** due to the huge data amount.

## Features
- **User Authentication**: Secure login and logout functionality.
- **Homepage**: Featured movie recommendations, trending content, and movie details.
- **Friend System**: Add and manage friends.
- **Watch Together**: Watch shows with friends and chat.
- **Account Management**: Update account settings and view user details.

## Easy Access to Demo
- **[Demo App (Click to access)](https://metaflix.streamlit.app/)**

## Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: 
  - MongoDB for movie data, friend data, and watch history data
  - AWS RDS for relational data
  - HBase for live comments data (Due to the EMR cluster setup, the HBase part is not included in the demo app)

- **Python Libraries**:
  - See details in requirements.txt
- **Deployment**: Streamlit Cloud

## Installation
### Prerequisites
#### 1. Python 3.7+
#### 2. MongoDB database (Atlas or local setup)
#### 3. AWS RDS for additional data storage
#### 4. HBase on an EMR cluster
#### 5. S3 bucket for storing data files (`chat_data.csv`)
#### 6. Python 3.7+ installed on the EMR cluster
#### 7. AWS CLI installed on the EMR cluster
#### 8. MySQL Workbench for RDS setup
#### 9. Jupyter notebook for MongoDB setup
#### 10. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Steps

### A. **Setup RDS**:
#### 1. Connect to your RDS instance in MySQL Workbench
#### 2. Download `CreateNetflixDB.sql` and data files (`Netflix Userbase.csv`,`All_Profiles.csv`, `All_Devices.csv`, `All_SearchHistory.csv`, `All_ViewingActivity.csv`, `chat_data.csv`)
#### 3. Change data file paths in SQL script
#### 4. Run `CreateNetflixDB.sql` script to create the database and populate tables
---
### B. **Setup MongoDB**:
#### 1. Create a MongoDB Atlas account and set up a cluster
#### 2. Download `nosql.ipynb` and data files (`netflix_titles.csv`, `Clickstream_Data_with_User_IDs.csv`, `Friends_Data_MongoDB.json`)
#### 3. Change data file paths in the Jupyter notebook
#### 4. Change the MongoDB connection string in the Jupyter notebook
#### 5. Run the Jupyter notebook to populate the MongoDB database
---
### C. **Setup HBase**:
### Steps to Set Up and Load Data

#### 1. Create the HBase Table
Run the following HBase shell commands to create the table:

```shell
create 'chat_data', 'message_details', 'user_details', 'show_details'
```

#### 2. Verify Table Structure
Ensure the table structure is correct by running:

```shell
describe 'chat_data'
```

#### 3. Download CSV Data
Download the `chat_data.csv` file from the S3 bucket (replace `netflixx` with your bucket name):

```shell
sudo aws s3 cp s3://netflixx/data/chat_data.csv /user/hadoop/chat_data.csv
```

#### 4. Install Python Development Tools
Install the necessary Python development tools on your system:

```shell
sudo yum install python3-devel
```

#### 5. Install Required Python Libraries
Install the Python libraries required for connecting to HBase:

```shell
pip install thriftpy2 happybase
```

#### 6. Run Python Script to Load Data
Create a Python script named `load_hbase.py` with the following content:

```python
import csv
import happybase

# Connect to HBase
connection = happybase.Connection('localhost')
table = connection.table('chat_data')

# Read CSV and insert data into HBase
with open('/user/hadoop/chat_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unique_id = row['unique_id']
        data = {
            'show_details:show_id': row['show_id'],
            'user_details:User_ID': row['User ID'],
            'user_details:all_authors': row['all_authors'],
            'message_details:messages': row['messages'],
            'message_details:timestamps': row['timestamps'],
            'message_details:time': row['time'],
        }
        table.put(unique_id, data)

print("Data successfully loaded into HBase!")
```

Run the script to load the data:

```shell
python3 load_hbase.py
```
---
### D. **Setup Data Warehouse**:
#### 1. Download file `star_schema.sql`
#### 2. Run the SQL script in MySQL workbench in the corresponding database to create the star schema
---
### E. **Setup the Streamlit app**:
#### 1. Download all files from the `demo` folder
#### 2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
#### 3. Set up your MongoDB or RDS credentials in `secrets.toml`:
   ```toml
   [mongodb]
   connection_string = "your_mongodb_connection_string"
   database_name = "StreamingPlatform"

   [rds]
   db_host = "your-rds-endpoint.amazonaws.com"
   db_user = "your_username"
   db_password = "your_password"
   db_name = "Netflix"
   ```

#### 4. Run the app:
   ```bash
   streamlit run __init__.py
   ```

## Streamlit App File Structure
```
demo/
│
├── __init__.py           # Main entry point of the app
├── .streamlit/           # Streamlit configuration folder
│   └── secrets.toml      # Credentials for MongoDB and RDS 
├── login_config.py       # Login configuration
├── home.py               # Logic for the Homepage
├── friends.py            # Logic for the Friends system
├── watch_together.py     # Logic for the Watch Together feature
├── accounts.py            # Logic for the Account Management
├── requirements.txt      # Dependencies
└── moviecover.jpg        # Sample movie cover image
```

## Streamlit App Deployment
1. Push the code to your Git repository.
2. Set up your app on **Streamlit Cloud**.
3. Add secrets (`secrets.toml`) in Streamlit's **Secrets Manager** under the "Advanced settings" section.