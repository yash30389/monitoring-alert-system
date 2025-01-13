# Hardcoded RDS connection details
RDS_HOSTNAME = ''                      # RDS server host
RDS_PORT = 3306                        # RDS host port
RDS_DATABASE = ''                      # Add databse name
RDS_USERNAME = ''                      # User Name
RDS_PASSWORD = ''                      # User Password
RDS_DATABASE_ENGINE_TYPE = ''          # Add database type [mysql, mssql, psycopg2]
COMPANY_NAME = ''                      # Add company name

# Add SNS topic ARN and webhook URLs to the config
SNS_TOPIC_ARN = ""
WEBHOOK_URLS = [""]

# List of endpoints to check and their configurations
endpoints = [
    {
        "url": "",
        "max_response_time": 0.5,  # in seconds
        "acceptable_status_codes": [200, 201]
    },
    {
        "url": "",
        "max_response_time": 0.5,
        "acceptable_status_codes": [200]
    },
    {
        "url": "",
        "max_response_time": 0.7,
        "acceptable_status_codes": [200]
    }
]