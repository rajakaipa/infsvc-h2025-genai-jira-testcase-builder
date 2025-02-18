## JIRA Testcase Builder
This project is a web application built using Flask that allows users to generate detailed test cases based on functional requirements. The application supports uploading text, DOCX, and PDF files, and it can also fetch issue descriptions from Jira. The generated test cases can be downloaded in Excel format.

## Features
File Upload: Users can upload text, DOCX, or PDF files containing functional requirements.

Jira Integration: Fetch issue descriptions directly from Jira using the issue key.

Test Case Generation: Generate detailed test cases using AWS Bedrock's Claude model.

Excel Download: Download the generated test cases in Excel format.

## Pre-requisites
Before running the application, ensure you have the following:

Python 3.x

AWS account with access to AWS Bedrock

Jira account with API access

Required Python libraries (install via pip install -r requirements.txt)

## Installation
Clone the repository:


git clone https://github.com/yourusername/test-case-generator.git
cd test-case-generator
Set up environment variables:
Create a .env file in the root directory with the following variables:

## Install dependencies:

pip install -r requirements.txt

## Run the application:


flask --app app.py run --debug --host=127.0.0.1 --port=500
The application will be available at http://127.0.0.1:5000/.

## usage
Home Page: Navigate to the home page to upload a file or enter functional requirements manually.

Jira Integration: Enter a Jira issue key to fetch the issue description.

Generate Test Cases: Select the types of test cases you want to generate and submit the form.

Download Excel: After generating test cases, you can download them in Excel format.

## File Structure

app.py: Main Flask application file.

templates/: Contains HTML templates for the web interface.

form.html: Form for uploading files and entering requirements.

results.html: Displays generated test cases.

uploads/: Directory for storing uploaded files and generated Excel files.

.env: Environment variables for AWS and Jira credentials.

requirements.txt: List of Python dependencies.

API Endpoints
GET /: Renders the home page with the form.

POST /generate: Processes the form data, generates test cases, and renders the results.

POST /fetch-jira: Fetches the description of a Jira issue.

## Dependecies
Flask: Web framework.

boto3: AWS SDK for Python.

pandas: Data manipulation library.

python-docx: Library for reading DOCX files.

PyPDF2: Library for reading PDF files.

requests: HTTP library for making requests to Jira API.

## dotenv

```
aws_access_key_id = 'your-access-key-id'  
aws_secret_access_key = 'your-secret-access-key' 
JIRA_DOMAIN = 'your-JIRA-Domain'
API_TOKEN = 'Your-API-Token'
USER_EMAIL = 'Your-Email' 
```

## Demo video

https://infoservicesllc-my.sharepoint.com/:v:/g/personal/venkata_kaipa_infoservices_com/EaGwc6WYclpNud5WMSJN0R0Bat8VpZAaEZsNqs1LHUiDdQ?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=QaFaxh

## Reference Documents

https://infoservicesllc-my.sharepoint.com/:w:/g/personal/venkata_kaipa_infoservices_com/EZWkCh99AQREqIXTC7IB2SIBxpxwRLLS7ravNodeC4EjRA?e=BwqWem
https://infoservicesllc-my.sharepoint.com/:w:/g/personal/venkata_kaipa_infoservices_com/EYaNgemj-uxIthFYgLanNDIBqkUzWo1cLFXVvJ5gUlvasQ?e=5qCBcP