from flask import Flask, render_template, request
import numpy as np
import pickle
import smtplib
import pandas as pd
from fpdf import FPDF
import uuid
import os



# Load the trained model
model = pickle.load(open('model.pkl', 'rb'))

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/dti-calculator", methods=['GET', 'POST'])
def dti_calculator():
    if request.method == 'POST':
        try:
            income = float(request.form['income'])
            total_debt = float(request.form['total_debt'])

            if income <= 0:
                return render_template("dti_calculator.html", error="Income must be greater than 0.")

            dti_ratio = (total_debt / income) * 100
            return render_template("dti_calculator.html", dti_ratio=round(dti_ratio, 2))
        except Exception as e:
            return render_template("dti_calculator.html", error=f"Error: {str(e)}")
    return render_template("dti_calculator.html")





@app.route("/about")
def about():
    return render_template("about.html")

from flask import Flask, render_template, request, send_file
import numpy as np
import pickle
import os
from fpdf import FPDF
import uuid

# ... your existing imports and model loading ...

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get inputs
        age = int(request.form['age'])
        ed = int(request.form['ed'])
        employ = int(request.form['employ'])
        address = int(request.form['address'])
        income = float(request.form['income'])
        debtinc = float(request.form['debtinc'])
        creddebt = float(request.form['creddebt'])
        othdebt = float(request.form['othdebt'])

        features = np.array([[age, ed, employ, address, income, debtinc, creddebt, othdebt]])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]

        if prediction == 1:
            result = "The customer might not be able to repay the loan."
        else:
            result = "The customer will likely to repay the loan."

        # Example recommendations (can customize)
        recommendations = []
        if creddebt > 0.5 * income:
            recommendations.append("Consider reducing credit card debt.")
        if debtinc > 0.4:
            recommendations.append("Income-to-debt ratio is high. Try lowering expenses.")

        # Generate a unique filename for the PDF
        pdf_filename = f"loan_prediction_{uuid.uuid4().hex}.pdf"
        pdf_filepath = os.path.join("static", "pdf_reports", pdf_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(pdf_filepath), exist_ok=True)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Loan Default Prediction Report", ln=True, align='C')
        pdf.ln(10)

        pdf.cell(0, 10, "Customer Inputs:", ln=True)
        pdf.cell(0, 8, f"Age: {age}", ln=True)
        pdf.cell(0, 8, f"Education Level: {ed}", ln=True)
        pdf.cell(0, 8, f"Employment Duration: {employ}", ln=True)
        pdf.cell(0, 8, f"Address Duration: {address}", ln=True)
        pdf.cell(0, 8, f"Income: {income}", ln=True)
        pdf.cell(0, 8, f"Debt to Income Ratio: {debtinc}", ln=True)
        pdf.cell(0, 8, f"Credit Card Debt: {creddebt}", ln=True)
        pdf.cell(0, 8, f"Other Debt: {othdebt}", ln=True)

        pdf.ln(10)
        pdf.cell(0, 10, "Prediction Result:", ln=True)
        pdf.multi_cell(0, 10, result)

        pdf.ln(10)
        pdf.cell(0, 10, f"Probability of Default: {round(probabilities[1] * 100, 2)}%", ln=True)
        pdf.cell(0, 10, f"Probability of No Default: {round(probabilities[0] * 100, 2)}%", ln=True)

        if recommendations:
            pdf.ln(10)
            pdf.cell(0, 10, "Recommendations:", ln=True)
            for rec in recommendations:
                pdf.cell(0, 8, f"- {rec}", ln=True)

        pdf.output(pdf_filepath)

        return render_template('result.html',
                               prediction_text=result,
                               prob_default=round(probabilities[1] * 100, 2),
                               prob_no_default=round(probabilities[0] * 100, 2),
                               recommendations=recommendations,
                               pdf_file=pdf_filename)

    except Exception as e:
        return render_template('result.html', prediction_text=f"Error: {str(e)}")


    
@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        subject = 'Contact Form Submission from ' + name
        body = 'Name: ' + name + '\nEmail: ' + email + '\nMessage: ' + message

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('markdummy4242@gmail.com', 'lhvm mafu pziv aqfn')
        server.sendmail('markdummy4242@gmail.com', 'ganeshusharma301@gmail.com', subject + '\n\n' + body)
        server.quit()

        return render_template('thank_you.html')
    except Exception as e:
        return f"Error sending email: {e}"


if __name__ == '__main__':
    app.run(debug=True,port=5000)
