# Installing Dependancy
Paste this into your terminal: pip install -r requirement.txt

# Setting Up Database
Insert your mysql database credential to the enviorment in terminal/ di .env:
-"DB_HOST"
-"DB_USER"
-"DB_PASSWORD"
-"DB_NAME"

Windows:
setx DB_HOST "your host here"
setx DB_USER "your user here"
setx DB_PASSWORD "your password here"
setx DB_NAME "your database name here"

Linux/Mac:
export DB_HOST="your host here"
export DB_USER="your user here"
export DB_PASSWORD="your password here"
export DB_NAME="your database name here"

Example of the database can be accesed trough "skillhub_db.sql"

# Run Application
Paste this into your terminal: streamlit run app.py

# Testing
Paste this into your terminal: pytest tests/