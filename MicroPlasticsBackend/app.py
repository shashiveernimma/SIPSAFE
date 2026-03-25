from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import os
import gc

# ML prediction
from ml_model.predict_model import predict_microplastic

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 🔥 LIMIT FILE SIZE (VERY IMPORTANT)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

SAFE_LIMIT = 30

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===============================
# IMAGE ANALYSIS (OPTIMIZED)
# ===============================
def analyze_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Image not loaded")

    # 🔥 RESIZE (BIGGEST FIX)
    image = cv2.resize(image, (512, 512))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cv2.imwrite("static/gray_image.jpg", gray)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    dilated = cv2.dilate(opening, kernel, iterations=1)

    contours, _ = cv2.findContours(
        dilated,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    count = 0

    for contour in contours:
        area = cv2.contourArea(contour)

        # 🔥 INCREASE THRESHOLD (LESS PROCESSING)
        if area > 10:
            count += 1
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 1)

    cv2.imwrite("static/detected_particles.jpg", image)

    # 🔥 FREE MEMORY
    del gray, blur, thresh, opening, dilated, contours
    gc.collect()

    return count


# ===============================
# WATER SAFETY
# ===============================
def check_safety(count):
    if count <= 20:
        return "SAFE to drink"
    elif count <= 50:
        return "Moderate contamination"
    else:
        return "NOT SAFE to drink"


# ===============================
# HOME PAGE
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# ANALYZE ROUTE (SAFE)
# ===============================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # 🔥 ANALYSIS
        count = analyze_image(filepath)

        status = check_safety(count)

        # 🔥 ML (wrap in try to avoid crash)
        try:
            prediction = predict_microplastic(filepath)
        except Exception as e:
            print("ML Error:", e)
            prediction = "ML prediction failed"

        return jsonify({
            "microplastic_count": count,
            "water_status": status,
            "ml_prediction": prediction,
            "grayscale_image": "/static/gray_image.jpg",
            "detected_particles": "/static/detected_particles.jpg"
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Backend processing failed"}), 500


# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
