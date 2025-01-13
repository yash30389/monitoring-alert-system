import boto3  # For AWS SNS
from botocore.exceptions import BotoCoreError, ClientError
import pymysql
import psycopg2
import pyodbc
import requests
import time
import json
from config import COMPANY_NAME, RDS_HOSTNAME, RDS_PORT, RDS_DATABASE, RDS_USERNAME, RDS_PASSWORD, RDS_DATABASE_ENGINE_TYPE, endpoints, WEBHOOK_URLS, SNS_TOPIC_ARN
from datetime import datetime

current_month = datetime.now().strftime('%B')
current_year = datetime.now().year

def publish_to_sns(message, subject=None):
    """
    Publish a message to an SNS topic.
    """
    sns_client = boto3.client("sns")
    if subject is None:
        subject = f"{COMPANY_NAME}_Alert Notification"
    
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )
        print(f"SNS alert sent: {response['MessageId']}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error sending SNS alert: {e}")

def send_to_webhooks(message):
    """
    Send a POST request with the alert message to all configured webhook URLs.
    """
    for webhook_url in WEBHOOK_URLS:
        try:
            response = requests.post(
                webhook_url,
                json={"content": message},  # Discord requires 'content' field
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"Webhook alert sent to {webhook_url}")
            else:
                print(f"Error sending webhook alert to {webhook_url}: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error sending webhook alert to {webhook_url}: {e}")

