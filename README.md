# Monitoring and Alert System for Microservice Endpoint/Website's Uptime and Response Time

This project is a lightweight monitoring solution designed to track the uptime and response time of a microservice endpoint or website URL. The system provides alerts for downtime and response time issues, and it is designed to support scalability for additional endpoints in the future while using minimal resources.

---

## Features

### 1. Uptime Monitoring
- Regularly checks if the endpoint/URL is reachable and operational.

### 2. Response Time Measurement
- Records the response time of the endpoint/URL during each check.

### 3. Alerts
- **Downtime Alerts**: Notifies when the endpoint/URL becomes unavailable.
- **Response Time Alerts**: Notifies when response times exceed a defined threshold.

### 4. Scalability
- Supports monitoring multiple endpoints with minimal additional configuration.

---

## Prerequisites
- **Python 3.7+** or another programming environment if using different libraries/tools.
- Installed dependencies (see below).

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yash30389/monitoring-alert-system.git
cd monitoring-alert-system
```

### 2. Set Configuration
Edit the `config.py` file (if applicable) to include:
- **Endpoint URLs**
- **Alert thresholds** (response time, downtime, etc.)
- **Notification settings** (WebhookURL's, AWS SNS topics, etc.)
Create webhooks and an AWS SNS topic in your AWS account or any supported platform for webhooks, such as Slack, Discord, or Microsoft Teams.

---

# Lambda Layer Setup
The Lambda function in this project uses dependencies specified in `requirements.txt` and configurations from `config.py`. To optimize and reuse these across multiple Lambda functions, we create a Lambda Layer.

## Steps to Create a Lambda Layer
***NOTE:*** The directory name must follow this path: `python/lib/python{version}/site-packages`.

(***e.g***. `python/lib/python3.13/site-packages`)

**Create Directory Structure for the Layer:**
```bash
mkdir -p python/lib/python3.13/site-packages
```

**Install Dependencies:**

Install the dependencies specified in `requirements.txt` into the site-packages directory:

```bash
pip install -r requirements.txt --target python/lib/python3.13/site-packages/
```
**Add Config File:** Copy `config.py` into the python directory of the layer:

```bash
cp config.py python/
```
**Package the Layer:** Create a `.zip` file for the Lambda layer:

```bash
cd python
Compress-Archive -Path .\* -DestinationPath ..\python.zip
cd ..
```


## Create the Layer in the AWS Console
1. **Login to AWS Management Console**: Navigate to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/).


2. **Go to the Layers Section:** On the left menu, click **"Layers"**.

3. **Create a New Layer:** Click the ***"Create layer"*** button.

4. Enter a name for the layer (**e.g.**, monitoring-layer).

5. **Upload the ZIP File:**

    Under the **"Upload a `.zip` file"** section, click **"Upload"** and select the `python.zip` file created        earlier.

6. **Choose Compatible Runtimes:**

    Select the Python runtime version(s) compatible with your Lambda function (**e.g.**, Python 3.13).

7. **Create the Layer:**

    Click **"Create"** to upload the layer.


## Permissions for Using AWS SNS in Lambda

If your Lambda function uses the AWS SNS service to publish messages or send emails, you must attach the appropriate permissions to the Lambda function's execution role.

### Required IAM Permissions

Add the following permissions to the execution role associated with your Lambda function:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "<SNS_TOPIC_ARN>"
    }
  ]
}
```

## Attach the Layer to Your Lambda Function
Navigate to your Lambda function in the **AWS Console**.

1. In the **"Configuration"** tab, click **"Layers"** under the **"Function overview"** section.

2. **Click "Add a layer":**
    
    Select **"Custom layers".**

3. Choose the layer which previously created (**e.g.**, monitoring-layer).

4. Select the layer version.

5. Click **"Add"** to attach the layer with Lambda function.

---

# Usage

### Start Monitoring
Run the script to begin monitoring:
```bash
python lambda_function.py
```


## Alerts
Alerts are generated based on the following conditions:
1. **Downtime**: When the endpoint/URL is unreachable.
2. **Response Time**: When the response time exceeds the defined threshold.

Alert notifications will be sent via the configured channels (WebhookURLs, AWS SNS topics, etc.).

---

## Adding New Endpoints
1. Update the `config.py` file to include the new endpoint URL.
2. Restart the monitoring script.

---

## Built With
- **Python**: Core logic implementation.
- **Requests Library**: For making HTTP requests.

---

## Future Improvements
- Add a user-friendly web interface for managing endpoints and thresholds.
- Integrate with third-party monitoring tools (e.g., Prometheus, Grafana).
- Support webhook-based alerts.

