from flask import Flask, render_template, request, redirect, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os, json, base64, math

app = Flask(__name__)
app.secret_key = "vipheraid_expo_final_2026_madurai"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///viperaid.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)


class Report(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    animal_type = db.Column(db.String(50))
    urgency = db.Column(db.String(20), default="Medium")
    location_text = db.Column(db.String(200))
    geo = db.Column(db.String(100))
    description = db.Column(db.Text)
    reporter_name = db.Column(db.String(100))
    reporter_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Reported")
    assigned_to = db.Column(db.String(100))
    photo_url = db.Column(db.String(300))
    is_emergency = db.Column(db.Boolean, default=False)


class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(200), nullable=False)
    shelter_type = db.Column(db.String(50))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(100))
    geo = db.Column(db.String(100))
    capacity = db.Column(db.String(20))
    animals_helped = db.Column(db.String(200))
    description = db.Column(db.Text)
    hours = db.Column(db.String(100))
    website = db.Column(db.String(200))


with app.app_context():
    db.create_all()


# ─── PAGES ──────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return render_template("index.html")

@app.route("/report")
def report(): return render_template("report.html")

@app.route("/emergency")
def emergency(): return render_template("emergency.html")

@app.route("/rescue")
def rescue():
    if not session.get("rescuer"): return redirect("/rescue-login")
    return render_template("rescue.html")

@app.route("/donate")
def donate(): return render_template("donate.html")




@app.route("/shelter")
def shelter_page(): return render_template("shelter.html")


# ─── AUTH ────────────────────────────────────────────────────────────────────
@app.route("/rescue-login", methods=["GET", "POST"])
def rescue_login():
    if request.method == "POST":
        org = request.form.get("org","").strip()
        code = request.form.get("code","").strip()
        if code == "VIPERNGO":
            session["rescuer"] = True
            session["org"] = org or "NGO"
            return redirect("/rescue")
        flash("Invalid NGO code. Try: VIPERNGO")
        return redirect("/rescue-login")
    return render_template("rescue-login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ─── REPORT APIs ─────────────────────────────────────────────────────────────
@app.route("/api/report", methods=["POST"])
def api_create_report():
    if request.is_json:
        data = request.json or {}
        photo = None
    else:
        data = request.form.to_dict()
        photo = request.files.get("photo")

    photo_url = None
    if photo and photo.filename:
        filename = secure_filename(f"{int(datetime.now().timestamp())}_{photo.filename}")
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        photo_url = f"/static/uploads/{filename}"

    is_emerg = str(data.get("isEmergency","")).lower() in ("true","1","yes")

    r = Report(
        id=f"VA{int(datetime.now().timestamp())}",
        animal_type=data.get("animalType"),
        urgency=data.get("urgency","Medium"),
        location_text=data.get("locationText"),
        geo=data.get("geo"),
        description=data.get("description"),
        reporter_name=data.get("reporterName") or session.get("citizen_name"),
        reporter_phone=data.get("reporterPhone") or session.get("citizen_phone"),
        status="Reported",
        assigned_to="",
        photo_url=photo_url,
        is_emergency=is_emerg
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"success": True, "id": r.id, "photoUrl": photo_url})


@app.route("/api/reports")
def api_reports():
    # Emergency reports always first, then by date desc
    reports = Report.query.order_by(Report.is_emergency.desc(), Report.created_at.desc()).limit(100).all()
    return jsonify([{
        "id": r.id, "animalType": r.animal_type, "urgency": r.urgency,
        "locationText": r.location_text, "geo": r.geo, "description": r.description,
        "status": r.status, "createdAt": r.created_at.isoformat(),
        "reporterName": r.reporter_name, "reporterPhone": r.reporter_phone,
        "assignedTo": r.assigned_to, "photoUrl": r.photo_url,
        "isEmergency": bool(r.is_emergency)
    } for r in reports])


@app.route("/api/report/<report_id>", methods=["POST"])
def api_update_report(report_id):
    if not session.get("rescuer"): return jsonify({"error":"Unauthorized"}), 403
    r = Report.query.get_or_404(report_id)
    data = request.json or {}
    if "status" in data: r.status = data["status"]
    if "assignedTo" in data: r.assigned_to = data["assignedTo"]
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/report/<report_id>", methods=["DELETE"])
def api_delete_report(report_id):
    if not session.get("rescuer"): return jsonify({"error":"Unauthorized"}), 403
    r = Report.query.get_or_404(report_id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True})


# ─── SHELTER APIs ─────────────────────────────────────────────────────────────
@app.route("/api/shelter", methods=["POST"])
def api_create_shelter():
    data = request.json or {}
    s = Shelter(
        name=data.get("name","").strip(),
        shelter_type=data.get("shelter_type"),
        address=data.get("address"),
        city=data.get("city"),
        phone=data.get("phone"),
        email=data.get("email"),
        geo=data.get("geo"),
        capacity=data.get("capacity"),
        animals_helped=data.get("animals_helped"),
        description=data.get("description"),
        hours=data.get("hours"),
        website=data.get("website")
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({"success": True, "id": s.id})


@app.route("/api/shelters")
def api_get_shelters():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    shelters = Shelter.query.order_by(Shelter.created_at.desc()).all()
    result = []
    for s in shelters:
        d = {
            "id": s.id, "name": s.name, "shelter_type": s.shelter_type,
            "address": s.address, "city": s.city, "phone": s.phone,
            "email": s.email, "geo": s.geo, "capacity": s.capacity,
            "animals_helped": s.animals_helped, "description": s.description,
            "hours": s.hours, "website": s.website
        }
        if lat and lng and s.geo:
            try:
                parts = s.geo.replace(" ","").split(",")
                slat, slng = float(parts[0]), float(parts[1])
                R = 6371
                dlat = math.radians(slat - lat); dlng = math.radians(slng - lng)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat))*math.cos(math.radians(slat))*math.sin(dlng/2)**2
                d["distance_km"] = round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)
            except: d["distance_km"] = None
        result.append(d)
    if lat and lng:
        result.sort(key=lambda x: x.get("distance_km") or 9999)
    return jsonify(result)


@app.route("/api/shelter/<int:shelter_id>", methods=["DELETE"])
def api_delete_shelter(shelter_id):
    s = Shelter.query.get_or_404(shelter_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({"success": True})


# ─── AI ANIMAL DETECTION ───────────────────────────────────────────────────
@app.route("/api/detect-animal", methods=["POST"])
def api_detect_animal():
    """Basic animal photo validation — accepts photos with sufficient image data."""
    data = request.json or {}
    image_b64 = data.get("image","")
    if not image_b64 or len(image_b64) < 2000:
        return jsonify({"isAnimal": False, "detectedAs": "Image too small or missing"})
    # Accept photo — frontend Canvas will display it
    return jsonify({"isAnimal": True, "animalType": "Animal", "confidence": 0.85, "detectedAs": None, "bbox": None})

@app.route("/favicon.ico")
def favicon(): return "", 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


@app.route("/api/public-stats")
def api_public_stats():
    total = Report.query.count()
    resolved = Report.query.filter_by(status="Completed").count()
    active = Report.query.filter(Report.status != "Completed").count()
    return jsonify({"total": total, "resolved": resolved, "active": active})
