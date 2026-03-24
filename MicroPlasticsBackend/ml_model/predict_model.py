import cv2
import joblib
import numpy as np

model = joblib.load("ml_model/microplastic_model.pkl")

def predict_microplastic(image_path):

    img = cv2.imread(image_path)

    img = cv2.resize(img,(100,100))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    features = gray.flatten().reshape(1,-1)

    prediction = model.predict(features)

    if prediction == 1:
        return "Microplastics detected"
    else:
        return "Water appears clean"