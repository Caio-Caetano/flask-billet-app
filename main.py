# app.py
import re
import io
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return """
    <h1> Welcome to my API </h1>
    <p> This is the main route, to actually use call the route <strong>/bill-upload</strong> </p>
    <p> Use form-data to pass the information, I recommend to use Postman for tests </p>
    <p> Thanks! :D </p>
    """

@app.route('/bill-info', methods=['POST'])
def get_bill_info():
    files = request.files.getlist('files')

    regex_cod_bar = r'\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14}'
    regex_due_date = r'(\d{2}/\d{2}/\d{4})'
    regex_value = r'(\d{1,3}(?:\.\d{3})*,\d{2})'

    for oneFile in files:
        pdf_bytes = oneFile.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_stream)
        page_content = pdf_reader.pages[0].extract_text()

        due_date_match = re.search(regex_due_date, page_content)
        value_match = re.search(regex_value, page_content)
        cod_bar_match = re.search(regex_cod_bar, page_content)

        due_date = due_date_match.group(1) if due_date_match else None
        value = value_match.group(1) if value_match else None
        cod_bar = cod_bar_match.group().replace('\n', '') if cod_bar_match else None
        
        dic_return = {
            'due_date': due_date,
            'value': value,
            'cod_bar': cod_bar,
            'file_name':oneFile.filename
        }

    return dic_return

@app.route('/bill-upload', methods=['POST'])
def vincular_arquivos():
    residents_json = request.form.get('residents')
    residents_list = json.loads(residents_json)
    files = request.files.getlist('files')

    regex_cod_bar = r'\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14}'
    regex_due_date = r'(\d{2}/\d{2}/\d{4})'
    regex_value = r'(\d{1,3}(?:\.\d{3})*,\d{2})'

    uploadSuccessfully = []
    uploadUnsuccessfuly = residents_list

    for oneFile in files:
        pdf_bytes = oneFile.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_stream)
        page_content = pdf_reader.pages[0].extract_text()
        for user in residents_list:
            due_date_match = re.search(regex_due_date, page_content)
            value_match = re.search(regex_value, page_content)
            cod_bar_match = re.search(regex_cod_bar, page_content)
            name_user_match = re.search(user['name'], page_content)
            cpf_user_match = re.search(user['document'], page_content)

            due_date = due_date_match.group(1) if due_date_match else None
            value = value_match.group(1) if value_match else None
            cod_bar = cod_bar_match.group().replace('\n', '') if cod_bar_match else None

            if name_user_match and cpf_user_match:
                uploadSuccessfully.append({'user':user, 'cod_bar':cod_bar, 'value':value, 'due_date':due_date, 'file_name':oneFile.filename})
                uploadUnsuccessfuly.remove(user)
    
    return {'success':uploadSuccessfully, 'unsuccess':uploadUnsuccessfuly}

if __name__ == '__main__':
    app.run()