# Configuration dictionary for database engines
DATABASE_ENGINES = {
    "mysql": {
        "module": pymysql,
        "connection_args": lambda cfg: {
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["username"],
            "password": cfg["password"],
            "database": cfg["database"],
        },
        "create_table_queries": {
            "current_month": f"""
                CREATE TABLE IF NOT EXISTS `{current_month}_{current_year}` (
                    endpointurl VARCHAR(255),
                    statuscode INT,
                    notification VARCHAR(50),
                    response_time VARCHAR(50),
                    max_response_time INT,
                    acceptable_status_codes JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "alerts_table_query": f"""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpointurl VARCHAR(255) NOT NULL,
                    issue_type VARCHAR(50) NOT NULL,
                    alert_message TEXT NOT NULL
                );
            """
        },
        "insert_query_health": f"""
            INSERT INTO `{current_month}_{current_year}` (endpointurl, statuscode, notification, response_time, max_response_time, acceptable_status_codes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
        "insert_query_alerts": """
            INSERT INTO alerts (endpointurl, issue_type, alert_message)
            VALUES (%s, %s, %s)
        """,
        "select_unhealthy_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Unhealthy' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
        "select_slow_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Slow' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
    },
    "postgresql": {
        "module": psycopg2,
        "connection_args": lambda cfg: {
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["username"],
            "password": cfg["password"],
            "database": cfg["database"],
        },
        "create_table_queries": {
            "current_month": f"""
                CREATE TABLE IF NOT EXISTS `{current_month}_{current_year}` (
                    endpointurl VARCHAR(255),
                    statuscode INT,
                    notification VARCHAR(50),
                    response_time VARCHAR(50),
                    max_response_time INT,
                    acceptable_status_codes JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "alerts_table_query": f"""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpointurl VARCHAR(255) NOT NULL,
                    issue_type VARCHAR(50) NOT NULL,
                    alert_message TEXT NOT NULL
                );
            """
        },
        "insert_query_health": f"""
            INSERT INTO `{current_month}_{current_year}` (endpointurl, statuscode, notification, response_time, max_response_time, acceptable_status_codes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
        "insert_query_alerts": """
            INSERT INTO alerts (endpointurl, issue_type, alert_message)
            VALUES (%s, %s, %s)
        """,
        "select_unhealthy_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Unhealthy' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
        "select_slow_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Slow' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
    },
    "mssql": {
        "module": pyodbc,
        "connection_args": lambda cfg: {
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["username"],
            "password": cfg["password"],
            "database": cfg["database"],
        },
        "create_table_queries": {
            "current_month": f"""
                CREATE TABLE IF NOT EXISTS `{current_month}_{current_year}` (
                    endpointurl VARCHAR(255),
                    statuscode INT,
                    notification VARCHAR(50),
                    response_time VARCHAR(50),
                    max_response_time INT,
                    acceptable_status_codes JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "alerts_table_query": f"""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpointurl VARCHAR(255) NOT NULL,
                    issue_type VARCHAR(50) NOT NULL,
                    alert_message TEXT NOT NULL
                );
            """
        },
        "insert_query_health": f"""
            INSERT INTO `{current_month}_{current_year}` (endpointurl, statuscode, notification, response_time, max_response_time, acceptable_status_codes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
        "insert_query_alerts": """
            INSERT INTO alerts (endpointurl, issue_type, alert_message)
            VALUES (%s, %s, %s)
        """,
        "select_unhealthy_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Unhealthy' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
        "select_slow_count": f"""
            SELECT COUNT(*) FROM `{current_month}_{current_year}`
            WHERE endpointurl = %s AND notification = 'Slow' AND created_at > NOW() - INTERVAL 15 MINUTE
        """,
    }
}


def connect_to_database(engine, config):
    """
    Connect to the database dynamically based on the engine provided.
    """
    if engine not in DATABASE_ENGINES:
        raise ValueError(f"Unsupported database engine: {engine}")
    
    engine_config = DATABASE_ENGINES[engine]
    module = engine_config["module"]
    connection_args = engine_config["connection_args"](config)
    
    # Establish connection
    connection = module.connect(**connection_args)
    print(f"Connected to {engine} database!")
    return connection, engine_config

def create_tables_if_not_exists(connection, engine_config):
    """
    Create tables if they don't exist.
    """
    # Get current month and year
    current_month = time.strftime('%B')
    current_year = time.strftime('%Y')
    
    try:
        cursor = connection.cursor()
        # Create current month-year table if it doesn't exist
        cursor.execute(engine_config["create_table_queries"]["current_month"].format(month=current_month, year=current_year))
        # Create the alerts table if it doesn't exist
        cursor.execute(engine_config["create_table_queries"]["alerts_table_query"])
        connection.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()

def insert_health_data(connection, engine_config, data):
    """
    Insert health check data into the database.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(engine_config["insert_query_health"], data)
        connection.commit()
    except Exception as e:
        print(f"Error inserting health data: {e}")
    finally:
        cursor.close()

def send_alert(connection, engine_config, url, issue_type, alert_message):
    """
    Log an alert into the alerts table and send notifications via SNS and webhooks.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(engine_config["insert_query_alerts"], (url, issue_type, alert_message))
        connection.commit()
        print(f"Alert generated: {alert_message}")
        # Send notifications
        publish_to_sns(alert_message)
        send_to_webhooks(alert_message)
    except Exception as e:
        print(f"Error logging alert: {e}")
    finally:
        cursor.close()

def check_and_alert(connection, engine_config, url, notification, response_time=None, max_response_time=None):
    """
    Check if an alert needs to be sent for repeated issues.
    """
    cursor = connection.cursor()
    try:
        if notification == "Unhealthy":
            cursor.execute(engine_config["select_unhealthy_count"], (url,))
        elif notification == "Slow":
            cursor.execute(engine_config["select_slow_count"], (url,))
        
        count = cursor.fetchone()[0]
        if count >= 3:  # Trigger alert if the issue occurs 3 times in a short period
            if notification == "Unhealthy":
                issue_type = "Unhealthy"
                alert_message = f"The URL {url} has been marked as Unhealthy 3 times consecutively."
            elif notification == "Slow":
                issue_type = "Slow Response"
                alert_message = (
                    f"The URL {url} has been slow 3 times consecutively.\n"
                    f"Recent Response Time: {response_time}, Max Allowed: {max_response_time}"
                )
            send_alert(connection, engine_config, url, issue_type, alert_message)
    except Exception as e:
        print(f"Error checking for alert: {e}")
    finally:
        cursor.close()

def lambda_handler(event, context):
    db_engine = RDS_DATABASE_ENGINE_TYPE
    config = {
        "host": RDS_HOSTNAME,
        "port": RDS_PORT,
        "database": RDS_DATABASE,
        "username": RDS_USERNAME,
        "password": RDS_PASSWORD,
    }

    try:
        connection, engine_config = connect_to_database(db_engine, config)

        # Create the tables if they don't exist
        create_tables_if_not_exists(connection, engine_config)

        with connection.cursor() as cursor:
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(endpoint["url"])
                    response_time = time.time() - start_time
                    formatted_response_time = f"{response_time:.3f}s"
                    status_code = response.status_code
                    acceptable_status_codes = endpoint["acceptable_status_codes"]
                    max_response_time = endpoint["max_response_time"]

                    if status_code not in acceptable_status_codes:
                        notification = "Unhealthy"
                    elif response_time > max_response_time:
                        notification = "Slow"
                    else:
                        notification = "Healthy"

                    data = (
                        endpoint["url"],
                        status_code,
                        notification,
                        formatted_response_time,
                        max_response_time,
                        json.dumps(acceptable_status_codes)
                    )

                    insert_health_data(
                        connection,
                        engine_config,
                        data
                    )

                    check_and_alert(
                        connection,
                        engine_config,
                        endpoint["url"],
                        notification,
                        formatted_response_time,
                        max_response_time
                    )

                except Exception as e:
                    print(f"Error processing endpoint {endpoint['url']}: {e}")
    except Exception as e:
        print(f"Error in lambda_handler operation: {e}")