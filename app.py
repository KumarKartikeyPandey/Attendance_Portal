from flask import Flask, render_template, request, redirect, session, url_for, send_file
import os, json, uuid
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = 'data/records.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Create an empty JSON file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    user = request.form['username']
    pwd = request.form['password']
    if user == 'admin' and pwd == 'admin':
        session['user'] = user
        return redirect(url_for('home'))
    return "Invalid credentials", 403

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            if 'photo' not in request.files:
                return "No photo file found in request", 400
            file = request.files['photo']
            if file.filename == '':
                return "Empty photo file", 400

            filename = secure_filename(str(uuid.uuid4()) + '.jpg')
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            form_data['photo'] = filepath

            data = []
            if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                try:
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    data = []

            data.append(form_data)
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)

            return redirect(url_for('home'))
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return f"Error processing form: {str(e)}", 500
    return render_template('register.html')

@app.route('/download')
def download():
    if 'user' not in session:
        return redirect('/')
        
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", 'B', 14)
                self.cell(0, 10, "Space Attendance Report", ln=True, align="C")
                self.ln(10)
                self.set_font("Arial", 'B', 10)
                self.cell(30, 10, "Name", 1, 0, 'C')
                self.cell(30, 10, "Roll No", 1, 0, 'C')
                self.cell(30, 10, "Branch", 1, 0, 'C')
                self.cell(30, 10, "Section", 1, 0, 'C')
                self.cell(50, 10, "Email", 1, 0, 'C')
                self.cell(30, 10, "Photo", 1, 1, 'C')

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', align='C')

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        for entry in data:
            pdf.cell(30, 30, entry.get('name', ''), 1, 0, 'C')
            pdf.cell(30, 30, entry.get('roll', ''), 1, 0, 'C')
            pdf.cell(30, 30, entry.get('branch', ''), 1, 0, 'C')
            pdf.cell(30, 30, entry.get('section', ''), 1, 0, 'C')
            pdf.cell(50, 30, entry.get('email', ''), 1, 0, 'C')

            photo_path = entry.get('photo', '')
            if os.path.exists(photo_path):
                x = pdf.get_x()
                y = pdf.get_y()
                pdf.cell(30, 30, '', 1, 0)  # empty cell with border for the image
                try:
                    pdf.image(photo_path, x=x + 1, y=y + 1, w=28, h=28)
                except Exception as e:
                    print(f"Error adding image to PDF: {str(e)}")
            else:
                pdf.cell(30, 30, 'N/A', 1, 0, 'C')

            pdf.ln(30)

        pdf_path = 'output/report.pdf'
        pdf.output(pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name="attendance_report.pdf")
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"Error generating PDF: {str(e)}", 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)