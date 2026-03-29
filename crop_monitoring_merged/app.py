import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import datetime
from models.demo_model import predict_from_image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# CONFIG
UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}
DB_PATH = "database.db"
DEMO_ALERTS_ONLY = True   # If True, email/SMS not attempted; change to False to enable actual services (configure below)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "very-secret-demo-key-please-change"

# initialize DB tables
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                crop_pred TEXT,
                disease_pred TEXT,
                fertilizer TEXT,
                pesticide TEXT,
                advice TEXT,
                timestamp TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                moisture REAL,
                pest_level REAL,
                prediction TEXT,
                created_at TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ---------- ROUTES ----------

@app.route("/")
def index():
    return render_template("index.html")

# Upload page (image)
@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if 'crop_image' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['crop_image']
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # demo prediction
            result = predict_from_image(filename)

            # Save to DB
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""INSERT INTO uploads (filename, crop_pred, disease_pred, fertilizer, pesticide, advice, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (filename, result["crop"], result["disease"], result["fertilizer"], result["pesticide"], result["advice"], timestamp))
            conn.commit()
            insert_id = c.lastrowid
            conn.close()

            return redirect(url_for("result", id=insert_id))
        else:
            flash("Allowed file types: png, jpg, jpeg")
            return redirect(request.url)
    return render_template("upload.html")

# Result page for single upload
@app.route("/result/<int:id>")
def result(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename, crop_pred, disease_pred, fertilizer, pesticide, advice, timestamp FROM uploads WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "Result not found", 404
    data = {
        "id": row[0],
        "filename": row[1],
        "crop": row[2],
        "disease": row[3],
        "fertilizer": row[4],
        "pesticide": row[5],
        "advice": row[6],
        "timestamp": row[7]
    }
    return render_template("result.html", data=data)

# Serve upload images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Dashboard (shows recent uploads)
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename, crop_pred, disease_pred, timestamp FROM uploads ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return render_template("dashboard.html", uploads=rows)

# Sensor analyze endpoint (form from earlier)
@app.route("/analyze_sensor", methods=["POST"])
def analyze_sensor():
    data = request.get_json()
    temp = float(data.get("temperature", 0))
    moisture = float(data.get("moisture", 0))
    pest = float(data.get("pest_level", 0))

    # simple demo prediction logic
    if pest > 70:
        pred = "High Pest Risk"
    elif moisture < 20:
        pred = "Soil Dry - Irrigation Needed"
    elif temp > 40:
        pred = "Heat Stress"
    else:
        pred = "Healthy"

    # save to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sensor_data (temperature, moisture, pest_level, prediction, created_at) VALUES (?, ?, ?, ?, ?)",
              (temp, moisture, pest, pred, now))
    conn.commit()
    conn.close()

    # alerts (demo): console print or (configure email/SMS)
    alerts = []
    if temp > 40:
        alerts.append(f"High Temperature Alert: {temp}°C")
    if moisture < 20:
        alerts.append(f"Low Soil Moisture Alert: {moisture}%")
    if pest > 70:
        alerts.append(f"Pest Outbreak Risk: {pest}%")

    # If DEMO_ALERTS_ONLY True, we just return alerts in response
    # For production, you can configure SMTP/Twilio here.
    return jsonify({"status":"success","prediction":pred,"alerts":alerts})

# Get latest sensor data for charts (last 10)
@app.route("/get_sensor_data")
def get_sensor_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT temperature, moisture, pest_level, created_at FROM sensor_data ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    rows = rows[::-1]  # oldest first
    data = {
        "temperature": [r[0] for r in rows],
        "moisture": [r[1] for r in rows],
        "pest": [r[2] for r in rows],
        "labels": [r[3] for r in rows]
    }
    return jsonify(data)

# PDF report for an upload
@app.route("/download-report/<int:id>")
def download_report(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filename, crop_pred, disease_pred, fertilizer, pesticide, advice, timestamp FROM uploads WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "No data", 404

    file_path = f"report_{id}.pdf"
    cpdf = canvas.Canvas(file_path, pagesize=letter)
    cpdf.setFont("Helvetica-Bold", 16)
    cpdf.drawString(160, 750, "Crop Analysis Report")
    cpdf.setFont("Helvetica", 12)
    y = 700
    labels = ["Filename", "Crop", "Disease", "Fertilizer", "Pesticide", "Advice", "Timestamp"]
    for label, value in zip(labels, row):
        cpdf.drawString(50, y, f"{label}: {value}")
        y -= 25
    cpdf.save()
    return send_file(file_path, as_attachment=True)

# Additional pages (basic)
@app.route("/crop-health")
def crop_health():
    return render_template("crop_health.html")

@app.route("/soil-condition")
def soil_condition():
    return render_template("soil_condition.html")

@app.route("/pest-risks")
def pest_risks():
    return render_template("pest_risks.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

if __name__ == "__main__":
    app.run(debug=True)
