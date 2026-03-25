from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import os

# ML prediction
from ml_model.predict_model import predict_microplastic

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

SAFE_LIMIT = 30

# create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# IMAGE ANALYSIS
# ===============================
def analyze_image(image_path):

    image = cv2.imread(image_path)

    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # save grayscale image
    cv2.imwrite("static/gray_image.jpg", gray)

    # remove noise
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # adaptive threshold (better for microscope lighting)
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    # remove tiny noise using morphology
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # slightly enlarge particles
    dilated = cv2.dilate(opening, kernel, iterations=1)

    # detect contours
    contours, _ = cv2.findContours(
        dilated,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    count = 0

    for contour in contours:

        area = cv2.contourArea(contour)

        # detect small particles
        if area > 10:

            count += 1

            # draw contour on detected particle
            cv2.drawContours(image, [contour], -1, (0,255,0), 1)

    # save detected particles image
    cv2.imwrite("static/detected_particles.jpg", image)

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
# ANALYZE ROUTE
# ===============================
@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"})

    file = request.files["image"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

    file.save(filepath)

    # particle detection
    count = analyze_image(filepath)

    # safety classification
    status = check_safety(count)

    # ML prediction
    prediction = predict_microplastic(filepath)

    return jsonify({
        "microplastic_count": count,
        "water_status": status,
        "ml_prediction": prediction,
        "grayscale_image": "/static/gray_image.jpg",
        "detected_particles": "/static/detected_particles.jpg"
    })


# ===============================
# RUN SERVER
# ======================
# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
