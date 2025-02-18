from flask import Flask, request, render_template, send_file, jsonify
import os
import json
import boto3
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# AWS Bedrock Client
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Jira credentials and endpoint
JIRA_DOMAIN = os.getenv('JIRA_DOMAIN')
API_TOKEN = os.getenv('API_TOKEN')
USER_EMAIL = os.getenv('USER_EMAIL')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_text_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def read_docx_file(filepath):
    doc = Document(filepath)
    return '\n'.join([p.text for p in doc.paragraphs])

def read_pdf_file(filepath):
    reader = PdfReader(filepath)
    content = ''
    for page in reader.pages:
        content += page.extract_text() if page.extract_text() else ''
    return content

def parse_test_cases(data):
    test_cases = []
    lines = data.strip().split("\n")

    def add_section(key, value):
        if value:
            if len(value) == 1:
                current_test_case[key] = value[0].strip()
            else:
                current_test_case[key] = "\n".join(value).strip()

    current_test_case = {}
    current_key = None
    current_value = []
    test_case_counter = 1

    for line in lines:
        if line.startswith("Title:"):
            if current_test_case:
                add_section(current_key, current_value)
                test_cases.append(current_test_case)

            current_test_case = {
                "Test Case": f"TC-{test_case_counter:03d}",
                "Title": line.split("Title:")[1].strip()
            }
            test_case_counter += 1
            current_key = "Title"
            current_value = []

        elif line.startswith("Type:"):
            add_section(current_key, current_value)
            current_key = "Type"
            current_value = [line.split("Type:")[1].strip()]

        elif line.startswith("Preconditions:"):
            add_section(current_key, current_value)
            current_key = "Preconditions"
            current_value = [line.split("Preconditions:")[1].strip()]

        elif line.startswith("Test Steps:"):
            add_section(current_key, current_value)
            current_key = "Test_Steps"
            current_value = [line.split("Test Steps:")[1].strip()]
            # if line.split("Test Steps:")[1].strip():
	        #     current_value = [line.split("Test Steps:")[1].strip()]

        elif line.startswith("Expected Results:"):
            add_section(current_key, current_value)
            current_key = "Expected_Results"
            current_value = [line.split("Expected Results:")[1].strip()]

        elif line.startswith("Postconditions:"):
            add_section(current_key, current_value)
            current_key = "Postconditions"
            current_value = [line.split("Postconditions:")[1].strip()]
            

        # else:
        #     current_value.append(line.strip())
        elif line and 'Test Case' not in line:
            current_value.append(line.strip())
            
    if current_test_case:
        add_section(current_key, current_value)
        test_cases.append(current_test_case)

    return test_cases

def fetch_jira_issue_description(issue_key):
    url = f'https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}'
    response = requests.get(url, auth=HTTPBasicAuth(USER_EMAIL, API_TOKEN))

    if response.status_code == 200:
        issue_data = response.json()
        description = issue_data['fields']['description']
        # description_text = ' '.join([item['text'] for item in description['content'][0]['content'] if item['type'] == 'text'])
        def extract_text(content):
            text = ""
            for item in content:
                if item['type'] == 'text':
                    text += item['text'] + "\n"
                elif 'content' in item:
                    text += extract_text(item['content'])+'\n'
            return text.strip()
 
        description_text = extract_text(description['content'])
        return description_text
    else:
        return None

@app.route('/fetch-jira', methods=['POST'])
def fetch_jira():
    issue_key = request.form.get('issue_key')
    if not issue_key:
        return jsonify({'error': 'Issue key is required'}), 400

    description = fetch_jira_issue_description(issue_key)
    if description:
        return jsonify({'description': description})
    else:
        return jsonify({'error': 'Failed to fetch Jira issue description'}), 500

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate_test_cases():
    uploaded_file = request.files.get('requirement_file')
    code_content = request.form.get('code_content', '').strip()
    selected_test_types = request.form.getlist('test_types')

    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)

        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'txt':
            code_content = read_text_file(filepath)
        elif ext == 'docx':
            code_content = read_docx_file(filepath)
        elif ext == 'pdf':
            code_content = read_pdf_file(filepath)

    if not code_content or not selected_test_types:
        return render_template('results.html', generated_tests=[])

    prompt = f"""
    Generate at least five detailed test cases for each of the functional requirements provided below. Each test case must include the following fields:
    - Title: A concise and descriptive title.
    - Preconditions: Any necessary setup or data requirements before starting the test.
    - Test Steps: A detailed, step-by-step approach for executing the test.
    - Expected Results: Clear outcomes or validations expected after performing each step.
    - Postconditions: The state of the system after test execution (if applicable).

    Functional Requirement:
    {code_content}

    Include test cases for the following types: {', '.join(selected_test_types)}.
    """

    native_request = {
        "prompt": f"Human: {prompt}\nAssistant:",
        "max_tokens_to_sample": 4096,
        "temperature": 0.5,
    }

    try:
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-instant-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(native_request)
        )
        response_text = json.loads(response['body'].read()).get('completion', '')
        generated_tests = parse_test_cases(response_text)

        if 'download_excel' in request.form:
            df = pd.DataFrame(generated_tests)
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_cases.xlsx')
            df.to_excel(excel_path, index=False)
            return send_file(excel_path, as_attachment=True)

    except Exception as e:
        print(f"Error: {e}")
        generated_tests = []

    return render_template('results.html', generated_tests=generated_tests)

if __name__ == '__main__':
    app.run(debug=True)