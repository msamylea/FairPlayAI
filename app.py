from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import io
from xhtml2pdf import pisa
from reports.create_policy_report import create_policy_report_pdf
from process_input import process_input
import requests
import time
from utilities.constants import us_states, reproductive_rights_and_health, economic_equality, safety_and_security
from data import data_retrieval
from ai.analysis import analyze_policy
import pandas as pd
import json
from plots.create_plots import create_plots
from data.civic_data import get_representatives
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

topics = {
    "Reproductive Rights": reproductive_rights_and_health,
    "Economic Equality": economic_equality,
    "Safety and Security": safety_and_security
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/policy-analysis', methods=['GET'])
def policy_analysis():
    return render_template('policy_analysis.html')

@app.route('/find-policies', methods=['GET'])
def find_policies():
    return render_template('find_policies.html')

@app.route('/contact-reps')
def contact_reps():
    return render_template('contact_reps.html')

@app.route('/policy-search', methods=['GET', 'POST'])
def policy_search_page():
    return render_template('policy_search.html', states=us_states, topics=topics)

@app.route('/get_bills', methods=['POST'])
def policy_search():
    selected_topic = request.form.get('topic')
    selected_state = request.form.get('state')
    bills = data_retrieval.get_bills(selected_topic, selected_state)
    print(bills)
    return jsonify(bills)

@app.route('/get_bill_pdf', methods=['POST'])
def get_bill_pdf_route():
    bill_id = request.form.get('bill_id')
    pdf_file = data_retrieval.get_bill_pdf(bill_id)
    return send_file(pdf_file, as_attachment=False)


@app.route('/proxy/representatives')
def proxy_representatives():
    address = request.args.get('location')
    if not address:
        return jsonify({"error": "Address not provided"}), 400
    try:
        response = get_representatives(address)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    text = request.form.get('text')

    if file and text:
        return jsonify({"error": "Please provide either a file or text input, not both."}), 400

    try:
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            policy_content = process_input(file_path)
            logger.info(f"Processed file input: {filename}")
        elif text:
            policy_content = text
            logger.info("Received text input")
        else:
            return jsonify({"error": "No valid input provided"}), 400

        logger.info(f"Policy content (first 500 chars): {policy_content[:500]}...")

        policy_report = analyze_policy(policy_content)
        plot_html = create_plots(policy_report)
        logger.info(f"Policy report generated: {str(policy_report)[:500]}...")

        pdf_content = create_policy_report_pdf(policy_report, plot_html)
        logger.info("PDF content generated")
        
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Temporary file removed: {file_path}")

        # Save the PDF temporarily
        temp_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_report.pdf')
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_content)
        logger.info(f"Temporary PDF saved: {temp_pdf_path}")
        
        time.sleep(0.5)
        
        return jsonify({
            "success": True, 
            "pdf_url": "/get_pdf",
        })
    
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"An error occurred during analysis: {str(e)}"}), 500
    
@app.route('/get_pdf')
def get_pdf():
    temp_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_report.pdf')
    return send_file(temp_pdf_path, mimetype='application/pdf')


@app.route('/statistics', methods=['GET'])
def statistics():
    with open("data/2024_cleaned.csv") as f:
        data = pd.read_csv(f)
    
    # Filter data for female victims only
    women_victims = data[data['Victim Sex'] == 'Female']
    
    # Calculate statistics
    total_incidents = len(women_victims)
    women_victims_percentage = (len(women_victims) / len(data)) * 100
    
    crime_types = women_victims['Type'].value_counts().to_dict()
    offender_relationships = women_victims['Offender Relationship'].value_counts().to_dict()
    weapons_used = women_victims['Weapon Type'].value_counts().to_dict()
    injury_types = women_victims['Injury Type'].value_counts().to_dict()
    incidents_by_location = women_victims['Location'].value_counts().to_dict()
    offender_sex_dist = (women_victims['Offender Sex'].value_counts(normalize=True) * 100).to_dict()

    # Calculate percentage of incidents resulting in injury
    injury_percentage = (women_victims['Injury Type'] != 'No injury').mean() * 100

    # Calculate percentage of domestic violence
    domestic_violence = women_victims['Offender Relationship'].isin(['Intimate Partner', 'Other Relative'])
    domestic_violence_percentage = domestic_violence.mean() * 100

    # Prepare data for the template
    stats = {
        'total_incidents': total_incidents,
        'women_victims_percentage': women_victims_percentage,
        'crime_types': crime_types,
        'offender_relationships': offender_relationships,
        'weapons_used': weapons_used,
        'injury_types': injury_types,
        'incidents_by_location': incidents_by_location,
        'offender_sex_dist': offender_sex_dist,
        'injury_percentage': injury_percentage,
        'domestic_violence_percentage': domestic_violence_percentage
    }

    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
