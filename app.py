from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "attendance_secret_804"

TEACHER_PASSWORD = "804"
STUDENTS = {
    "12": "12",
    "13": "13",
    "18": "18"
}
VALID_QR_CODE = "UNIVERSITY-ATTENDANCE"
DATA_FILE = "attendance.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll = request.form.get('roll')
        password = request.form.get('password')
        if roll in STUDENTS and STUDENTS[roll] == password:
            session['student'] = roll
            return redirect('/student')
        else:
            return "Roll No ya Password galat hai! <a href='/login'>Wapas jao</a>"
    return render_template('login.html')

@app.route('/student')
def student_panel():
    if 'student' not in session:
        return redirect('/login')
    return render_template('student.html', roll=session['student'])

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'student' not in session:
        return jsonify({"status": "error", "msg": "login nahi hai"})
    roll = session['student']
    scanned_code = request.json.get('qr_code')
    if scanned_code != VALID_QR_CODE:
        return jsonify({"status": "error", "msg": "Galat QR Code! Sirf University wala QR scan karo."})
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    for d in data:
        if d['name'] == roll and d['date'] == today:
            return jsonify({"status": "error", "msg": "Aaj ki hazri pehle hi lag chuki hai!"})
    now = datetime.now()
    entry = {"name": roll, "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S")}
    data.append(entry)
    save_data(data)
    return jsonify({"status": "success", "msg": f"Hazri lag gayi! Roll {roll}"})

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd == TEACHER_PASSWORD:
            session['teacher'] = True
            return redirect('/teacher')
        else:
            return "Teacher Password galat! <a href='/teacher/login'>Wapas</a>"
    return render_template('teacher_login.html')

@app.route('/teacher')
def teacher_panel():
    if 'teacher' not in session:
        return redirect('/teacher/login')
    data = load_data()
    data.reverse()
    return render_template('teacher.html', all_data=data, total=len(data))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)